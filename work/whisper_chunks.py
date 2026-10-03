"""Re-run Whisper (fr) on short chunks cut at Parakeet word gaps, for tighter caption alignment."""
import sys, json, soundfile as sf, sherpa_onnx
M, wav, out = sys.argv[1:4]
raw = json.load(open("raw_words.json"))
chunks, cur = [], [raw[0]]
for w in raw[1:]:
    if w["start"] - cur[-1]["end"] > 0.30 or w["end"] - cur[0]["start"] > 10: chunks.append(cur); cur = [w]
    else: cur.append(w)
chunks.append(cur)
P = f"{M}/sherpa-onnx-whisper-turbo"
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f"{P}/turbo-encoder.int8.onnx", decoder=f"{P}/turbo-decoder.int8.onnx",
    tokens=f"{P}/turbo-tokens.txt", language="fr", task="transcribe", num_threads=4)
audio, sr = sf.read(wav, dtype="float32"); res = []
for c in chunks:
    a0, a1 = max(0, c[0]["start"] - 0.15), c[-1]["end"] + 0.2
    st = rec.create_stream(); st.accept_waveform(sr, audio[int(a0 * sr):int(a1 * sr)]); rec.decode_stream(st)
    res.append({"start": c[0]["start"], "end": c[-1]["end"], "text": st.result.text.strip(), "pw": c})
    print(f"[{a0:7.2f}] {st.result.text.strip()}", flush=True)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=0)
