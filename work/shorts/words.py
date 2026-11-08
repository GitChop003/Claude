import sys,json
sys.path.insert(0,'.')
from cut import words_of
W=words_of(sys.argv[1]); a=float(sys.argv[2]) if len(sys.argv)>2 else 0; b=float(sys.argv[3]) if len(sys.argv)>3 else 1e9
print(' '.join(f"{w['w']}@{w['s']:.2f}" for w in W if a<=w['s']<b))
