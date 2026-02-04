'''
Loads changes from the changelog for the given version.
'''

import sys

changelog = sys.argv[1].strip()
version = sys.argv[2].lower().strip().strip('v')
output = ''
in_block = False

with open(changelog, encoding='utf-8', mode='r') as f:
    while line := f.readline():
        if line.startswith('## '):
            in_block = version in line
        elif in_block:
            print(line.strip())
