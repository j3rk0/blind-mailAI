from transformers import pipeline, Wav2Vec2ForCTC, Wav2Vec2ProcessorWithLM
import sounddevice as sd
from utils.lib import format_asr_result
import librosa
import sounddevice as sd

class ASRModule:

    def __init__(self):
        asr_processor = Wav2Vec2ProcessorWithLM.from_pretrained('models/wav2vec2LM')
        self.pipe = pipeline('automatic-speech-recognition',
                             model=Wav2Vec2ForCTC.from_pretrained('models/wav2vec2LM'),
                             tokenizer=asr_processor.tokenizer,
                             feature_extractor=asr_processor.feature_extractor,
                             decoder=asr_processor.decoder)
        self.beep, self.sr = librosa.load('beep.mp3')

    def transcribe_audio(self, time=5):
        print('attendo risposta ....')

        sd.play(self.beep, self.sr)
        sd.wait()

        myrecording = sd.rec(int(time * 16000), samplerate=16000, channels=1)
        sd.wait()

        sd.play(self.beep, self.sr)
        sd.wait()

        print('elaboro risposta')
        ret = format_asr_result(self.pipe(myrecording.T[0]))
        print(ret)
        return ret

