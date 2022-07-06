class EmailModule:

    def __init__(self):
        self.mail_db = [
            {'object': 'comunicazione importante', 'time': {'day': 'diciannove', 'month': 'dicembre'}, 'person': '',
             'body': ''},
            {'object': 'hai vinto 100 euro', 'time': {'day': 'trenta', 'month': 'febbraio'},
             'person': 'riccardo arnese', 'body': 'rispondi alla mail col tuo iban per ricevere il premio'},
            {'object': 'convalida esame', 'time': {'day': 'quattordici', 'month': 'agosto'}, 'person': 'franco cutugno',
             'body': 'vorrei convalidare l esame di nlp con voto 30 e lode'},
            {'object': 'vincita lotteria', 'time': {'day': 'quattro', 'month': 'marzo'}, 'person': 'enalotto napoli',
             'body': 'complimenti! hai vinto il jackpot'},
            {'object': 'convalida idoneità', 'time': {'day': 'venticinque', 'month': 'novembre'},
             'person': 'guido russo', 'body': 'salve professore, vorrei convalidare l idonieta di inglese'},
            {'object': 'rimborso volo', 'time': {'day': 'trentuno', 'month': 'dicembre'}, 'person': 'riccardo arnese',
             'body': 'vorrei il rimborso per il volo che è stato cancellato'},

        ]

    def dispatch_intent(self, intent):
        print(f"dispatching {intent}")

    def get_email(self, object=None, time=None, person=None):

        return [mail for mail in self.mail_db if (object is None or object in mail['object']) and \
                (time is None or any(
                    [i in mail['time']['month'] or i in mail['time']['day'] for i in time.split(' ')])) and \
                (person is None or person in mail['person'])]
