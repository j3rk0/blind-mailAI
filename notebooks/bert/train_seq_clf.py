import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from sklearn.model_selection import train_test_split
from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer
from transformers import AutoTokenizer
from transformers import DataCollatorWithPadding
from transformers import IntervalStrategy

# %%

tokenizer = AutoTokenizer.from_pretrained("models/berttokenizer")
model = AutoModelForSequenceClassification.from_pretrained("models/bert4token",
                                                           problem_type="multi_label_classification",
                                                           num_labels=7)

# %%

intent_labels = {"LABEL_0": "send_email",
                 "LABEL_1": "list_email",
                 "LABEL_3": "read_email",
                 "LABEL_4": "delete_email",
                 "LABEL_5": "reply_email",
                 "LABEL_6": "forward_email",
                 "LABEL_7": "close_email"}

#%%

inputs = tokenizer('ciao pasquale come va', return_tensors="pt")
with torch.no_grad():
    logits = model(**inputs).logits

predicted_class_id = logits.argmax().item()
print(model.config.id2label[predicted_class_id])

# %%

df = pd.read_csv('data/dataset.csv', index_col=0)

train_df, eval_df = train_test_split(df, train_size=.8)
# %%
train = {'input_ids': [tokenizer(train_df.iloc[i, 0], truncation=True)['input_ids'] for i in range(train_df.shape[0])],
         'attention_mask': [np.array(tokenizer(train_df.iloc[i, 0], truncation=True)['attention_mask']) for i in
                            range(train_df.shape[0])],
         'label': [[1. if j == train_df.iloc[i, 2] else 0. for j in range(7)] for i in range(train_df.shape[0])]}

eval = {'input_ids': [tokenizer(eval_df.iloc[i, 0], truncation=True)['input_ids'] for i in range(eval_df.shape[0])],
        'attention_mask': [np.array(tokenizer(eval_df.iloc[i, 0], truncation=True)['attention_mask']) for i in
                           range(eval_df.shape[0])],
        'label': [[1. if j == eval_df.iloc[i, 2] else 0. for j in range(7)] for i in range(eval_df.shape[0])]}

train = Dataset.from_dict(train)
eval = Dataset.from_dict(eval)

# %%
from datasets import load_metric

metric = load_metric("accuracy")

test = None


def compute_metrics(p):
    preds = np.argmax(p.predictions, axis=1)
    truth = np.argmax(p.label_ids, axis=1)
    return {"accuracy": (preds == truth).mean()}


# %%
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy=IntervalStrategy.EPOCH,
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train,
    eval_dataset=eval,
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics
)

trainer.train()

# %%
from transformers import pipeline

pipe = pipeline('text-classification', model=model, tokenizer=tokenizer)
pred = pipe('rispondi a fulvio camera')[0]

print(intent_labels[pred['label']])

# %%
model.save_pretrained('models/bert4sequence')
