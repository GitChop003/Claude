"""Reconstruit seulement le SON d'un short déjà découpé (image inchangée) avec la chaîne son corrigée.
Mêmes îlots que cut.py, morceaux audio seuls, même mixage ; l'image de l'ancien cut.mp4 est recopiée.
Usage : reaudio.py <spec.json> <rt_dir> <rush_dir> <out_dir> [--check <référence.mp4>]"""
import json, os, subprocess, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cut


def main(spec_path, rt_dir, rush_dir, out_dir):
    spec = json.load(open(spec_path))
    pieces, inputs = [], []
    for c in spec["clips"]:
        f = glob.glob(f"{rush_dir}/*_{c['rush']}_D_MP4*.mp4")[0]
        W = cut.words_of(f"{rt_dir}/{c['rush']}.json")
        if c["rush"] not in cut.ENV: cut.ENV[c["rush"]] = cut.envelope(f)
        for isl in cut.islands(W, c["in"], c["out"], c.get("drop", []), cut.ENV[c["rush"]]):
            pieces.append((f, isl["s"], isl["e"]))
    tmp = f"{out_dir}/_apieces"; os.makedirs(tmp, exist_ok=True)
    lst, t = [], 0.0
    for k, (f, s, e) in enumerate(pieces):
        d = e - s; pf = f"{tmp}/a{k:02d}.wav"
        # même découpe audio que cut.py
        dv = d  # durée exacte : alignement identique au découpage complet (vérifié sur s2, décalage 0 ms)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.3f}", "-t", f"{d:.3f}", "-i", f, "-vn",
                        "-af", f"afade=t=in:d=0.025,afade=t=out:st={max(0, d - 0.03):.3f}:d=0.03,apad,atrim=0:{dv:.4f}",
                        "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "1", pf], check=True)
        lst.append(pf); t += d
    open(f"{tmp}/list.txt", "w").write("".join(f"file '{os.path.abspath(x)}'\n" for x in lst))
    old = json.load(open(f"{out_dir}/words.json")); T = old["dur"] + cut.TAIL
    vraw = f"{tmp}/voice.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt",
                    "-af", f"apad=pad_dur={cut.TAIL + 2},highpass=f=70,afftdn=nr=8:nf=-40,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,"
                           f"aformat=channel_layouts=stereo,atrim=0:{T:.3f}", "-ar", "48000", "-c:a", "pcm_s16le", vraw], check=True)
    g = -14.0 - cut.lufs(vraw)
    music = os.path.join(os.path.dirname(os.path.abspath(cut.__file__)), "music_bed.wav")
    mix = f"{tmp}/mix.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vraw, "-i", music, "-filter_complex",
                    f"[0:a]volume={g:.2f}dB[vx];[1:a]atrim=0:{T:.3f},asetpts=PTS-STARTPTS,aformat=channel_layouts=stereo,"
                    f"afade=t=in:d=1.2,afade=t=out:st={T - 2.2:.3f}:d=2.2[mx];"
                    f"[vx][mx]amix=inputs=2:normalize=0:duration=first,apad=pad_dur=1,alimiter=limit=0.89:latency=1:level=0,atrim=0:{T:.3f}[ao]",
                    "-map", "[ao]", "-ar", "48000", "-c:a", "pcm_s16le", mix], check=True)
    src = f"{out_dir}/cut.mp4"; dst = f"{out_dir}/cut_new.mp4"
    # image : recopiée ; ré-encodée seulement si les images clés sont trop espacées (anciens cuts s1-s4)
    kf = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-skip_frame", "nokey", "-show_entries", "frame=pts_time",
                         "-of", "csv=p=0", src], capture_output=True, text=True).stdout.split()
    kf = [float(x.strip(",")) for x in kf if x.strip(",")]
    gap = max(b - a for a, b in zip(kf, kf[1:])) if len(kf) > 1 else 99
    vopt = ["-c:v", "copy"] if gap <= 1.1 else ["-c:v", "libx264", "-crf", "16", "-preset", "medium", "-r", "30", "-g", "30", "-keyint_min", "30", "-pix_fmt", "yuv420p"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", mix, "-map", "0:v", "-map", "1:a", "-t", f"{T:.3f}", *vopt,
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", dst], check=True)
    os.replace(dst, src)
    cut.check_tail(src, old["words"], T)
    print(spec["id"], "son reconstruit", "(image recopiée)" if gap <= 1.1 else "(image ré-encodée, images clés)")


if __name__ == "__main__":
    main(*sys.argv[1:5])
