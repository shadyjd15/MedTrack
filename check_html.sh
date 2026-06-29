#!/bin/bash
# Extract inline <script> blocks from an HTML file and syntax-check each with node.
f="$1"
python3 -c "
import re, sys
with open('$f') as fh:
    content = fh.read()
scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
for i, s in enumerate(scripts):
    with open(f'/tmp/_htmlcheck_{i}.js', 'w') as out:
        out.write(s)
print(len(scripts))
" > /tmp/_count.txt
count=$(cat /tmp/_count.txt)
ok=1
for i in $(seq 0 $((count-1))); do
  if ! node --check /tmp/_htmlcheck_$i.js 2>/tmp/_err.txt; then
    echo "SYNTAX ERROR in $f script block $i:"
    cat /tmp/_err.txt
    ok=0
  fi
done
if [ "$ok" = "1" ]; then echo "$f: all $count inline script(s) OK"; fi
