from pathlib import Path
import argparse
import glob
import os
import codecs

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, required=True)
parser.add_argument('--output', type=str, required=True)

def main():
    args = parser.parse_args()
    for f in glob.glob(f'{args.input}/*'):
        inp = open(f, 'r', encoding='latin1')
        outp = open('{}.txt'.format(os.path.join(args.output,
                                                 Path(f).stem)), 'w')
        line = []
        lines = []
        reading = True
        while reading:
            try:
                c = inp.read(1)
                if not c:
                    break
                else:
                    if (ord(c) >= 32 and ord(c) <= 122):
                        line.append(c)
                    if c == '|':
                        line.append(c)
                    if c == '\n':
                        lines.append(line)
                        line = []
            except:
                reading = False
                
        print(f'{f} {len(lines)} lines')

        for line in lines:
            try:
                line = ''.join(line)
                line = line.rstrip()
                # line = codecs.encode(line, 'ascii')
                #line = codecs.decode(line, 'latin1', 'skip')
                outp.write(line)
                outp.write('\n')
            except:
                pass
        outp.close()
        inp.close()

if __name__ in "__main__":
    main()
