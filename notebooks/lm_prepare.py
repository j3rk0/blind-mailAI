import os, sys
os.environ['KENLM_ROOT'] = f"{os.getcwd()}/lib/lm/kenlm"
os.environ['KENLM_ROOT_DIR'] = f"{os.getcwd()}/lib/lm/kenlm"
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from lib.utils import record_audio
from pyctcdecode import build_ctcdecoder


# %%

repo_name = 'models/wav2vec2'
model = Wav2Vec2ForCTC.from_pretrained(repo_name)
processor = Wav2Vec2Processor.from_pretrained(repo_name)

# %% BUILD LM DECODER

vocab_dict = processor.tokenizer.get_vocab()
sorted_vocab_dict = {k.lower(): v for k, v in sorted(vocab_dict.items(), key=lambda item: item[1])}

decoder = build_ctcdecoder(
    labels=list(sorted_vocab_dict.keys()),
    kenlm_model_path="models/lm/lm.fixed.arpa",
)

# %% INITIALIZE MODEL


# %% LOAD AUDIO

# waveform, sr = librosa.load(f'data/DATASET_NLP/mp3/B_3_1/B_3_1_2.mp3', sr=16000) # load from file
waveform = record_audio()  # record live

# %% PROCESS INPUT AND INFER

inputs = processor(waveform, sampling_rate=16000, return_tensor='pt', padding=True)
input_values = torch.FloatTensor(inputs.input_values)
attention_mask = torch.LongTensor(inputs.attention_mask)
logits = model(input_values, attention_mask).logits

# %% FORMAT RESULT

pred_ids = torch.argmax(logits, dim=-1)[0]
pred = processor.decode(pred_ids)
print(f'la tua frase è: {pred}')
