## ASR dialogue system for email managing

### current state:

build model for ASR use finetuned on a domain-specific small dataset of
text-to-speech generated mp3 files.
as extra dependency you need ffmpeg and also check requirements from kenlm
if you want to generate the LM by yourself


#### ASR fine tuning:

1) create python 3.8 virtualenv with requirements
2) untar DATASET_NLP.tar.gz in a folder named data
3) run fine tuning notebook. this will get you a models/wav2vec2 folder with torch model

#### LM generation:

1) from command line cd into lib and run get_lm_corpus.sh this will get you
200 mb of data from paisa italian corpus in data/lm/corpus.txt
2) cd into lib/lm and run get_kenlm.sh to get kenlm executables
3) run build_lm.sh this will generate a lm model in models/lm/lm.arpa
4) run prepare_lm notebook to generate a lm processor for wav2vec2

#### NER and Intent Classification

1) generate tje dataset using the script lib/generate_dataset.py this will get you a data/ner_dataset.csv file
2) 