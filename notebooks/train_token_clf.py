import pandas as pd
from datasets import Dataset
from sklearn.model_selection import train_test_split
from transformers import BertTokenizerFast, BertForTokenClassification, AutoTokenizer
from transformers import DataCollatorForTokenClassification, IntervalStrategy
from datasets import load_metric
from transformers import AutoModelForTokenClassification, TrainingArguments, Trainer
import numpy as np
from datasets import load_metric



# %%

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
model = AutoModelForTokenClassification.from_pretrained("distilbert-base-uncased",num_labels=7)
# %%


ner_ids = {'O': 0, 'B-PER': 1, 'I-PER': 2, 'B-OBJ': 3, 'I-OBJ': 4, 'B-DATE': 5, 'I-DATE': 6}

df = pd.read_csv('data/dataset.csv', index_col=0)

train_df, eval_df = train_test_split(df, train_size=.8)
# %%

train = {'id': [i for i in range(train_df.shape[0])],
         'ner_tags': [ [ner_ids[t] for t in
                      train_df.iloc[i, 1].replace('[', '').replace(']', '').replace('\'', '').replace(' ', '').split(
                          ",")]
                      for i in range(train_df.shape[0]) ],
         'tokens': [train_df.iloc[i, 0].split(' ') for i in range(train_df.shape[0])]}

eval = {'id': [i for i in range(eval_df.shape[0])],
        'ner_tags': [ [ner_ids[t] for t in
                     eval_df.iloc[i, 1].replace('[', '').replace(']', '').replace('\'', '').replace(' ', '').split(
                         ",")] for i in range(eval_df.shape[0]) ],
        'tokens': [eval_df.iloc[i, 0].split(' ') for i in range(eval_df.shape[0])]}

label_list = list(ner_ids.values())

train = Dataset.from_dict(train)
eval = Dataset.from_dict(eval)

# %%
example = train[0]
tokenized_input = tokenizer(example["tokens"], is_split_into_words=True)
tokens = tokenizer.convert_ids_to_tokens(tokenized_input["input_ids"])
print(tokens)


# %%


def tokenize_and_align_labels(examples):
    tokenized_inputs = tokenizer(examples["tokens"], truncation=True, is_split_into_words=True)

    labels = []
    for i, label in enumerate(examples[f"ner_tags"]):
        word_ids = tokenized_inputs.word_ids(batch_index=i)  # Map tokens to their respective word.
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:  # Set the special tokens to -100.
            if word_idx is None:
                label_ids.append(-100)
            elif word_idx != previous_word_idx:  # Only label the first token of a given word.
                label_ids.append(label[word_idx])
            else:
                label_ids.append(-100)
            previous_word_idx = word_idx
        labels.append(label_ids)

    tokenized_inputs["labels"] = labels
    return tokenized_inputs


tokenized_train = train.map(tokenize_and_align_labels, batched=True)
tokenized_eval = eval.map(tokenize_and_align_labels, batched=True)

#%%
data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

training_args = TrainingArguments(
    output_dir="models/bert4tokens",
    evaluation_strategy=IntervalStrategy.EPOCH,
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=8,
    weight_decay=0.01,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_eval,
    tokenizer=tokenizer,
    data_collator=data_collator
)

trainer.train()

#%%

model.save_pretrained('models/bert4token')
tokenizer.save_pretrained('models/berttokenizer')

#%%


tokenizer = AutoTokenizer.from_pretrained("models/berttokenizer")
model = AutoModelForTokenClassification.from_pretrained("models/bert4token",num_labels=7)

#%%
from transformers import pipeline
token_classifier = pipeline(
    "token-classification", model=model,tokenizer=tokenizer, aggregation_strategy="simple"
)

ret = token_classifier('inoltra la mail a franco cutugno con oggetto sei risultato positivo in data diciannove ottobre')
print(ret)
#%%