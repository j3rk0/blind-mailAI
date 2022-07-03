"""
-----------------
intent:

0 send_email
1 list_email
2 read_email
3 delete_email
4 reply_email
5 forward_email
6 close_email
------------------
entities:

O: outside
b-per: inzio slot persona
i-per: interno slot persona
b-obj: inizio slot oggetto
i-obj: interno slot oggetto
b-date: inizio slot data
i-date: interno slot data
---------------------
"""

import random

import pandas as pd


def get_random_object():
    conj = ' con ogetto'

    ret_text = ['informazioni ricevimento', 'elezioni studentesche', 'Posticipo incontro',
                'Firme per la partecipazione al corso di informatica', 'Ritiro attestato',
                'Problema accesso sito universitario', 'Promemoria', 'info su prescrizione medica',
                'Assistenza tecnica', 'Reclamo e richiesta di assistenza', 'Candidatura spontanea',
                'comunicazione importante', 'ordine del giorno', 'richiesta modulo', 'consegna progetto',
                'conferma invito', 'attivazione profilo'][random.randint(0, 15)].lower()

    ret_slot = ['O', 'O', 'B-OBJ'] + ['I-OBJ'] * (len(ret_text.split(' ')) - 1)

    return f"{conj} {ret_text}", ret_slot


with open('data/italian_names.csv') as f:
    names = [name.replace('\n', '').replace(',', ' ') for name in f.readlines()]


def get_random_person(to=True):
    name = names[random.randint(0, len(names) - 1)]

    conj = ['da', 'di', 'inviate da', 'con mittente'][random.randint(0, 3)]
    if to:
        conj = ['a', 'per', 'con destinatario'][random.randint(0, 2)]
        if name.lower()[0] in ['a', 'e', 'i', 'o', 'u'] and conj == 'a':
            conj = 'ad'

    return f" {conj} {name.lower()}", ['O'] * len(conj.split(' ')) + ['B-PER', 'I-PER']


def get_random_date():
    ret_text = ''
    ret_slots = []
    type = ['exact', 'relative', 'month'][random.randint(0, 2)]

    if type == 'exact':

        conj = ['ricevute il', 'del', 'con data'][random.randint(0, 2)]
        day = ['primo', 'due', 'tre', 'quattro', 'cingue', 'sei', 'sette', 'otto', 'nove', 'dieci',
               'undici', 'dodici', 'tredici', 'quattordici', 'quindici', 'sedici', 'diciasette',
               'diciotto', 'diciannove', 'venti', 'ventuno', 'ventidue', 'ventitre', 'ventiquattro',
               'venticinque', 'ventisei', 'ventisette', 'ventotto', 'ventinove', 'trenta',
               'trentuno'][random.randint(0, 30)]
        month = ['gennaio', 'febbraio', 'marzo', 'aprile',
                 'maggio', 'giugno', 'luglio', 'agosto',
                 'settembre', 'ottobre', 'novembre', 'dicembre'][random.randint(0, 11)]
        ret_text = f"{conj} {day} {month}"
        ret_slots = ['O'] * len(conj.split(' ')) + ['B-DATE', 'I-DATE']
    elif type == 'relative':
        ret_text, ret_slots = [('di questo mese', ['O', 'B-DATE', 'I-DATE']),
                               ('ricevute questo mese', ['O', 'B-DATE', 'I-DATE']),
                               ('del mese scorso', ['O', 'B-DATE', 'I-DATE']),
                               ('ricevute il mese scorso', ['O', 'O', 'B-DATE', 'I-DATE']),
                               ('di questa settimana', ['O', 'B-DATE', 'I-DATE']),
                               ('ricevute questa settimana', ['O', 'B-DATE', 'I-DATE']),
                               ('della settimana scorsa', ['O', 'B-DATE', 'I-DATE']),
                               ('ricevute la settimana scorsa', ['O', 'O', 'B-DATE', 'I-DATE']),
                               ('di oggi', ['O', 'B-DATE']),
                               ('ricevute oggi', ['O', 'B-DATE']),
                               ('di ieri', ['O', 'B-DATE']),
                               ('ricevute ieri', ['O', 'B-DATE'])][random.randint(0, 11)]
    elif type == 'month':
        pref = ['ricevute a', 'di'][random.randint(0, 1)]
        month = ['gennaio', 'febbraio', 'marzo', 'aprile',
                 'maggio', 'giugno', 'luglio', 'agosto',
                 'settembre', 'ottobre', 'novembre', 'dicembre'][random.randint(0, 11)]
        ret_text = f"{pref} {month}"
        ret_slots = ['O'] * len(pref.split(' ')) + ['B-DATE']
    return f" {ret_text}", ret_slots


def compose_sentence(intent):
    ret_text, ret_slots = "", None
    if intent == 0:

        if random.randint(1, 7) <= 4:
            ret_text = ['potresti', 'vorresti', 'voglio', 'puoi'][random.randint(0, 1)] + \
                       " " + ['inviare', 'mandare', 'spedire'][random.randint(0, 2)] + \
                       " " + ['una mail', 'un messaggio'][random.randint(0, 1)]
            ret_slots = ['O', 'O', 'O', 'O']
        else:
            ret_text = ['invia', 'manda', 'spedisci'][random.randint(0, 2)] + ' ' + \
                       ['una mail', 'un messaggio'][random.randint(0, 1)]
            ret_slots = ['O', 'O', 'O']

        additional_slots = [['obj'], ['obj', 'per'], ['per'], ['per', 'obj'], []][random.randint(0, 4)]

        text_to_add, slot_to_add = '', []
        for slot in additional_slots:
            if slot == 'obj':
                text_to_add, slot_to_add = get_random_object()
            elif slot == 'per':
                text_to_add, slot_to_add = get_random_person()
            ret_text += text_to_add
            ret_slots += slot_to_add

    elif intent == 1:

        n = random.randint(0, 2)

        if n == 0:
            ret_text = ['potresti', 'vorresti'][random.randint(0, 1)] + ' ' + \
                       ['cercarmi', 'leggermi', 'cercare', 'leggere'][random.randint(0, 3)] + ' ' + \
                       ['le mail', 'i messaggi'][random.randint(0, 1)]
            ret_slots = ['O', 'O', 'O', 'O']

        elif n == 1:
            ret_text = ['vorrei', 'voglio'][random.randint(0, 1)] + ' ' + \
                       ['cercare', 'leggere'][random.randint(0, 1)] + ' ' + \
                       ['delle mail', 'dei messaggi', 'le mail', 'i messaggi'][random.randint(0, 1)]
            ret_slots = ['O', 'O', 'O', 'O']
        else:
            ret_text = ['cerca', 'leggi', 'cerchi'][random.randint(0, 2)] + ' ' + \
                       ['le mail', 'i messaggi'][random.randint(0, 1)]

            ret_slots = ['O', 'O', 'O']

        slots = ['obj', 'per', 'date', 'no']

        additional_slots = [[t1, t2, t3] for t1 in slots for t2 in slots for t3 in slots
                            if (t1 != 'no' and t2 == 'no' and t3 == 'no') or
                            (t1 != 'no' and t2 != 'no' and t3 == 'no' and t1 != t2) or
                            (t1 != 'no' and t2 != 'no' and t3 != 'no' and t1 != t2 and t2 != t3 and t3 != t1)]

        additional_slots = additional_slots[random.randint(0, len(additional_slots) - 1)]
        for slot in additional_slots:
            text_to_add, slot_to_add = '', []
            if slot == 'obj':
                text_to_add, slot_to_add = get_random_object()
            elif slot == 'per':
                text_to_add, slot_to_add = get_random_person(to=False)
            elif slot == 'date':
                text_to_add, slot_to_add = get_random_date()

            ret_text += text_to_add
            ret_slots += slot_to_add

    elif intent == 2:

        n = random.randint(0, 2)
        if n == 0:
            ret_text = ['potresti ', 'vorresti '][random.randint(0, 1)] + ' ' + \
                       ['leggerla', 'leggermela'][random.randint(0, 1)]
        elif n == 1:
            ret_text = ['vorrei', 'voglio'][random.randint(0, 1)] + ' ' + \
                       ['leggerla', 'leggere la mail', 'leggere il messaggio'][random.randint(0, 2)]
        else:
            ret_text = ['leggila', 'leggi', 'leggimela', 'leggimi la mail',
                        'leggimi il messaggio', 'leggi la mail', 'leggi il messaggio'][random.randint(0, 4)]

        ret_slots = ['O'] * len(ret_text.split(' '))
    elif intent == 3:
        if random.randint(0, 1) == 0:
            ret_text = ['potresti', 'vorresti', 'vorrei', 'voglio'][random.randint(0, 3)] + ' ' + \
                       ['cancellare la mail', 'cancellare il messaggio', 'eliminare la mail', 'cancellarla',
                        'eliminare il messaggio', 'eliminarla'][random.randint(0, 5)]
        else:
            ret_text = ['cancella', 'cancella la mail', 'cancella il messaggio', 'elimina', 'elimina la mail',
                        'elimina il messaggio', 'cancellala', 'eliminala'][random.randint(0, 7)]

        ret_slots = ['O'] * len(ret_text.split(' '))
    elif intent == 4:
        if random.randint(0, 1) == 0:
            ret_text = ['potresti', 'vorresti', 'vorrei', 'voglio'][random.randint(0, 3)] + ' ' + \
                       ['rispondere', 'rispondere alla mail', 'rispondere al messaggio', 'rispondergli'][
                           random.randint(0, 3)]
        else:
            ret_text = ['rispondi', 'rispondi alla mail', 'rispondi al messaggio', 'rispondigli'][random.randint(0, 3)]

        ret_slots = ['O'] * len(ret_text.split(' '))
    elif intent == 5:
        if random.randint(0, 1) == 0:
            ret_text = ['potresti', 'vorresti', 'vorrei', 'voglio'][random.randint(0, 3)] + ' ' + \
                       ['inoltrare', 'inoltrare la mail', 'inoltrare il messaggio', 'inoltrarla'][random.randint(0, 3)]
        else:
            ret_text = ['inoltra', 'inoltra la mail', 'inoltra il messaggio', 'inoltrala'][random.randint(0, 3)]

        ret_slots = ['O'] * len(ret_text.split(' '))

        text_to_add, slot_to_add = get_random_person()
        ret_text += text_to_add
        ret_slots += slot_to_add
    elif intent == 6:
        if random.randint(0, 1) == 0:
            ret_text = ['potresti', 'vorresti', 'vorrei', 'voglio'][random.randint(0, 3)] + ' ' + \
                       ['chiudere', 'chiudere la mail', 'chiudere il messaggio', 'chiuderla', 'uscire',
                        'uscire dalla mail', 'uscire dal messaggio'][random.randint(0, 6)]
        else:
            ret_text = ['chiudi', 'chiudila', 'chiudi la mail', 'chiudi il messaggio', 'esci dalla mail',
                        'esci dal messaggio'][random.randint(0, 5)]

        ret_slots = ['O'] * len(ret_text.split(' '))

    if ret_text.count('con') > 1:
        tokens = ret_text.split(' ')
        found_first = False
        for i in range(len(tokens) - 1):
            if tokens[i] == 'con' and not found_first:
                found_first = True
            elif tokens[i] == 'con' and tokens[i + 1] == 'oggetto':
                tokens[i] = 'ed'
            elif tokens[i] == 'con':
                tokens[i] = 'e'
        ret_text = ' '.join(tokens)

    return ret_text, ret_slots


# %%

examples_for_intent = 50
text_array = []
slot_array = []
intent_array = []

for intent in range(7):
    for _ in range(examples_for_intent):
        text, slots = compose_sentence(intent)
        text_array.append(text)
        slot_array.append(slots)
        intent_array.append(intent)

res = pd.DataFrame.from_dict({'text': text_array, 'slots': slot_array, 'intent': intent_array})
res.to_csv('data/dataset_ner.csv')