import json,sys,glob,os
for f in sorted(glob.glob(sys.argv[1]+'/*.json')):
    d=json.load(open(f)); print(f"\n=== {os.path.basename(f)[:-5]}  ({d['dur']:.0f}s)")
    for s in d['segs']:
        if s['text']: print(f"{s['start']:6.1f}-{s['end']:6.1f} {s['text']}")
