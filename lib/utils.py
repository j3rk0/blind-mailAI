from typing import Dict, List, Union
import sounddevice as sd
import librosa
import pandas as pd
import torch
from datasets import load_from_disk, Dataset
import os


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


def load_dataset(source_path, processor, refresh=False):
    # check if processed data already exists
    if os.path.isdir('data/hfdata/train.hf') and os.path.isdir('data/hfdata/eval.hf') and not refresh:
        return load_from_disk('data/hfdata/train.hf'), load_from_disk('data/hfdata/eval.hf')
    else:
        ds = pd.read_csv(source_path)

        train_data = {'input_values': [], 'labels': [], 'input_length': []}
        eval_data = {'input_values': [], 'labels': [], 'input_length': []}
        for i in range(ds.shape[0]):

            fname, ftext = ds.iloc[i, 0:2]

            for j in range(1, 8):
                to_expand = eval_data
                if j <= 5:  # to Train 1-5
                    to_expand = train_data

                waveform, sr = librosa.load(f'data/DATASET_NLP/mp3/{fname}/{fname}_{j}.mp3', sr=16000)
                waveform = processor(waveform, sampling_rate=16000).input_values[0]

                with processor.as_target_processor():
                    to_expand['labels'].append(processor(ftext.lower()).input_ids)

                to_expand['input_values'].append(waveform)
                to_expand['input_length'].append(len(waveform))

        train = Dataset.from_dict(train_data)
        valid = Dataset.from_dict(eval_data)
        train.save_to_disk('data/hfdata/train.hf')
        valid.save_to_disk('data/hfdata/eval.hf')
        return train, valid


def record_audio(time=5, sr=16000):
    print('start recording')
    myrecording = sd.rec(int(time * sr), samplerate=sr, channels=1)
    sd.wait()
    print('stop recording')
    return myrecording.T[0]
