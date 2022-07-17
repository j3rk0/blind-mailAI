# ASR dialogue system for email managing


A voice email manager ... with Neural Networks.
It use a wav2vec2 + LM for asr, google cloud tts for
voice and bert for understanding ( intent classification and token classification ).
The system is trained with syntetic data. It use rdf for dialogue
state tracking and smtp/pop3 to comunicating with email server.
the system is in italian language only

## Steps to build the AI pipeline:

you can train your own system with the following step:


#### Generate training data

1) create python 3.8 virtualenv with requirements
2) write a file in data/names.txt with some rows in the format:

   name,surname

   with random names and surnames. you must have also a google api tts
   auth key saved as data/tts_auth_key.json
3) run generate_dataset notebook. this will create a data/dataset.csv file 
   and a data/audio folder.
4) now you can safely delete data/names.txt


#### ASR fine tuning:


1) run fine tuning notebook. this will get you a models/wav2vec2 folder with torch model
2) you can now safely delete data/audio and data/hfdata folders

#### LM generation:

1) from command line cd into lib and run get_lm_corpus.sh this will get you
200 mb of data from paisa italian corpus in data/lm/corpus.txt
2) cd into lib/lm and run get_kenlm.sh to get kenlm executables
3) run build_lm.sh this will generate a lm model in models/lm/lm.arpa
4) run build_asr_with_lm notebook to generate a model in models/wav2vec2LM
5) if you run infer_asr you get the result of asr with lm. you can safely delete models/lm 
and models/wav2vec2. you can also safely delete data/hfdata folder

#### Tokens and Intent Classification

1) run train_token_clf notebook to train token classifier. this will
   get you a model/bert4token and model/berttokenizer folders with pytorch models
2) run train_seq_clf notebook to train intent classificator. this will
   get you a model/bert4sequence folder with the pytorch model
3) now you can safely delete data/dataset.csv

#### Email Module

1) buil a email.conf file in the following format:
    
   smtp_server:smtp_port

    pop3_server:pop3_port
       
    email:password

2) build a contacts.txt with evrey row in the format (one for each contact in your library)
    
    name surname:email

## Start the app
1) execute main.py
