"""Correction d'une phrase dans la voix de Bognin (XTTS-v2, clonage à partir d'un extrait du même rush).

Usage : python xtts_fix.py <ref.wav> <sortie_prefix> "<texte corrigé>" [n_variantes]
Le modèle est sous licence Coqui CPML (non commerciale) : choix assumé par la production,
voir la note dans videos/shorts/TITRES.md.
"""
import os, sys
os.environ.setdefault("COQUI_TOS_AGREED", "1")
import torch
from TTS.api import TTS

ref, out, text = sys.argv[1], sys.argv[2], sys.argv[3]
n = int(sys.argv[4]) if len(sys.argv) > 4 else 3
torch.set_num_threads(4)
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
for i in range(n):
    torch.manual_seed(100 + i)
    tts.tts_to_file(text=text, speaker_wav=ref, language="fr", file_path=f"{out}_{i}.wav",
                    temperature=0.6, repetition_penalty=5.0, top_p=0.85, speed=1.0, split_sentences=False)
    print("ok", f"{out}_{i}.wav")
