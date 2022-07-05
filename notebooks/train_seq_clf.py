import pandas as pd
import torch
import numpy as np
from datasets import Dataset
from sklearn.model_selection import train_test_split
from transformers import BertTokenizerFast, BertForTokenClassification, AutoTokenizer
from transformers import DataCollatorForTokenClassification, IntervalStrategy
from transformers import DataCollatorWithPadding

from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer

# %%

tokenizer = AutoTokenizer.from_pretrained("models/berttokenizer")
model = AutoModelForSequenceClassification.from_pretrained("models/bert4token",
                                                           problem_type="multi_label_classification",
                                                           num_labels=7)

# %%

intent_ids = {"send_email": 0,
              "list_email": 1,
              "read_email": 2,
              "delete_email": 3,
              "reply_email": 4,
              "forward_email": 5,
              "close_email": 6}

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
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

training_args = TrainingArguments(
    output_dir="./results",
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
    train_dataset=train,
    eval_dataset=eval,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

trainer.train()

#%%

model.save_pretrained('models/bert4sequence')
