import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from utils import record_audio

#%% INITIALIZE MODEL

repo_name = 'models/wav2vec2'
model = Wav2Vec2ForCTC.from_pretrained(repo_name)
processor = Wav2Vec2Processor.from_pretrained(repo_name)

# %% LOAD AUDIO

#waveform, sr = librosa.load(f'data/DATASET_NLP/mp3/B_3_1/B_3_1_2.mp3', sr=16000) # load from file
waveform = record_audio()  # record live


#%% PROCESS INPUT AND INFER

inputs = processor(waveform, sampling_rate=16000, return_tensor='pt', padding=True)
input_values = torch.FloatTensor(inputs.input_values)
attention_mask = torch.LongTensor(inputs.attention_mask)
logits = model(input_values, attention_mask).logits

# %% FORMAT RESULT

pred_ids = torch.argmax(logits, dim=-1)[0]
pred = processor.decode(pred_ids)
print(f'la tua frase è: {pred}')
