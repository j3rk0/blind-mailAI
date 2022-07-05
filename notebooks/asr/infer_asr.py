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

waveform = record_audio()  # record live

# %%

from transformers import pipeline

asr_pipe = pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
                    feature_extractor=processor.feature_extractor,
                    decoder=processor.decoder)

print(asr_pipe(waveform))
