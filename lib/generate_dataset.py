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

outside
b-per
i-per
b-obj
i-obj
b-time
i-time
---------------------
"""

prefixes = [['potresti ', 'vorresti '], ['vorrei ', 'voglio '], ['']]
prefix_tag = [[['O'], ['O']], [['O'], ['O']], [[]]]

intents = [{0: ['inviare', 'mandare', 'spedire'],
            1: ['cercarmi', 'leggermi', 'cercare', 'leggere'],
            2: ['leggerla', 'leggermela'],
            3: ['cancellare', 'eliminare', 'cancellarla', 'eliminarla'],
            4: ['rispondere', 'rispondergli'],
            5: ['inoltrare', 'inoltrarla'],
            6: ['chiudere', 'chiuderla']},

           {0: ['inviare', 'mandare', 'spedire'],
            1: ['cercare', 'leggere'],
            2: ['leggerla', ],
            3: ['cancellare', 'eliminare', 'cancellarla', 'eliminarla'],
            4: ['rispondere', 'rispondergli'],
            5: ['inoltrare', 'inoltrarla'],
            6: ['chiudere', 'chiuderla']},

           {0: ['invia', 'manda', 'spedisci'],
            1: ['cerca', 'leggi', 'cerchi'],
            2: ['leggila', ],
            3: ['cancella', 'elimina', 'cancellala', 'eliminala'],
            4: ['rispondi', 'rispondigli'],
            5: ['inoltra', 'inoltrala'],
            6: ['chiudi', 'chiudila']}
           ]

intent_tag = ['O']

cojs = {0: ['una mail', 'un messaggio'], 1: ['le mail', 'i messaggi']}

coj_tag = ['O', 'O']

person_conj = {0: 'a',
               1: 'da',
               5: 'a'}
per_conj_tag = ['O']

persons = ['Gianluca Magalli', 'Pietro Pisani', 'Jessica esposito', 'marco rossi', 'giuseppe esposito', 'fulvio camera',
           'riccardo arnese', 'sabrina mennella', 'vincenzo desimone']

person_tag = ['B-PER', 'I-PER']

obj_conj = 'con ogetto'
obj_conj_tag = ['O', 'O']

objects = ['comunicazione importante', 'ordine del giorno', 'richiesta modulo', 'consegna progetto',
           'conferma invito', 'attivazione profilo']
objects_tag = [['B-OBJ', 'I-OBJ'], ['B-OBJ', 'I-OBJ', 'I-OBJ'], ['B-OBJ', 'I-OBJ'], ['B-OBJ', 'I-OBJ'],
               ['B-OBJ', 'I-OBJ'], ['B-OBJ', 'I-OBJ']]

date_conj = ['ricevute', 'di']
date_conj_tag = ['O']

dates = ['il tredici aprile', 'il quindici maggio', 'a marzo', 'a luglio', 'questo mese', 'questa settimana',
         'ieri', 'oggi']
dates_tag = [['O', 'B-TIME', 'I-TIME'], ['O', 'B-TIME', 'I-TIME'], ['O', 'B-TIME'], ['O', 'B-TIME'],
             ['B-TIME', 'I-TIME'],
             ['B-TIME', 'I-TIME'], ['B-TIME'], ['B-TIME']]
# ricorda "di il" va stotituito con 'del'

# %%

sentences_array = []
intent_array = []
slot_array = []

for prefix_type in range(len(prefixes)):
    for prefix_index in range(len(prefixes[prefix_type])):
        pref = prefixes[prefix_type][prefix_index]
        pref_tag = prefix_tag[prefix_type][prefix_index]
        for curr_intent in range(6):
            for intent_str in intents[prefix_type][curr_intent]:

                if curr_intent not in [0, 1, 5]:  # INTENT WITHOUT SLOTS
                    sentences_array.append(f"{pref}{intent_str}")
                    intent_array.append(curr_intent)
                    slot_array.append(pref_tag + intent_tag)
                elif curr_intent in [0, 1]:
                    for coj in cojs[curr_intent]:
                        # NO SLOTS
                        sentences_array.append(f"{pref}{intent_str} {coj}")
                        intent_array.append(curr_intent)
                        slot_array.append(pref_tag + intent_tag + coj_tag)

                        # ONLY PERSONS
                        for per in persons:
                            sentences_array.append(f"{pref}{intent_str} {coj} {person_conj[curr_intent]} {per}")
                            intent_array.append(curr_intent)
                            slot_array.append(pref_tag + intent_tag + coj_tag + per_conj_tag + person_tag)

                            # PERSONS + OBJECT
                            for obj_index in range(len(objects)):
                                sentences_array.append(
                                    f"{pref}{intent_str} {coj} {person_conj[curr_intent]} {per} {obj_conj} {objects[obj_index]}")
                                intent_array.append(curr_intent)
                                slot_array.append(
                                    pref_tag + intent_tag + coj_tag + per_conj_tag + person_tag + obj_conj_tag +
                                    objects_tag[obj_index])

                                # PERSONS + OBJECT + DATE
                                if curr_intent == 1:
                                    for dconj in date_conj:
                                        for date_index in range(len(dates)):
                                            sentences_array.append(
                                                f"{pref}{intent_str} {coj} {person_conj[curr_intent]} {per} {obj_conj} {objects[obj_index]} {dconj} {dates[date_index]}")
                                            intent_array.append(curr_intent)
                                            slot_array.append(
                                                pref_tag + intent_tag + coj_tag + per_conj_tag + person_tag + coj_tag +
                                                objects_tag[obj_index] + date_conj_tag + dates_tag[date_index])

                            # PERSONS + DATES
                            if curr_intent == 1:
                                for dconj in date_conj:
                                    for date_index in range(len(dates)):
                                        sentences_array.append(
                                            f"{pref}{intent_str} {coj} {person_conj[curr_intent]} {per} {dconj} {dates[date_index]}")
                                        intent_array.append(curr_intent)
                                        slot_array.append(pref_tag + intent_tag + coj_tag + per_conj_tag + person_tag +
                                                          date_conj_tag + dates_tag[date_index])

                                        # PERSONS + DATE + OBJECT
                                        for obj_index in range(len(objects)):
                                            sentences_array.append(
                                                f"{pref}{intent_str} {coj} {person_conj[curr_intent]} {per} {dconj} {dates[date_index]} {obj_conj} {objects[obj_index]}")
                                            intent_array.append(curr_intent)
                                            slot_array.append(
                                                pref_tag + intent_tag + coj_tag + per_conj_tag + person_tag +
                                                date_conj_tag + dates_tag[date_index] + obj_conj_tag +
                                                objects_tag[obj_index])

                        # ONLY OBJECTS
                        for obj_index in range(len(objects)):
                            sentences_array.append(f"{pref}{intent_str} {coj} {obj_conj} {objects[obj_index]}")
                            intent_array.append(curr_intent)
                            slot_array.append(pref_tag + intent_tag + coj_tag + obj_conj_tag + objects_tag[obj_index])

                            # OBJECT + PERSON
                            for per in persons:
                                sentences_array.append(
                                    f"{pref}{intent_str} {coj} {obj_conj} {objects[obj_index]} {person_conj[curr_intent]} {per}")
                                intent_array.append(curr_intent)
                                slot_array.append(pref_tag + intent_tag + coj_tag + obj_conj_tag +
                                                  objects_tag[obj_index] + per_conj_tag + person_tag)
                                # OBJECT + PERSONS + DATE
                                if curr_intent == 1:
                                    for dconj in date_conj:
                                        for date_index in range(len(dates)):
                                            sentences_array.append(
                                                f"{pref}{intent_str} {coj} {obj_conj} {objects[obj_index]} {person_conj[curr_intent]} {per} {dconj} {dates[date_index]}")
                                            intent_array.append(curr_intent)
                                            slot_array.append(pref_tag + intent_tag + coj_tag + obj_conj_tag +
                                                              objects_tag[obj_index] + per_conj_tag + person_tag +
                                                              date_conj_tag + dates_tag[date_index])

                            # OBJECT + DATE
                            if curr_intent == 1:
                                for dconj in date_conj:
                                    for date_index in range(len(dates)):
                                        sentences_array.append(
                                            f"{pref}{intent_str} {coj} {obj_conj} {objects[obj_index]} {dconj} {dates[date_index]}")
                                        intent_array.append(curr_intent)
                                        slot_array.append(pref_tag + intent_tag + coj_tag +
                                                          obj_conj_tag +
                                                          objects_tag[obj_index] +
                                                          date_conj_tag + dates_tag[date_index])
                                        # OBJECT + DATE + PERSONS
                                        for per in persons:
                                            sentences_array.append(
                                                f"{pref}{intent_str} {coj}  {obj_conj} {objects[obj_index]} {dconj} {dates[date_index]} {person_conj[curr_intent]} {per}")
                                            intent_array.append(curr_intent)
                                            slot_array.append(pref_tag + intent_tag + coj_tag + obj_conj_tag +
                                                              date_conj_tag + dates_tag[date_index] +
                                                              objects_tag[obj_index] + per_conj_tag + person_tag)

                        # ONLY DATES
                        if curr_intent == 1:
                            for dconj in date_conj:
                                for date_index in range(len(dates)):
                                    sentences_array.append(f"{pref}{intent_str} {coj} {dconj} {dates[date_index]}")
                                    intent_array.append(curr_intent)
                                    slot_array.append(pref_tag + intent_tag + coj_tag +
                                                      date_conj_tag + dates_tag[date_index])

                                # DATES + PERSONS
                                for per in persons:
                                    sentences_array.append(
                                        f"{pref}{intent_str} {coj} {dconj} {dates[date_index]} {person_conj[curr_intent]} {per}")
                                    intent_array.append(curr_intent)
                                    slot_array.append(pref_tag + intent_tag + coj_tag + date_conj_tag +
                                                      dates_tag[date_index] + per_conj_tag + person_tag)

                                    # DATES + PERSONS + OBJECTS
                                    for obj_index in range(len(objects)):
                                        sentences_array.append(
                                            f"{pref}{intent_str} {coj} {dconj} {dates[date_index]} {person_conj[curr_intent]} {per} {obj_conj} {objects[obj_index]}")
                                        intent_array.append(curr_intent)
                                        slot_array.append(
                                            pref_tag + intent_tag + coj_tag + date_conj_tag +
                                            dates_tag[date_index] + per_conj_tag + person_tag +
                                            obj_conj_tag + objects_tag[obj_index])
                                # DATES + OBJECTS
                                for obj_index in range(len(objects)):
                                    sentences_array.append(
                                        f"{pref}{intent_str} {coj} {dconj} {dates[date_index]} {obj_conj} {objects[obj_index]}")
                                    intent_array.append(curr_intent)
                                    slot_array.append(
                                        pref_tag + intent_tag + coj_tag + date_conj_tag +
                                        dates_tag[date_index] + obj_conj_tag + objects_tag[obj_index])

                                    # DATES + OBJECT + PERSON
                                    for per in persons:
                                        sentences_array.append(
                                            f"{pref}{intent_str} {coj} {dconj} {dates[date_index]} {obj_conj} {objects[obj_index]} {person_conj[curr_intent]} {per}")
                                        intent_array.append(curr_intent)
                                        slot_array.append(pref_tag + intent_tag + coj_tag + date_conj_tag +
                                                          dates_tag[date_index] + obj_conj_tag +
                                                          objects_tag[obj_index] + per_conj_tag + person_tag)
                else:  # INTENT 5
                    sentences_array.append(f"{pref}{intent_str}")
                    intent_array.append(curr_intent)
                    slot_array.append(pref_tag + intent_tag)

                    for per in persons:
                        sentences_array.append(f"{pref}{intent_str} {person_conj[curr_intent]} {per}")
                        intent_array.append(curr_intent)
                        slot_array.append(pref_tag + intent_tag + per_conj_tag + person_tag)

for i in range(len(sentences_array)):
    sentences_array[i] = sentences_array[i].replace('di il', 'del').replace('di a', 'di')

# %%

import pandas as pd

df = pd.DataFrame.from_dict({'text': sentences_array, 'entities': slot_array, 'intent': intent_array})
df.to_csv('data/ner_dataset.csv')