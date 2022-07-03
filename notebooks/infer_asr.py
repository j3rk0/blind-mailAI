import os.path

import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, Wav2Vec2ProcessorWithLM
from utils.lib import record_audio

# %% INITIALIZE MODEL

use_lm = os.path.isdir('models/wav2vec2LM')
if use_lm:
    model = Wav2Vec2ForCTC.from_pretrained('models/wav2vec2LM')
    processor = Wav2Vec2ProcessorWithLM.from_pretrained('models/wav2vec2LM')
else:
    model = Wav2Vec2ForCTC.from_pretrained('models/wav2vec2')
    processor = Wav2Vec2Processor.from_pretrained('models/wav2vec2')
    use_lm = False

# %% LOAD AUDIO

# waveform, sr = librosa.load(f'data/DATASET_NLP/mp3/B_3_1/B_3_1_2.mp3', sr=16000) # load from file
waveform = record_audio()  # record live

# %% PROCESS INPUT AND INFER

inputs = processor(waveform, sampling_rate=16000, return_tensor='pt', padding=True)
input_values = torch.FloatTensor(inputs.input_values)
attention_mask = torch.LongTensor(inputs.attention_mask)

with torch.no_grad():
    logits = model(input_values, attention_mask).logits

# %% FORMAT RESULT

if use_lm:
    pred = processor.batch_decode(logits.numpy()).text[0].lower()
else:
    pred = processor.decode(torch.argmax(logits, dim=-1)[0])

print(f'la tua frase è: {pred}')
