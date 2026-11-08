"""Découpe « juste milieu » d'un short à partir des transcriptions mot à mot.

Entrée : spec JSON  {"id", "clips":[{"rush":"0787","in":12.3,"out":25.0,"drop":[[a,b],...]}...]}
- Les rushes contiennent souvent plusieurs prises ou plusieurs idées : chaque clip
  vise une plage précise (in/out) d'un rush, jamais le fichier entier.
- Pauses : on garde 0,10 s avant le premier mot et 0,16 s après le dernier mot de
  chaque îlot de parole ; une pause > 0,45 s est raccourcie (coupe), une pause plus
  courte est conservée telle quelle. Résultat : ni coupe sèche, ni rythme mou.
- Les « euh / heu / hum » isolés sont retirés.
Sortie : <out>/cut.mp4 (1080×1920, étalonné, voix -14 LUFS) + <out>/words.json (temps de sortie).
"""
import json, os, subprocess, sys, glob

PAD_IN, PAD_OUT, MAX_GAP = 0.10, 0.16, 0.45
FILLERS = {"euh", "heu", "hum", "hmm", "bah", "euh,", "heu,"}


def words_of(rt_json):
    d = json.load(open(rt_json))
    W = []
    for s in d["segs"]:
        toks, ts = s["tokens"], s["ts"]
        cur = None
        for i, (t, tt) in enumerate(zip(toks, ts)):
            if cur is None or t.startswith(" ") or t.startswith("▁"):
                if cur: W.append(cur)
                cur = {"w": t.strip(" ▁"), "s": tt, "e": None}
            else:
                cur["w"] += t
        if cur: W.append(cur)
        # fin de mot = début du mot suivant (borné), dernier mot = fin du segment
    for i, w in enumerate(W):
        nxt = W[i + 1]["s"] if i + 1 < len(W) else w["s"] + 0.5
        w["e"] = min(nxt, w["s"] + 0.7)
    return [w for w in W if w["w"]]


def islands(words, a, b, drops):
    ws = [w for w in words if w["s"] >= a - 0.05 and w["s"] < b
          and not any(x <= w["s"] < y for x, y in drops)
          and w["w"].lower().strip(".,!?") not in FILLERS]
    out = []
    for w in ws:
        if out and w["s"] - out[-1]["e"] <= MAX_GAP:
            out[-1]["e"] = w["e"]; out[-1]["words"].append(w)
        else:
            out.append({"s": w["s"], "e": w["e"], "words": [w]})
    res = []
    for isl in out:
        s = max(a, isl["s"] - PAD_IN); e = min(b, isl["e"] + PAD_OUT)
        if res and s <= res[-1]["e"]:
            res[-1]["e"] = e; res[-1]["words"] += isl["words"]
        else:
            res.append({"s": s, "e": e, "words": isl["words"]})
    return res


def main(spec_path, rt_dir, rush_dir, out_dir, grade):
    spec = json.load(open(spec_path)); os.makedirs(out_dir, exist_ok=True)
    pieces = []  # (input_index, s, e, words)
    inputs = []
    for c in spec["clips"]:
        f = glob.glob(f"{rush_dir}/*_{c['rush']}_D_MP4*.mp4")[0]
        if f not in inputs: inputs.append(f)
        W = words_of(f"{rt_dir}/{c['rush']}.json")
        for isl in islands(W, c["in"], c["out"], c.get("drop", [])):
            pieces.append((inputs.index(f), isl["s"], isl["e"], isl["words"]))
    tmp = f"{out_dir}/_pieces"; os.makedirs(tmp, exist_ok=True)
    t, out_words, cuts, lst = 0.0, [], [], []
    for k, (i, s, e, ws) in enumerate(pieces):
        d = e - s; pf = f"{tmp}/p{k:02d}.mp4"
        # chaque morceau est décodé seul (-ss avant -i) : mémoire minimale
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.3f}", "-t", f"{d:.3f}", "-i", inputs[i],
                        "-vf", f"{grade},fps=30", "-af", f"afade=t=in:d=0.025,afade=t=out:st={max(0,d-0.03):.3f}:d=0.03",
                        "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-ar", "48000",
                        "-threads", "2", pf.replace(".mp4", ".mov")], check=True)
        lst.append(pf.replace(".mp4", ".mov"))
        for w in ws:
            out_words.append({"w": w["w"], "s": round(t + w["s"] - s, 3), "e": round(t + w["e"] - s, 3)})
        t += d; cuts.append(round(t, 3))
    open(f"{tmp}/list.txt", "w").write("".join(f"file '{os.path.abspath(x)}'\n" for x in lst))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt",
                    "-vf", "tpad=stop_mode=clone:stop_duration=1.4",
                    "-af", "apad=pad_dur=1.4,highpass=f=70,afftdn=nr=8:nf=-40,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,loudnorm=I=-14:TP=-1.5:LRA=9",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-movflags", "+faststart", "-threads", "3", f"{out_dir}/cut.mp4"], check=True)
    n = len(pieces)
    json.dump({"dur": round(t, 3), "cuts": cuts, "words": out_words}, open(f"{out_dir}/words.json", "w"), ensure_ascii=False, indent=0)
    print(spec["id"], "durée", round(t, 1), "s,", n, "morceaux")


if __name__ == "__main__":
    main(*sys.argv[1:6])
