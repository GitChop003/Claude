import sys, json, soundfile as sf, sherpa_onnx
M, wav, segf, out = sys.argv[1:5]
P = f"{M}/sherpa-onnx-whisper-turbo"
rec = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=f"{P}/turbo-encoder.int8.onnx", decoder=f"{P}/turbo-decoder.int8.onnx",
    tokens=f"{P}/turbo-tokens.txt", language="fr", task="transcribe", num_threads=4)
audio, sr = sf.read(wav, dtype="float32")
segs = json.load(open(segf)); res = []
for s in segs:
    a = audio[int(s["start"]*sr):int(s["end"]*sr)]
    st = rec.create_stream(); st.accept_waveform(sr, a); rec.decode_stream(st)
    r = st.result
    res.append({"start": s["start"], "end": s["end"], "text": r.text.strip(), "ts": list(r.timestamps)[:3]})
    print(f"[{s['start']:7.2f}-{s['end']:7.2f}] {r.text.strip()}", flush=True)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
