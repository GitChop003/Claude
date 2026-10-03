import json, soundfile as sf, sherpa_onnx
M = "/tmp/claude-0/-home-user-Claude/52534eb1-8e3a-5e03-8a7b-4b8d05e1408f/scratchpad/models"
P = f"{M}/sherpa-onnx-whisper-turbo"
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f"{P}/turbo-encoder.int8.onnx", decoder=f"{P}/turbo-decoder.int8.onnx",
    tokens=f"{P}/turbo-tokens.txt", language="fr", task="transcribe", num_threads=4)
audio, sr = sf.read("../media/audio16k.wav", dtype="float32")
W = json.load(open("whisper.json")); raw = json.load(open("raw_words.json"))
new = []
for s in W:
    if s["end"] - s["start"] <= 29.5: new.append(s); continue
    ws = [w for w in raw if s["start"] <= w["start"] < s["end"]]
    mid = (s["start"] + s["end"]) / 2
    gaps = [(ws[i + 1]["start"] - ws[i]["end"], i) for i in range(len(ws) - 1) if abs(ws[i]["end"] - mid) < 8]
    i = max(gaps)[1]; cut = (ws[i]["end"] + ws[i + 1]["start"]) / 2
    for a, b in ((s["start"], cut), (cut, s["end"])):
        st = rec.create_stream(); st.accept_waveform(sr, audio[int(a * sr):int(b * sr)]); rec.decode_stream(st)
        new.append({"start": a, "end": b, "text": st.result.text.strip()}); print(f"[{a:.2f}-{b:.2f}] {st.result.text.strip()}")
json.dump(new, open("whisper_seg.json", "w"), ensure_ascii=False, indent=1)
