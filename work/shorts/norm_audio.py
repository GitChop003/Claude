"""Ramène le son d'un rendu à -14 LUFS par un gain fixe mesuré (pas de loudnorm dynamique, qui coupe la fin).
Usage : norm_audio.py <entrée.mp4> <sortie.mp4>"""
import subprocess, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from cut import lufs
src, dst = sys.argv[1:3]
g = -14.0 - lufs(src)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-c:v", "copy", "-af", f"volume={g:.2f}dB,apad=pad_dur=0.5,alimiter=limit=0.89:latency=1:level=0",
                "-shortest", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", dst], check=True)
print(f"son : gain {g:+.2f} dB -> {lufs(dst):.1f} LUFS")
