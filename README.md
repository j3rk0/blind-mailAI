# ASR dialogue system for email managing

## Steps to build the AI pipeline:

#### Generate training data

1) create python 3.8 virtualenv with requirements
2) write a file in data/names.txt with some rows in the format:

   name,surname

   with random names and surnames. you must have also a google api tts
   auth key saved as data/tts_auth_key.json
3) run generate_dataset notebook. this will create a data/dataset.csv file 
   and a data/audio folder.


#### ASR fine tuning:


1) run fine tuning notebook. this will get you a models/wav2vec2 folder with torch model

#### LM generation:

1) from command line cd into lib and run get_lm_corpus.sh this will get you
200 mb of data from paisa italian corpus in data/lm/corpus.txt
2) cd into lib/lm and run get_kenlm.sh to get kenlm executables
3) run build_lm.sh this will generate a lm model in models/lm/lm.arpa
4) run build_asr_with_lm notebook to generate a model in models/wav2vec2LM
5) if you run infer_asr you get the result of asr with lm. you can safely delete models/lm 
and models/wav2vec2

#### NER and Intent Classification

1) run train_token_clf notebook to train token classifier
2) run train_seq_clf notebook to train intent classificator

#### Email Module

1) buil a email.conf file in the following format:
    
   smtp_server:smtp_port

    pop3_server:pop3_port
       
    email:password

2) build a contacts.txt with evrey row in the format (one for each contact in your library)
    
    name surname:email

## Start the app
1) execute main.py
