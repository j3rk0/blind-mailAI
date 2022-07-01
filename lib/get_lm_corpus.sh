#!/bin/bash
wget https://clarin.eurac.edu/repository/xmlui/bitstream/handle/20.500.12124/3/paisa.raw.utf8.gz
gzip -d paisa.raw.utf8.gz
split --bytes=200M paisa.raw.utf8
mv xaa ../data/lm/corpus.txt
rm x*
rm paisa.*
