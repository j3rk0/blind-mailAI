import os

import librosa
import sounddevice as sd
from google.cloud import texttospeech

from app.asr import ASRModule
from app.email import EmailModule
from app.understanding import UnderstandingModule

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f"{os.getcwd()}/data/tts_auth_key.json"


class Speaker:

    def __init__(self):
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="it", name='it-IT-standard-A'
        )

        self.client = texttospeech.TextToSpeechClient()
        # Select the type of audio file you want returned
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type

    def say(self, text):
        response = self.client.synthesize_speech(
            input=texttospeech.SynthesisInput(text=text), voice=self.voice, audio_config=self.audio_config
        )
        with open(f"temp.mp3", "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)

        audio, sr = librosa.load('temp.mp3')
        sd.play(audio, sr)
        sd.wait()


class App:
    def __init__(self):
        self.understanding_module = UnderstandingModule()
        self.asr_module = ASRModule()
        self.opened_mail = []
        self.mail_module = EmailModule()
        self.speaker = Speaker()
        # initialize graph

    def main_loop(self):
        if len(self.opened_mail) == 0:
            self.speaker.say('cosa vuoi fare?')

            text = self.asr_module.transcribe_audio(8)
            intent, slots = self.understanding_module.process(text)
            # aggiungi successore

            if intent == 'send_email' and len(self.opened_mail) == 0:
                self.speaker.say('invio una mail')
                mail = {'object': None, 'user': None, 'body': None}
                for slot in slots:
                    if slot[0] == 'object':
                        mail['object'] = slot[1]
                    elif slot[0] == 'person':
                        mail['user'] = slot[1]

                for field in mail.keys():
                    if mail[field] is None:
                        if field == 'user':
                            self.speaker.say('a chi va inviato?')
                            mail['user'] = self.asr_module.transcribe_audio()
                            # aggiorna grafo
                        elif field == 'object':
                            self.speaker.say('qual\' è l\' ogetto?')
                            mail['object'] = self.asr_module.transcribe_audio()
                            # aggiorna grafo
                        elif field == 'body':
                            self.speaker.say('qual è il corpo della mail?')
                            mail['body'] = self.asr_module.transcribe_audio(10)
                            # aggiorna grafo

                self.speaker.say('sei sicuro di voler inviare?')
                t = self.asr_module.transcribe_audio(3)
                while not 'si' in t or 'no' in t:
                    self.speaker.say('non ho capito, sei sicuro di voler inviare?')
                    t = self.asr_module.transcribe_audio(3)
                if t == 'si':
                    self.mail_module.dispatch_intent({'intent':intent,'mail':mail})

                # aggiorna grafo
                res = self.asr_module.transcribe_audio(3)
                # aggiorna grafo
                if res == 'si':
                    self.mail_module.dispatch_intent({'intent': intent, 'mail': mail})
                else:
                    self.main_loop()
                    return

            elif intent == 'list_email' or len(self.opened_mail) > 0:

                time = None
                object = None
                person = None
                for slot in slots:
                    if slot[0] == 'person':
                        person = slot[1]
                    elif slot[0] == 'object':
                        object = slot[1]
                    elif slot[0] == 'time':
                        time = slot[1]

                self.speaker.say(f'cerco le mail {f"da {person}" if person is not None else ""} '
                                 f'{f"con ogetto {object}" if object is not None else ""} '
                                 f'{f"ricevute in data {time}" if time is not None else ""}')

                # aggiorna grafo

                self.opened_mail = self.mail_module.get_email(object, time, person)
                self.speaker.say(f"ci sono {len(self.opened_mail)} "
                                 f"{f'da {person}' if person is not None else ''} "
                                 f"{f'in data {time}' if time is not None else ''} "
                                 f"{f'con ogetto {object}' if object is not None else ''}")
                self.main_loop()
                return
            elif text == 'esci':
                return
            elif text == 'aiuto':
                self.speaker.say('operazioni possibili')
                # aggiorna grafo
                self.main_loop()
                return
            else:
                self.speaker.say('non ho capito')
                self.main_loop()
                return
        else:
            mail = self.opened_mail[0]
            self.speaker.say(f"mail da {mail['person']} con oggetto {mail['object']}, cosa vuoi fare?")
            # aggiorna grafo
            text = self.asr_module.transcribe_audio()
            # aggiorna grafo
            intent, slots = self.understanding_module.process(text)
            if intent == 'read_email':
                self.speaker.say(f"{mail['body']}")
                self.opened_mail = mail
            elif intent == 'delete_email':
                self.speaker.say('sei sicuro di voler cancellare la mail?')
                t = self.asr_module.transcribe_audio(3)
                while not 'si' in t or 'no' in t:
                    self.speaker.say('non ho capito, sei sicuro di voler inviare?')
                    t = self.asr_module.transcribe_audio(3)
                if t == 'si':
                    self.mail_module.dispatch_intent({'intent': intent, 'mail': mail})
                # aggiorna grafo
                self.main_loop()
                return
            elif intent == 'forward_email':
                new_mail = {'body': mail['body'], 'object': f"fwd:{mail['object']}", 'person': None,
                            'time': {'day': 'oggi', 'month': 'oggi'}}
                for slot in slots:
                    if slot[0] == 'person':
                        new_mail['person'] = slot[1]
                if new_mail['person'] is None:
                    self.speaker.say('a chi va inoltrata la mail?')
                    # aggiorna grafo
                    new_mail['person'] = self.asr_module.transcribe_audio()
                    # aggiorna grafo
                self.mail_module.dispatch_intent({'intent': intent, 'mail': new_mail})

            elif intent == 'reply_email':
                new_mail = {'body': None, 'object': f're:{mail["object"]}', 'person': mail['person']}

                self.speaker.say('qual è il corpo della mail?')
                new_mail['body'] = self.asr_module.transcribe_audio(10)


                # aggiorna grafo

                self.mail_module.dispatch_intent({'intent': intent, 'mail': new_mail})

            elif intent == 'close_email':
                # aggiorna grafo
                if len(self.opened_mail) > 0:
                    del self.opened_mail[0]
                self.main_loop()
                return
            elif 'esci' in  text:
                self.opened_mail = []
                self.main_loop()
                return
            else:
                self.speaker.say('non ho capito')


# %%

app = App()
app.main_loop()
