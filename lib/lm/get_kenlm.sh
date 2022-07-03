#!/bin/bash
wget -O - https://kheafield.com/code/kenlm.tar.gz |tar xz
mkdir kenlm/build
cd kenlm/build
cmake ..
make -j2
cd ..
source ../../../venv/bin/activate
pip install -e .