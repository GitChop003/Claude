import json, sys, subprocess
name, src, out = sys.argv[1:4]
edl = json.load(open(f"{name}.edl.json")); segs = edl["segments"]
args = ["ffmpeg", "-v", "error", "-y"]
for s, e in segs: args += ["-ss", f"{s:.3f}", "-t", f"{e - s:.3f}", "-i", src]
f = []
for i, (s, e) in enumerate(segs):
    d = e - s
    f.append(f"[{i}:v:0]scale=1920:1080:flags=lanczos,fps=30000/1001,setpts=PTS-STARTPTS,format=yuv420p[v{i}]")
    f.append(f"[{i}:a:0]aresample=48000,asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={d - 0.02:.3f}:d=0.02[a{i}]")
f.append("".join(f"[v{i}][a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=1[v][a]")
f.append("[a]loudnorm=I=-16:TP=-1.5:LRA=11[an]")
args += ["-filter_complex", ";".join(f), "-map", "[v]", "-map", "[an]", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-g", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out]
subprocess.run(args, check=True)
