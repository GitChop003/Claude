"""Re-transcribe an edited voice track in fixed windows to verify no word was clipped.  check_voice.py VOICE.wav [win=6]"""
import subprocess, sys, numpy as np, sherpa_onnx
M = "/tmp/claude-0/-home-claude/3103370c-3a96-56b2-b40e-7458c05b9768/scratchpad/models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"
rec = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f"{M}/encoder.int8.onnx", decoder=f"{M}/decoder.int8.onnx",
        joiner=f"{M}/joiner.int8.onnx", tokens=f"{M}/tokens.txt", model_type="nemo_transducer", num_threads=2)
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
win = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
t = 0.0
while t < len(x) / 16000:
    a, b = int(t * 16000), int(min(len(x), (t + win + 0.6) * 16000))
    s = rec.create_stream(); s.accept_waveform(16000, np.concatenate([np.zeros(4000, np.float32), x[a:b], np.zeros(4000, np.float32)])); rec.decode_stream(s)
    print(f"{t:6.1f}: {s.result.text}", flush=True)
    t += win
