"""Mesure la position du visage (coordonnées 1080×1920) sur un montage : une détection toutes les 0,5 s.
Sortie : <assets>/faces.json = [[t, haut, bas], ...] ; affiche le bas maximal (le plus bas où descend le visage)."""
import sys, json, cv2, numpy as np
path = sys.argv[1]
cap = cv2.VideoCapture(f"{path}/cut.mp4")
fps = cap.get(cv2.CAP_PROP_FPS) or 30
cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
out, i, step = [], 0, int(fps / 2)
while True:
    ok = cap.grab()
    if not ok: break
    if i % step == 0:
        ok, fr = cap.retrieve()
        g = cv2.cvtColor(cv2.resize(fr, (540, 960)), cv2.COLOR_BGR2GRAY)
        f = cas.detectMultiScale(g, 1.1, 6, minSize=(90, 90))
        if len(f):
            x, y, w, h = max(f, key=lambda r: r[2] * r[3])
            # le cadre Haar s'arrête au menton environ : on ajoute 12 % pour la barbe et le cou
            out.append([round(i / fps, 2), int(y * 2), int((y + h * 1.12) * 2)])
    i += 1
json.dump(out, open(f"{path}/faces.json", "w"))
b = [o[2] for o in out]
print(path.split("/")[-2], "détections", len(out), "| bas du visage : médiane", int(np.median(b)), "p95", int(np.percentile(b, 95)), "max", max(b))
