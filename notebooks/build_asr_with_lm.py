import os, sys
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, Wav2Vec2ProcessorWithLM
from utils.lib import record_audio
import librosa
from pyctcdecode import build_ctcdecoder

# %% INITIALIZE MODEL

repo_name = 'models/wav2vec2'
model = Wav2Vec2ForCTC.from_pretrained(repo_name)
processor = Wav2Vec2Processor.from_pretrained(repo_name)

# %% BUILD LM PROCESSOR

vocab_dict = processor.tokenizer.get_vocab()
sorted_vocab_dict = {k: v for k, v in sorted(vocab_dict.items(), key=lambda item: item[1])}

decoder = build_ctcdecoder(
    labels=list(sorted_vocab_dict.keys()),
    kenlm_model_path="models/lm/lm.arpa",
)

processor_with_lm = Wav2Vec2ProcessorWithLM(feature_extractor=processor.feature_extractor,
                                            tokenizer=processor.tokenizer,
                                            decoder=decoder)


# %% MODEL TESTING

waveform, sr = librosa.load(f'data/DATASET_NLP/mp3/B_3_1/B_3_1_2.mp3', sr=16000) # load from file

inputs = processor_with_lm(waveform, sampling_rate=16000, return_tensor='pt', padding=True)
input_values = torch.FloatTensor(inputs.input_values)
attention_mask = torch.LongTensor(inputs.attention_mask)

with torch.no_grad():
    logits = model(input_values, attention_mask).logits

pred_with_lm = processor_with_lm.batch_decode(logits.numpy()).text[0].lower()
pred = processor.batch_decode(torch.argmax(logits,dim=-1))[0].lower()


print(f'prediction with lm: {pred_with_lm}\n'
      f'prediction witouth lm: {pred}')

#%% SAVE MODEL

model.save_pretrained("models/wav2vec2LM")
processor_with_lm.save_pretrained('models/wav2vec2LM')



