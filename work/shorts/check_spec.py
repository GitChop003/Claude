"""Vérifie une spec sans les vidéos : texte final des sous-titres + chaque ancrage (temps source, occurrence)."""
import json, sys, re
sys.path.insert(0, '.')
from cut import words_of, islands
def norm(w): return re.sub(r"[^\wÀ-ÿ'-]", "", w.lower())
rt = sys.argv[1]
for k in sys.argv[2:]:
    sp = json.load(open(f'specs/{k}.json')); W = []
    for c in sp['clips']:
        ws = words_of(f"{rt}/{c['rush']}.json")
        for isl in islands(ws, c['in'], c['out'], c.get('drop', [])):
            W += [dict(w, rush=c['rush']) for w in isl['words']]
    rep = sp.get('replace', {})
    for w in W:
        if w['w'] in rep: w['w'] = rep[w['w']]
    for word, n, new in sp.get('replace_n', []):
        for w in W:
            if w['w'] == word:
                n -= 1
                if n == 0: w['w'] = new; break
    W = [w for w in W if w['w'].strip()]
    def at(x):
        n = x.get('n', 1); ex = [w for w in W if w['w'] == x['word']]
        if len(ex) >= n: return f"{ex[n-1]['rush']}@{ex[n-1]['s']:.1f}"
        m = [w for w in W if norm(w['w']) == norm(x['word'])]
        return f"{m[n-1]['rush']}@{m[n-1]['s']:.1f}(norm)" if len(m) >= n else 'INTROUVABLE'
    print(f"\n== {k} « {sp['title']} »\n" + ' '.join(w['w'] for w in W))
    for key in ['ui', 'lists', 'tags', 'flash']:
        for c in sp.get(key, []):
            print(f"  {key:6} {c.get('t2', c.get('title', c.get('text', c.get('a', ''))))[:30]:32} {at(c['t'])}" + (f"  → jusqu'à {at(c['until'])}" if 'until' in c else ''))
            for it in c.get('items', []): print(f"     · {it['text'][:28]:30} {at(it['at'])}")
    for key in ['method', 'choc', 'reveal']:
        if sp.get(key): v = sp[key]; print(f"  {key:6} {'':32} {at(v.get('t', v.get('at', v)))}")
    for n, v in sp.get('inserts', {}).items(): print(f"  insert{n} {'':31} {at(v[0])}")
