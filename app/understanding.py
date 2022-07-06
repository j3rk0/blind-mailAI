from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification, AutoModelForSequenceClassification
from utils.lib import format_tokenclf_result, format_seqclf_result


class UnderstandingModule:

    def __init__(self):
        tokenizer = AutoTokenizer.from_pretrained('models/berttokenizer')

        self.token_clf = pipeline("token-classification",
                                  model=AutoModelForTokenClassification.from_pretrained('models/bert4token'),
                                  tokenizer=tokenizer, aggregation_strategy="simple")

        self.seq_clf = pipeline('text-classification',
                                model=AutoModelForSequenceClassification.from_pretrained('models/bert4sequence'),
                                tokenizer=tokenizer)

    def process(self, text):
        intent = format_seqclf_result(self.seq_clf(text))
        slots = format_tokenclf_result(self.token_clf(text))

        ret_slots = []
        for slot in slots:
            if not slot['label'] == 'O':
                if slot['label'][-3:] == 'PER':
                    ret_slots.append(('person', slot['text']))
                elif slot['label'][-3:] == 'OBJ':
                    ret_slots.append(('object', slot['text']))
                elif slot['label'][-4:] == 'DATE':
                    ret_slots.append(('date', slot['text']))

        return intent,ret_slots
