import random
from typing import Dict, List, Union
import sounddevice as sd
import librosa
import pandas as pd
import torch
from datasets import load_from_disk, Dataset
import os
import numpy as np


class DataCollatorCTCWithPadding:
    """
    Data collator that will dynamically pad the inputs received.
    Args:
        processor (:class:`~transformers.Wav2Vec2Processor`)
            The processor used for proccessing the data.
        padding (:obj:`bool`, :obj:`str` or :class:`~transformers.tokenization_utils_base.PaddingStrategy`, `optional`, defaults to :obj:`True`):
            Select a strategy to pad the returned sequences (according to the model's padding side and padding index)
            among:
            * :obj:`True` or :obj:`'longest'`: Pad to the longest sequence in the batch (or no padding if only a single
              sequence if provided).
            * :obj:`'max_length'`: Pad to a maximum length specified with the argument :obj:`max_length` or to the
              maximum acceptable input length for the model if that argument is not provided.
            * :obj:`False` or :obj:`'do_not_pad'` (default): No padding (i.e., can output a batch with sequences of
              different lengths).
    """

    def __init__(self, processor, padding=True):
        self.processor = processor
        self.padding = padding

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        # split inputs and labels since they have to be of different lenghts and need
        # different padding methods
        input_features = [{"input_values": feature["input_values"]} for feature in features]
        label_features = [{"input_ids": feature["labels"]} for feature in features]

        batch = self.processor.pad(
            input_features,
            padding=self.padding,
            return_tensors="pt",
        )
        with self.processor.as_target_processor():
            labels_batch = self.processor.pad(
                label_features,
                padding=self.padding,
                return_tensors="pt",
            )

        # replace padding with -100 to ignore loss correctly
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)

        batch["labels"] = labels

        return batch


def _train_validate_test_split(df, train_percent=.6, validate_percent=.2, seed=None):
    np.random.seed(seed)
    perm = np.random.permutation(df.index)
    m = len(df.index)
    train_end = int(train_percent * m)
    validate_end = int(validate_percent * m) + train_end
    train = df.iloc[perm[:train_end]]
    validate = df.iloc[perm[train_end:validate_end]]
    test = df.iloc[perm[validate_end:]]
    return train, validate, test


def load_dataset(processor=None, refresh=False):
    # check if processed data already exists
    if os.path.isdir('data/hfdata/train.hf') and os.path.isdir('data/hfdata/eval.hf') and \
            os.path.isdir('data/hfdata/test.hf') and not refresh:
        return load_from_disk('data/hfdata/train.hf'), load_from_disk('data/hfdata/eval.hf'), \
               load_from_disk('data/hfdata/test.hf')
    elif processor is not None:
        ds = pd.read_csv(f"data/dataset.csv", index_col=0)

        folds = ['train'] * int(.6 * ds.shape[0]) + ['test'] * int(.2 * ds.shape[0]) + \
                ['valid'] * int(.2 * ds.shape[0])

        random.shuffle(folds)

        train_data = {'input_values': [], 'labels': [], 'input_length': []}
        eval_data = {'input_values': [], 'labels': [], 'input_length': []}
        test_data = {'input_values': [], 'labels': [], 'input_length': []}

        for i in range(ds.shape[0]):

            ftext = ds.iloc[i, 0]

            waveform, sr = librosa.load(f'data/audio/{i}.mp3', sr=16000)
            waveform = processor(waveform, sampling_rate=16000).input_values[0]

            to_expand = eval_data
            if folds[i] == 'train':
                to_expand = train_data
            elif folds[i] == 'test':
                to_expand = test_data

            to_expand['input_values'].append(waveform)
            to_expand['input_length'].append(len(waveform))
            with processor.as_target_processor():
                to_expand['labels'].append(processor(ftext.lower()).input_ids)

        train = Dataset.from_dict(train_data)
        valid = Dataset.from_dict(eval_data)
        test = Dataset.from_dict(test_data)
        train.save_to_disk('data/hfdata/train.hf')
        valid.save_to_disk('data/hfdata/eval.hf')
        test.save_to_disk('data/hfdata/test.hf')
        return train, valid, test


def record_audio(time=5, sr=16000):
    print('start recording')
    myrecording = sd.rec(int(time * sr), samplerate=sr, channels=1)
    sd.wait()
    print('stop recording')
    return myrecording.T[0]


def merge_tokens(accumuled_tokens):
    n_elem = len(accumuled_tokens)
    if n_elem == 1:
        return accumuled_tokens[0]
    t_len = np.zeros(n_elem)
    t_lab = []
    t_sco = np.zeros(n_elem)
    t_text = []
    for i in range(n_elem):
        t_text.append(accumuled_tokens[i]['text'].replace('##', ''))
        t_len[i] = len(accumuled_tokens[i]['text'].replace('##', ''))
        t_sco[i] = accumuled_tokens[i]['score']
        t_lab.append(accumuled_tokens[i]['label'])

    ret_score = t_sco.max()
    weights = (t_len * t_sco) / (t_len.sum() * t_sco.sum())
    scores = {}
    max_score = 0
    best_label = None
    for i in range(n_elem):

        if t_lab[i] not in scores.keys():
            scores[t_lab[i]] = weights[i]
        else:
            scores[t_lab[i]] += weights[i]

        if scores[t_lab[i]] >= max_score:
            max_score = scores[t_lab[i]]
            best_label = t_lab[i]
    return {'text': ''.join(t_text), 'score': ret_score, 'label': best_label}


# %%
def format_tokenclf_result(res):
    token_labels = {'LABEL_0': 'O',
                    'LABEL_1': 'B-PER',
                    'LABEL_2': 'I-PER',
                    'LABEL_3': 'B-OBJ',
                    'LABEL_4': 'I-OBJ',
                    'LABEL_5': 'B-DATE',
                    'LABEL_6': 'I-DATE'}
    # unpack tokens
    temp = []
    for r in res:
        tokens = r['word'].split(' ')
        for token in tokens:
            temp.append({'text': token,
                         'label': token_labels[r['entity_group']],
                         'score': r['score']})

    # merge tokens
    ret = []
    accumuled_tokens = []
    for r in temp:
        if r['text'][0:2] == "##" or len(accumuled_tokens) == 0:
            accumuled_tokens.append(r)
        elif len(accumuled_tokens) > 0:
            ret.append(merge_tokens(accumuled_tokens))
            accumuled_tokens = [r]
    ret.append(merge_tokens(accumuled_tokens))
    ret.reverse()
    curr = None
    res = []
    to_append = None
    # merge slots
    while len(ret) > 0:
        curr = ret.pop()
        if to_append is None:
            to_append = curr
        elif to_append['label'] == curr['label'] or \
            to_append['label'][-3:] == curr['label'][-3:]:
            to_append['text'] = f"{to_append['text']} {curr['text']}"
        elif to_append is not None:
            res.append(to_append)
            to_append = curr

    res.append(to_append)
    return res


def format_asr_result(res):
    return res['text'].lower()


def format_seqclf_result(res):
    return {"LABEL_0": "send_email",
            "LABEL_1": "list_email",
            "LABEL_2": "read_email",
            "LABEL_3": "delete_email",
            "LABEL_4": "reply_email",
            "LABEL_5": "forward_email",
            "LABEL_6": "close_email"}[res[0]['label']]
