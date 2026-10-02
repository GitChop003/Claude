import sys, json, numpy as np, soundfile as sf, sherpa_onnx
M = sys.argv[1]; wav = sys.argv[2]; out = sys.argv[3]
P = f"{M}/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"
rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=f"{P}/encoder.int8.onnx", decoder=f"{P}/decoder.int8.onnx",
    joiner=f"{P}/joiner.int8.onnx", tokens=f"{P}/tokens.txt",
    model_type="nemo_transducer", num_threads=4)
audio, sr = sf.read(wav, dtype="float32"); assert sr == 16000
cfg = sherpa_onnx.VadModelConfig()
cfg.silero_vad.model = f"{M}/silero_vad.onnx"
cfg.silero_vad.min_silence_duration = 0.25
cfg.silero_vad.min_speech_duration = 0.15
cfg.silero_vad.max_speech_duration = 25
cfg.sample_rate = 16000
vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=600)
segs = []
w = 512
for i in range(0, len(audio), w):
    vad.accept_waveform(audio[i:i+w])
    while not vad.empty():
        segs.append((vad.front.start, np.array(vad.front.samples))); vad.pop()
vad.flush()
while not vad.empty():
    segs.append((vad.front.start, np.array(vad.front.samples))); vad.pop()
res = []
for k, (start, s) in enumerate(segs):
    st = rec.create_stream(); st.accept_waveform(16000, s); rec.decode_stream(st)
    r = st.result
    t0 = start / 16000
    toks = [{"t": tok, "s": round(t0 + ts, 3)} for tok, ts in zip(r.tokens, r.timestamps)]
    durs = list(getattr(r, "durations", []) or [])
    for j, d in enumerate(durs[:len(toks)]): toks[j]["d"] = round(d, 3)
    res.append({"start": round(t0, 3), "end": round(t0 + len(s) / 16000, 3), "text": r.text, "tokens": toks})
    print(f"[{t0:7.2f}-{t0+len(s)/16000:7.2f}] {r.text}", flush=True)
json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
