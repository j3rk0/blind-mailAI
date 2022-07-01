#!/bin/bash
./kenlm/build/bin/lmplz -o 5 -S 40% <"../../data/lm/corpus.txt" >"../../models/lm/temp.arpa"

PYCMD=$(cat <<EOF
with open("../../models/lm/temp.arpa", "r") as read_file, open("../../models/lm/lm.arpa", "w") as write_file:
  print('starting conversion')
  has_added_eos = False
  for line in read_file:
    if not has_added_eos and "ngram 1=" in line:
      count=line.strip().split("=")[-1]
      write_file.write(line.replace(f"{count}", f"{int(count)+1}"))
    elif not has_added_eos and "<s>" in line:
      write_file.write(line)
      write_file.write(line.replace("<s>", "</s>"))
      has_added_eos = True
    else:
      write_file.write(line)
  print('ended conversion')
EOF
)

python3 -c "$PYCMD"
rm "../../models/lm/temp.arpa"
