import torch
from jiwer import wer
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, Wav2Vec2ProcessorWithLM
from utils.lib import load_dataset

# %%
train_data, eval_data, test_data = load_dataset()

# %%

processorLM = Wav2Vec2ProcessorWithLM.from_pretrained('models/wav2vec2LM')
processor = Wav2Vec2Processor.from_pretrained('models/wav2vec2')

modelLM = Wav2Vec2ForCTC.from_pretrained('models/wav2vec2LM')
model = Wav2Vec2ForCTC.from_pretrained('models/wav2vec2')

# %%


test_wer = []
testLM_wer = []

for i in range(test_data.shape[0]):
    print(f"{(i / test_data.shape[0] * 100):.2f}% completed")
    ground_truth = ''.join(processor.batch_decode(test_data['labels'][i]))
    waveform = test_data['input_values'][i]

    inputs = processorLM(waveform, sampling_rate=16000, return_tensor='pt', padding=True)
    input_values = torch.FloatTensor(inputs.input_values)
    attention_mask = torch.LongTensor(inputs.attention_mask)

    with torch.no_grad():
        logits = modelLM(input_values, attention_mask).logits

    predLM = processorLM.batch_decode(logits.numpy()).text[0].lower()
    pred = processor.decode(torch.argmax(logits, dim=-1)[0]).lower()
    test_wer.append(wer(pred, ground_truth))
    testLM_wer.append(wer(predLM, ground_truth))

# %%


avg_wer = sum(test_wer) / len(test_wer)
avg_LM_wer = sum(testLM_wer) / len(testLM_wer)
print(f"wer with no LM: {avg_wer}, wer with lm: {avg_LM_wer}")

# %%
from utils.lib import record_audio

waveforms = []
text = ['leggi una mail', 'rispondi alla mail', 'invia una mail con ogetto vincita lotteria',
        'elimina la mail', 'cerca le mail inviate a gennaio', 'inoltra questa mail',
        'vorrei cercare tutte le mail da fulvio camera ricevute ieri',
        'elimina la mail con oggetto ricevuta',
        'leggi le mail di oggi', 'inoltra la mail a vincenzo', 'rispondi a questa mail']

for t in text:
    print(f"{t}")
    waveforms.append(record_audio())

# %%


test_wer = []
testLM_wer = []
p = []
plm = []
for i in range(len(text)):
    print(f"{(i / len(text) * 100):.2f}% completed")
    ground_truth = text[i]
    waveform = waveforms[i]

    inputs = processorLM(waveform, sampling_rate=16000, return_tensor='pt', padding=True)
    input_values = torch.FloatTensor(inputs.input_values)
    attention_mask = torch.LongTensor(inputs.attention_mask)

    with torch.no_grad():
        logits = modelLM(input_values, attention_mask).logits

    predLM = processorLM.batch_decode(logits.numpy()).text[0].lower()
    pred = processor.decode(torch.argmax(logits, dim=-1)[0]).lower()

    p.append(pred)
    plm.append(predLM)

    test_wer.append(wer(pred, ground_truth))
    testLM_wer.append(wer(predLM, ground_truth))

# %%

avg_wer = sum(test_wer) / len(test_wer)
avg_LM_wer = sum(testLM_wer) / len(testLM_wer)
print(f"wer with no LM: {avg_wer}, wer with lm: {avg_LM_wer}")


#%%
import sounddevice as sd
print('start recording')
myrecording = sd.rec(int(5 * 16000), samplerate=16000, channels=1)
sd.wait()
print('stop recording')
#sd.play(myrecording,16000)


