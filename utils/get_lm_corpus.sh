#!/bin/bash
wget https://clarin.eurac.edu/repository/xmlui/bitstream/handle/20.500.12124/3/paisa.raw.utf8.gz
gzip -d paisa.raw.utf8.gz
sed -i'' -E 's/<[^<]+>//g' paisa.raw.utf8
split --bytes=200M paisa.raw.utf8
mv xab ../data/lm/corpus.txt
rm x*
rm paisa.*
