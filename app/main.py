import os

import librosa
import sounddevice as sd
from google.cloud import texttospeech

from app.graph import GraphDST
from app.asr import ASRModule
from app.email import EmailModule
from app.understanding import UnderstandingModule

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f"{os.getcwd()}/data/tts_auth_key.json"
os.environ['TOKENIZERS_PARALLELISM'] = 'true'

"""
cerca mail da riccardo
chiudi la mail
leggi la mail
rispondi alla mail

"""


# wewe

# noinspection PyTypeChecker
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
        self.speaker = Speaker()
        self.speaker.say('caricamento moduli, attendere')
        self.understanding_module = UnderstandingModule()
        self.asr_module = ASRModule()
        self.opened_mail = []
        self.mail_module = EmailModule()
        self.graph_module = GraphDST()
        self.speaker.say('caricamento completato')
        # initialize graph

    def main_loop(self):
        self.graph_module.print_graph()
        if len(self.opened_mail) == 0:
            self.speaker.say('cosa vuoi fare?')
            self.graph_module.exchange('System', 'cosa vuoi fare?')

            text = self.asr_module.transcribe_audio(6)
            intent, slots = self.understanding_module.process(text)

            # aggiungi successore

            if intent == 'send_email' and len(self.opened_mail) == 0:
                self.speaker.say('invio una mail')
                self.graph_module.exchange('System', 'invio una mail')
                mail = {'object': None, 'person': None, 'body': None}
                for slot in slots:
                    if slot[0] == 'object':
                        mail['object'] = slot[1]
                    elif slot[0] == 'person':
                        mail['person'] = slot[1]
                self.graph_module.exchange('User', text, intent, slots)
                for field in mail.keys():
                    if mail[field] is None:
                        if field == 'person':
                            self.speaker.say('a chi va inviato?')
                            self.graph_module.exchange('System', 'a chi va inviato?')
                            mail['person'] = self.asr_module.transcribe_audio()
                            self.graph_module.exchange('User', mail['person'], None, [('person', mail['person'])])

                        elif field == 'object':
                            self.speaker.say('qual\' è l\' oggetto?')
                            self.graph_module.exchange('System', 'qual è l oggetto?')
                            mail['object'] = self.asr_module.transcribe_audio()
                            self.graph_module.exchange('User', mail['object'], None, [('person', mail['object'])])
                            # aggiorna grafo
                        elif field == 'body':
                            self.speaker.say('qual è il corpo della mail?')
                            self.graph_module.exchange('System', 'qual è il corpo della mail?')
                            mail['body'] = self.asr_module.transcribe_audio(10)
                            self.graph_module.exchange('User', mail['body'], None, [('person', mail['body'])])
                            # aggiorna grafo

                if self.ask_confirm('inviare'):
                    self.mail_module.dispatch_intent({'intent': intent, 'mail': mail})
                    self.speaker.say('mail inviata')
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
                                 f'{f"con oggetto {object}" if object is not None else ""} '
                                 f'{f"ricevute in data {time}" if time is not None else ""}')

                self.graph_module.exchange('System', f'cerco le mail {f"da {person}" if person is not None else ""} '
                                                     f'{f"con oggetto {object}" if object is not None else ""} '
                                                     f'{f"ricevute in data {time}" if time is not None else ""}')

                # aggiorna grafo

                self.opened_mail = self.mail_module.get_email(object, time, person)
                self.speaker.say(f"ci sono {len(self.opened_mail)} nuove mail"
                                 f"{f'da {person}' if person is not None else ''} "
                                 f"{f'in data {time}' if time is not None else ''} "
                                 f"{f'con oggetto {object}' if object is not None else ''}")

                self.graph_module.exchange('System', f"ci sono {len(self.opened_mail)} nuove mail"
                                                     f"{f'da {person}' if person is not None else ''} "
                                                     f"{f'in data {time}' if time is not None else ''} "
                                                     f"{f'con oggetto {object}' if object is not None else ''}")
                self.main_loop()
                return
            elif 'esci' in text:
                self.speaker.say('ciao!')
                return
            elif 'aiuto' in text:
                self.speaker.say('operazioni possibili')
                self.graph_module.exchange('System', 'operazioni possibili')
                self.main_loop()
                return
            else:
                self.speaker.say('non ho capito')
                self.main_loop()
                return
        else:
            mail = self.opened_mail[0]
            self.speaker.say(f"mail da {mail['person']} con oggetto {mail['object']}, cosa vuoi fare?")
            self.graph_module.exchange('System',
                                       f"mail da {mail['person']} con oggetto {mail['object']}, cosa vuoi fare?")
            text = self.asr_module.transcribe_audio()
            intent, slots = self.understanding_module.process(text)

            if intent == 'read_email':
                self.graph_module.exchange('User', text, intent, None)
                self.speaker.say(f"{mail['body']}")
                self.graph_module.exchange('System', f"{mail['body']}")
                self.main_loop()
                return
            elif intent == 'delete_email':
                self.graph_module.exchange('User', text, intent, None)

                if self.ask_confirm('cancellare la mail'):
                    del self.opened_mail[0]
                    self.mail_module.dispatch_intent({'intent': intent, 'mail': mail})
                    self.speaker.say('mail cancellata')
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
                    self.graph_module.exchange('System', 'a chi va inoltrata la mail?')
                    new_mail['person'] = self.asr_module.transcribe_audio()
                    self.graph_module.exchange('User', new_mail['person'], None, new_mail['person'])

                self.graph_module.exchange('User', text, intent, [('person', new_mail['person'])])

                if self.ask_confirm('inoltrare'):
                    self.mail_module.dispatch_intent({'intent': intent, 'mail': new_mail})
                    self.speaker.say('mail inoltrarta')
                self.main_loop()
                return

            elif intent == 'reply_email':
                new_mail = {'body': None, 'object': f're:{mail["object"]}', 'person': mail['person']}
                self.graph_module.exchange('User', text, intent, None)
                self.speaker.say('qual è il corpo della mail?')
                self.graph_module.exchange('System', 'qual è il corpo della mail?')
                new_mail['body'] = self.asr_module.transcribe_audio(10)

                self.graph_module.exchange('User', text, intent,
                                           [('person', mail['person']), ('object', mail['object'])])

                if self.ask_confirm('rispondere'):
                    self.mail_module.dispatch_intent({'intent': intent, 'mail': new_mail})
                    self.speaker.say('risposta inviata')
                self.main_loop()
                return
            elif intent == 'close_email':
                self.graph_module.exchange('User', text, intent, None)
                self.graph_module.exchange('User', intent)
                if len(self.opened_mail) > 0:
                    del self.opened_mail[0]
                self.main_loop()
                return
            elif 'esci' in text:
                self.graph_module.exchange('User', intent)
                self.speaker.say('ciao!')
                return
            else:
                self.graph_module.exchange('User', intent)
                self.speaker.say('non ho capito')
                self.main_loop()
                return

    def ask_confirm(self, operation):
        self.speaker.say(f'sei sicuro di voler {operation}?')
        t = self.asr_module.transcribe_audio(3)
        while 'si' not in t and 'no' not in t:
            self.speaker.say(f'non ho capito, sei sicuro di voler {operation}?')
            t = self.asr_module.transcribe_audio(3)
        if 'si' in t:
            return True
        return False


# %%
app = App()

# %%
app.main_loop()
