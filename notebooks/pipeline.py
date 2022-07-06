from transformers import pipeline
from transformers import Wav2Vec2ForCTC, Wav2Vec2ProcessorWithLM
from transformers import AutoModelForTokenClassification, AutoModelForSequenceClassification, AutoTokenizer
from utils.lib import *

asr_processor = Wav2Vec2ProcessorWithLM.from_pretrained('models/wav2vec2LM')
tokenizer = AutoTokenizer.from_pretrained('models/berttokenizer')

asr_pipe = pipeline('automatic-speech-recognition', model=Wav2Vec2ForCTC.from_pretrained('models/wav2vec2LM'),
                    tokenizer=asr_processor.tokenizer,
                    feature_extractor=asr_processor.feature_extractor,
                    decoder=asr_processor.decoder)

# %%

token_labels = {'LABEL_0': 'O',
                'LABEL_1': 'B-PER',
                'LABEL_2': 'I-PER',
                'LABEL_3': 'B-OBJ',
                'LABEL_4': 'I-OBJ',
                'LABEL_5': 'B-DATE',
                'LABEL_6': 'I-DATE'}

token_pipe = pipeline(
    "token-classification", model=AutoModelForTokenClassification.from_pretrained('models/bert4token'),
    tokenizer=tokenizer, aggregation_strategy="simple")

# %%


intent_pipe = pipeline('text-classification',
                       model=AutoModelForSequenceClassification.from_pretrained('models/bert4sequence'),
                       tokenizer=tokenizer)

# %%

waveform = record_audio()

transcription = format_asr_result(asr_pipe(waveform))
tokens = format_tokenclf_result(token_pipe(transcription))
intent = format_seqclf_result(intent_pipe(transcription))

print(f" transcr: {transcription} \n tokens:{tokens} \n intent:{intent}")

# %%

import numpy as np
