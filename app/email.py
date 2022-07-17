from email.message import EmailMessage
from email.parser import Parser
import smtplib
import poplib


class EmailModule:
    def __init__(self):

        with open('data/email.conf', 'r') as conf_file:
            conf = conf_file.readlines()
            sftp_server, sftp_port = conf[0].replace('\n', '').split(':')
            pop3_server, pop3_port = conf[1].replace('\n', '').split(':')
            self.user, pwd = conf[2].split(':')

        self.smtp_server = smtplib.SMTP_SSL(sftp_server, int(sftp_port))
        self.smtp_server.ehlo()
        self.smtp_server.login(self.user, pwd)

        self.pop3_server = poplib.POP3_SSL(pop3_server, int(pop3_port))
        self.pop3_server.user(self.user)
        self.pop3_server.pass_(pwd)

        with open('data/contacts.txt', 'r') as contancts_file:
            self.person_db = {}
            for contact in contancts_file.readlines():
                person, email = contact.replace('\n', '').split(':')
                self.person_db[person] = email

        self.mail_db = []

        for i in range(1, len(self.pop3_server.list()[1]) + 1):
            m = self.pop3_server.retr(i)
            m = Parser().parsestr('\n'.join([t.decode() for t in m[1]]))
            curr = {'object': m.get('Subject'), 'time': {'day': 'diciannove', 'month': 'dicembre'},
                    'body': m.get_payload()[0].get_payload().split('_')[0],
                    'person': m.get('From')}
            self.mail_db.append(curr)

    def dispatch_intent(self, intent):
        print(f"dispatching {intent}")

        if intent['intent'] == 'send_email':
            for p in self.person_db.keys():
                if intent['mail']['person'] in p:
                    intent['mail']['person'] = self.person_db[p]
                    break

        if intent['intent'] in ['send_email', 'reply_email', 'forward_email']:
            m = intent['mail']
            msg = EmailMessage()
            msg.set_content(m['body'])
            msg['Subject'] = m['object']
            msg['From'] = self.user
            msg['To'] = m['person'].split(' ')[-1].replace('>', '').replace('<', '')
            self.smtp_server.send_message(msg)
        elif intent['intent'] == 'delete_mail':
            self.mail_db.remove(intent['mail'])

    def get_email(self, object=None, time=None, person=None):
        return [mail for mail in self.mail_db if (object is None or object in mail['object']) and \
                (time is None or any(
                    [i in mail['time']['month'] or i in mail['time']['day'] for i in time.split(' ')])) and \
                (person is None or person in mail['person'])]

# %%
