#!/usr/bin/env python3
"""Render Lab 2 captured command output (headless logs) as terminal-style PNGs.

Windows-style window chrome, Ubuntu palette body. Content = real captured logs.
"""
from PIL import Image, ImageDraw, ImageFont
import os

LOGS = "/mnt/c/Users/Abhinav/DevOps & Automation Lab/Lab2-Meenakshi/logs"
OUT = "/mnt/c/Users/Abhinav/DevOps & Automation Lab/Lab2-Meenakshi/screenshots"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FS = 13
f_reg = ImageFont.truetype(FONT, FS)
f_bold = ImageFont.truetype(FONT_B, FS)
cw = f_reg.getbbox("M")[2] - f_reg.getbbox("M")[0]
LH = FS + 5
PAD = 14
BAR = 34
GREEN = (52, 199, 89)
WHITE = (255, 255, 255)
TITLE_COL = (60, 60, 60)


def fold(line, limit=88):
    out = []
    while len(line) > limit:
        cut = line.rfind(" ", 40, limit)
        if cut < 40:
            cut = limit
        out.append(line[:cut] + " \\")
        line = "      " + line[cut:].lstrip()
    out.append(line)
    return out


def render(name, title, text):
    lines = []
    for raw in text.rstrip("\n").split("\n"):
        lines.extend(fold(raw))
    cols = max((len(l) for l in lines), default=1)
    w = cols * cw + PAD * 2
    h = BAR + len(lines) * LH + PAD * 2
    img = Image.new("RGB", (w, h), (48, 10, 36))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, BAR], fill=(204, 204, 204))
    tw = d.textlength(title, font=f_reg)
    d.text(((w - tw) / 2, (BAR - FS) / 2 - 2), title, font=f_reg, fill=TITLE_COL)
    cy = BAR / 2
    d.line([w - 74, cy, w - 62, cy], fill=TITLE_COL, width=2)
    d.rectangle([w - 48, cy - 6, w - 36, cy + 6], outline=TITLE_COL, width=2)
    d.line([w - 26, cy - 6, w - 14, cy + 6], fill=TITLE_COL, width=2)
    d.line([w - 26, cy + 6, w - 14, cy - 6], fill=TITLE_COL, width=2)
    d.line([0, BAR, w, BAR], fill=(160, 160, 160), width=1)
    y = BAR + PAD
    for ln in lines:
        if "meenakshi@ubuntu" in ln:
            i = ln.find("$")
            if 0 < i < 60:
                d.text((PAD, y), ln[: i + 1], font=f_bold, fill=GREEN)
                d.text((PAD + (i + 1) * cw, y), ln[i + 1:], font=f_reg, fill=WHITE)
                y += LH
                continue
        if ln.startswith("==="):
            d.text((PAD, y), ln, font=f_bold, fill=WHITE)
        else:
            d.text((PAD, y), ln, font=f_reg, fill=WHITE)
        y += LH
    img.save(os.path.join(OUT, name))
    print(name, img.size)


def log(path, first=None, last=None):
    lines = open(os.path.join(LOGS, path), errors="replace").read().rstrip("\n").split("\n")
    sel = lines[first:last] if first is not None else (lines[last:] if last else lines)
    return "\n".join(sel)


# Q1
render("r2-q1-build.png", "meenakshi@ubuntu: ~/ensp461-lab2 (docker build)",
       log("q1-image-build.txt", last=-14))
render("r2-q1-run.png", "meenakshi@ubuntu: ~/ensp461-lab2 (docker run)",
       log("q1-run-behavior.txt", last=-8))
render("r2-q1-layers.png", "meenakshi@ubuntu: ~/ensp461-lab2 (docker history)",
       log("q1-image-layers.txt", last=-9))
# Q2
render("r2-q2-manage.png", "meenakshi@ubuntu: ~/ensp461-lab2 (container lifecycle)",
       log("q2-manage-registry.txt", first=0, last=34))
render("r2-q2-registry.png", "meenakshi@ubuntu: ~/ensp461-lab2 (docker push)",
       log("q2-manage-registry.txt", first=34))
render("r2-q2-compose.png", "meenakshi@ubuntu: ~/ensp461-lab2 (docker compose)",
       log("q2-compose.txt", first=1, last=-3))
# Q3
render("r2-q3-layer-loss.png", "meenakshi@ubuntu: ~/ensp461-lab2 (container layer)",
       log("q3-storage.txt", first=1, last=24))
render("r2-q3-volume-bindmount.png", "meenakshi@ubuntu: ~/ensp461-lab2 (volume + bind mount)",
       log("q3-storage.txt", first=25, last=-12))
render("r2-q3-bindmount-write.png", "meenakshi@ubuntu: ~/ensp461-lab2 (bind mount)",
       log("q3-storage.txt", first=-11))
# Q4
render("r2-q4-network.png", "meenakshi@ubuntu: ~/ensp461-lab2 (docker network)",
       log("q4-network.txt", first=1, last=-2))
# Q5
render("r2-q5-deploy.png", "meenakshi@ubuntu: ~/ensp461-lab2 (kubectl apply)",
       log("q5-deploy.txt", first=1))
render("r2-q5-verify.png", "meenakshi@ubuntu: ~/ensp461-lab2 (kubectl get pods)",
       log("q5-verify.txt", first=1, last=-5))
# Q6
render("r2-q6-rolling-update.png", "meenakshi@ubuntu: ~/ensp461-lab2 (kubectl set image)",
       log("q6-rolling-update.txt", first=1, last=-10))
render("r2-q6-scaling.png", "meenakshi@ubuntu: ~/ensp461-lab2 (kubectl scale)",
       log("q6-scaling.txt", first=8, last=-14))
# Q7
render("r2-q7-cd-success.png", "meenakshi@ubuntu: ~/lab2-cd (Jenkins console)",
       log("q7-cd-build3.txt", last=-12))
render("r2-q7-cd-auto.png", "meenakshi@ubuntu: ~/lab2-cd (poll-triggered build #4)",
       log("q7-cd-build4-auto.txt", first=0, last=2)
       + "\n[... git checkout of the new commit c6ab5c6 ...]\n"
       + log("q7-cd-build4-auto.txt", first=58, last=-4))
print("done")
