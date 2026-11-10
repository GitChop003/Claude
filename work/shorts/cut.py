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
ENV = {}
TAIL = 3.0  # fin : la dernière phrase + 3 s (CTA lisible ~1,7 s, puis carte de fin)
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


def envelope(rush_file):
    """Énergie de la voix par tranches de 10 ms (16 kHz mono) + seuil voix/silence propre au rush."""
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", rush_file, "-map", "0:a:0", "-ac", "1", "-ar", "16000",
                          "-f", "f32le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32)
    n = len(a) // 160
    rms = np.sqrt((a[:n * 160].reshape(n, 160) ** 2).mean(1) + 1e-12)
    floor, speech = np.percentile(rms, 10), np.percentile(rms, 70)
    thr = max(floor * 2.5, speech * 0.10)
    return rms, thr


def speech_end(rms, thr, t_from, t_cap):
    """Premier instant après t_from où la voix reste sous le seuil 80 ms d'affilée (fin réelle du mot)."""
    i = int(t_from * 100); cap = int(t_cap * 100); quiet = 0
    while i < min(cap, len(rms)):
        quiet = quiet + 1 if rms[i] < thr else 0
        if quiet >= 8: return (i - 7) / 100
        i += 1
    return t_cap


def speech_start(rms, thr, t_from, t_floor):
    """En remontant depuis t_from : début réel de l'attaque (voix sous le seuil 50 ms d'affilée)."""
    i = int(t_from * 100); fl = int(t_floor * 100); quiet = 0
    while i > max(fl, 0):
        quiet = quiet + 1 if rms[i] < thr else 0
        if quiet >= 5: return (i + 5) / 100
        i -= 1
    return t_floor


def tts_words(path, rt_dir):
    """Mots + horodatages d'un fichier de voix (même modèle de transcription que les rushes)."""
    import numpy as np, sherpa_onnx
    M = os.path.join(os.path.dirname(rt_dir), "models", "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8")
    r = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f"{M}/encoder.int8.onnx", decoder=f"{M}/decoder.int8.onnx",
                                                      joiner=f"{M}/joiner.int8.onnx", tokens=f"{M}/tokens.txt",
                                                      num_threads=4, model_type="nemo_transducer")
    a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                                     capture_output=True).stdout, np.float32)
    st = r.create_stream(); st.accept_waveform(16000, a); r.decode_stream(st)
    tmp = {"segs": [{"tokens": list(st.result.tokens), "ts": list(st.result.timestamps)}]}
    p = path + ".words.json"; json.dump(tmp, open(p, "w"))
    return words_of(p)


def lufs(path):
    """Loudness intégrée (LUFS) d'un fichier, mesurée par ebur128."""
    r = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(r.rsplit("I:", 1)[1].split("LUFS")[0])


def check_tail(path, words, T):
    """Garde-fou : la dernière phrase doit s'entendre et le son doit durer jusqu'à la fin (CTA + carte de fin)."""
    import numpy as np
    a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                                     capture_output=True).stdout, np.float32)
    dur = len(a) / 16000
    s, e = words[-5]["s"], words[-1]["e"]
    seg = a[int(s * 16000):int(e * 16000)]
    lvl = 20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9)
    tail = a[int((T - 2.5) * 16000):int((T - 1.0) * 16000)]
    tl = 20 * np.log10(np.sqrt((tail ** 2).mean()) + 1e-9) if len(tail) else -200
    ok = dur >= T - 0.1 and lvl > -35 and tl > -80
    print(f"  contrôle fin : son {dur:.2f}/{T:.2f} s, dernière phrase {lvl:.0f} dBFS, musique de fin {tl:.0f} dBFS -> {'OK' if ok else 'ÉCHEC'}")
    if not ok: raise SystemExit("fin de son incorrecte")


def islands(words, a, b, drops, env=None):
    ws = [w for w in words if w["s"] >= a - 0.05 and w["s"] < b
          and not any(x <= w["s"] < y for x, y in drops)
          and w["w"].lower().strip(".,!?") not in FILLERS]
    out = []
    for w in ws:
        if out and w["s"] - out[-1]["e"] <= MAX_GAP:
            out[-1]["e"] = w["e"]; out[-1]["words"].append(w)
        else:
            out.append({"s": w["s"], "e": w["e"], "words": [w]})
    if env is not None:
        # Bornes calées sur le son réel : on laisse finir la dernière syllabe (les horodatages du modèle
        # marquent le DÉBUT des mots), sans jamais mordre sur le mot suivant non retenu.
        rms, thr = env
        idx = {id(w): k for k, w in enumerate(words)}
        for isl in out:
            first, last = isl["words"][0], isl["words"][-1]
            k1, k2 = idx[id(first)], idx[id(last)]
            nxt = words[k2 + 1]["s"] - 0.04 if k2 + 1 < len(words) else last["s"] + 1.2
            prv = words[k1 - 1]["s"] + 0.25 if k1 > 0 else max(0, first["s"] - 0.4)
            e_real = speech_end(rms, thr, last["s"] + 0.12, min(nxt, last["s"] + 1.1))
            s_real = speech_start(rms, thr, first["s"], max(prv, first["s"] - 0.35))
            isl["e"] = min(nxt, max(e_real + 0.12, isl["e"] + 0.10))  # jamais plus court qu'avant
            isl["s"] = max(prv, s_real - 0.06)
        res = []
        for isl in out:
            if res and isl["s"] <= res[-1]["e"]:
                res[-1]["e"] = isl["e"]; res[-1]["words"] += isl["words"]
            else:
                res.append(dict(isl))
        return res
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
    tts_of = {}  # index du morceau → fichier de voix corrigée
    for c in spec["clips"]:
        f = glob.glob(f"{rush_dir}/*_{c['rush']}_D_MP4*.mp4")[0]
        if f not in inputs: inputs.append(f)
        if "tts" in c:
            # Phrase corrigée (voix clonée, accord de Bognin) : l'image vient du rush à partir de c["in"],
            # le son du fichier corrigé. Les mots sont retranscrits pour les sous-titres.
            tp = os.path.join(os.path.dirname(os.path.abspath(spec_path)), c["tts"])
            d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", tp],
                                     capture_output=True, text=True).stdout)
            tts_of[len(pieces)] = tp
            pieces.append((inputs.index(f), c["in"], c["in"] + d, [dict(w, s=w["s"] + c["in"], e=w["e"] + c["in"]) for w in tts_words(tp, rt_dir)]))
            continue
        W = words_of(f"{rt_dir}/{c['rush']}.json")
        if c["rush"] not in ENV: ENV[c["rush"]] = envelope(f)
        for isl in islands(W, c["in"], c["out"], c.get("drop", []), ENV[c["rush"]]):
            pieces.append((inputs.index(f), isl["s"], isl["e"], isl["words"]))
    tmp = f"{out_dir}/_pieces"; os.makedirs(tmp, exist_ok=True)
    t, out_words, cuts, lst = 0.0, [], [], []
    for k, (i, s, e, ws) in enumerate(pieces):
        d = e - s; pf = f"{tmp}/p{k:02d}.mp4"
        # chaque morceau est décodé seul (-ss avant -i) : mémoire minimale
        extra = ["-i", tts_of[k], "-map", "0:v:0", "-map", "1:a:0"] if k in tts_of else []
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.3f}", "-t", f"{d:.3f}", "-i", inputs[i], *extra,
                        "-vf", f"{grade},fps=30", "-af", f"afade=t=in:d=0.025,afade=t=out:st={max(0,d-0.03):.3f}:d=0.03",
                        "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "1",
                        "-threads", "2", pf.replace(".mp4", ".mov")], check=True)
        lst.append(pf.replace(".mp4", ".mov"))
        for w in ws:
            out_words.append({"w": w["w"], "s": round(t + w["s"] - s, 3), "e": round(t + w["e"] - s, 3)})
        t += d; cuts.append(round(t, 3))
    open(f"{tmp}/list.txt", "w").write("".join(f"file '{os.path.abspath(x)}'\n" for x in lst))
    T = t + TAIL
    music = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music_bed.wav")  # nappe originale à -38 LUFS
    # Son en 3 étapes, SANS loudnorm dynamique : son tampon de 3 s avalait la fin du mixage
    # (dernière phrase muette sur s1-s4, plus de musique sous le CTA sur tous les shorts).
    vraw = f"{tmp}/voice.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt", "-vn",
                    "-af", f"apad=pad_dur={TAIL + 2},highpass=f=70,afftdn=nr=8:nf=-40,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,"
                           f"aformat=channel_layouts=stereo,atrim=0:{T:.3f}",
                    "-ar", "48000", "-c:a", "pcm_s16le", vraw], check=True)
    g = -14.0 - lufs(vraw)  # gain fixe : la voix seule à -14 LUFS
    mix = f"{tmp}/mix.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vraw, "-i", music, "-filter_complex",
                    f"[0:a]volume={g:.2f}dB[vx];[1:a]atrim=0:{T:.3f},asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo,"
                    f"afade=t=in:d=1.2,afade=t=out:st={T-2.2:.3f}:d=2.2[mx];"
                    f"[vx][mx]amix=inputs=2:normalize=0:duration=first,apad=pad_dur=1,alimiter=limit=0.89:latency=1,atrim=0:{T:.3f}[ao]",
                    "-map", "[ao]", "-ar", "48000", "-c:a", "pcm_s16le", mix], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt", "-i", mix,
                    "-filter_complex", f"[0:v]tpad=stop_mode=clone:stop_duration={TAIL}[vo]", "-map", "[vo]", "-map", "1:a", "-t", f"{T:.3f}",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-r", "30", "-g", "30", "-keyint_min", "30", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-threads", "3", f"{out_dir}/cut.mp4"], check=True)
    check_tail(f"{out_dir}/cut.mp4", out_words, T)
    n = len(pieces)
    json.dump({"dur": round(t, 3), "tail": TAIL, "cuts": cuts, "words": out_words}, open(f"{out_dir}/words.json", "w"), ensure_ascii=False, indent=0)
    print(spec["id"], "durée", round(t, 1), "s,", n, "morceaux")


if __name__ == "__main__":
    main(*sys.argv[1:6])
