from app.understanding import UnderstandingModule
from app.asr import ASRModule
from app.email import EmailModule


class App:
    def __init__(self):
        self.understanding_module = UnderstandingModule()
        self.asr_module = ASRModule()
        self.opened_mail = []
        self.mail_module = EmailModule()
        # initialize graph

    def main_loop(self):
        if len(self.opened_mail) == 0:
            print('cosa vuoi fare?')

            text = self.asr_module.transcribe_audio()
            intent, slots = self.understanding_module.process(text)
            # aggiungi successore

            if intent == 'send_email' and len(self.opened_mail) == 0:
                print('invio una mail')
                mail = {'object': None, 'user': None, 'body': None}
                for slot in slots:
                    if slot[0] == 'object':
                        mail['object'] = slot[1]
                    elif slot[0] == 'person':
                        mail['user'] = slot[1]

                for field in mail.keys():
                    if mail[field] is None:
                        if field == 'user':
                            print('a chi va inviato?')
                            mail['user'] = self.asr_module.transcribe_audio()
                            # aggiorna grafo
                        elif field == 'object':
                            print('qual\' è l\' ogetto?')
                            mail['object'] = self.asr_module.transcribe_audio()
                            # aggiorna grafo
                        elif field == 'body':
                            print('qual è il corpo della mail?')
                            mail['body'] = self.asr_module.transcribe_audio(10)
                            # aggiorna grafo

                print('sei sicuro di voler inviare?')
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

                print(f'cerco le mail {f"da {person}" if person is not None else ""} '
                      f'{f"con ogetto {object}" if object is not None else ""} '
                      f'{f"ricevute in data {time}" if time is not None else ""}')

                # aggiorna grafo

                self.opened_mail = self.mail_module.get_email(object, time, person)
                self.main_loop()
                return
            elif text == 'esci':
                return
            elif text == 'aiuto':
                print('operazioni possibili')
                # aggiorna grafo
                self.main_loop()
                return
            else:
                print('non ho capito, prego ripeti')
                self.main_loop()
                return
        else:
            while len(self.opened_mail) > 0:
                mail = self.opened_mail[0]
                print(f"mail da {mail['person']} con oggetto {mail['object']}, cosa vuoi fare?")
                # aggiorna grafo
                text = self.asr_module.transcribe_audio()
                # aggiorna grafo
                intent, slots = self.understanding_module.process(text)
                print(f'{text} {intent}')
                if intent == 'read_email':
                    print(f"{mail['body']}")
                    self.opened_mail = mail
                elif intent == 'delete_email':
                    print('sei sicuro di voler cancellare la mail?')
                    # aggiorna grafo
                    if self.asr_module.transcribe_audio() == 'si':
                        # aggiorna grafo
                        self.mail_module.dispatch_intent(mail)
                elif intent == 'forward_email':
                    new_mail = {'body': mail['body'], 'object': f"fwd:{mail['object']}", 'person': None,
                                'time': {'day': 'oggi', 'month': 'oggi'}}
                    for slot in slots:
                        if slot[0] == 'person':
                            new_mail['person'] = slot[1]
                    if new_mail['person'] is None:
                        print('a chi va inoltrata la mail?')
                        # aggiorna grafo
                        new_mail['person'] = self.asr_module.transcribe_audio()
                        # aggiorna grafo
                    self.mail_module.dispatch_intent({'intent': intent, 'mail': new_mail})

                elif intent == 'reply_email':
                    new_mail = {'body': None, 'object': f're:{mail["object"]}', 'person': mail['person']}

                    print('qual è il corpo della mail?')
                    new_mail['body'] = self.asr_module.transcribe_audio(10)

                    # aggiorna grafo

                    self.mail_module.dispatch_intent({'intent': intent, 'mail': new_mail})

                elif intent == 'close_email':
                    # aggiorna grafo
                    del self.opened_mail[0]
                    self.main_loop()
                    return
                elif text == 'esci':
                    self.opened_mail = []
                    self.main_loop()
                    return


#%%

app = App()
app.main_loop()


