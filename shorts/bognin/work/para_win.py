"""Re-decode short windows with Parakeet (token times).  para_win.py [--save] A-B [A-B ...]
--save stores the words in words_patch.json; short.py uses them instead of the full transcript there."""
import json, os, subprocess, sys, numpy as np, sherpa_onnx
SAVE = "--save" in sys.argv
PATCH = "/home/claude/claude/shorts/bognin/work/words_patch.json"
patch = json.load(open(PATCH)) if os.path.exists(PATCH) else []
M = "/tmp/claude-0/-home-claude/3103370c-3a96-56b2-b40e-7458c05b9768/scratchpad/models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"
rec = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f"{M}/encoder.int8.onnx", decoder=f"{M}/decoder.int8.onnx",
        joiner=f"{M}/joiner.int8.onnx", tokens=f"{M}/tokens.txt", model_type="nemo_transducer", num_threads=2)
SRC = "/tmp/claude-0/-home-claude/3103370c-3a96-56b2-b40e-7458c05b9768/scratchpad/src/source.mp4"
for w in [x for x in sys.argv[1:] if x != "--save"]:
    a, b = map(float, w.split("-"))
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-to", str(b), "-i", SRC, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    # VAD inside the window so token times are anchored on real speech onsets (padding skews TDT timestamps)
    cfg = sherpa_onnx.VadModelConfig()
    cfg.silero_vad.model = "/tmp/claude-0/-home-claude/3103370c-3a96-56b2-b40e-7458c05b9768/scratchpad/models/silero_vad.onnx"
    cfg.silero_vad.min_silence_duration = 0.25; cfg.silero_vad.min_speech_duration = 0.1; cfg.silero_vad.max_speech_duration = 25
    cfg.sample_rate = 16000
    vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=120)
    segs = []
    for i in range(0, len(x), 512):
        vad.accept_waveform(x[i:i + 512])
        while not vad.empty():
            segs.append((vad.front.start, np.array(vad.front.samples))); vad.pop()
    vad.flush()
    while not vad.empty():
        segs.append((vad.front.start, np.array(vad.front.samples))); vad.pop()
    words, cur, text = [], None, []
    for st0, smp in segs:
        s = rec.create_stream(); s.accept_waveform(16000, smp); rec.decode_stream(s)
        r = s.result; text.append(r.text); cur = None
        for t, ts in zip(r.tokens, r.timestamps):
            tt = a + st0 / 16000 + ts
            if t.startswith(" ") or cur is None:
                cur = [round(tt, 2), t.strip()]; words.append(cur)
            else:
                cur[1] += t
    print(f"{a}-{b}: {' | '.join(text)}\n   " + "  ".join(f"{t:.2f} {x}" for t, x in words))
    if SAVE:
        ws = [{"text": x, "start": t, "end": round(words[k + 1][0] if k + 1 < len(words) else min(b, t + 0.45), 2)} for k, (t, x) in enumerate(words)]
        patch = [p for p in patch if not (p["a"] < b and a < p["b"])] + [{"a": a, "b": b, "words": ws}]
if SAVE:
    json.dump(sorted(patch, key=lambda p: p["a"]), open(PATCH, "w"), ensure_ascii=False, indent=0)
    print("saved", len(patch), "patches")
