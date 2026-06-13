#!/usr/bin/env python3
"""Podcast カバー画像（正方形PNG）を生成する。"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / "cover.png"
SIZE = 1500

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\msgothic.ttc",
]


def load_font(size):
    for p in FONT_CANDIDATES:
        if pathlib.Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def vgradient(size, top, bottom):
    base = Image.new("RGB", (1, size), top)
    px = base.load()
    for y in range(size):
        t = y / (size - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return base.resize((size, size))


def centered(draw, cx, y, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text((cx - w / 2, y), text, font=font, fill=fill)


def main():
    img = vgradient(SIZE, (13, 30, 60), (8, 12, 22))
    d = ImageDraw.Draw(img)

    # アクセントの帯
    d.rectangle([0, int(SIZE * 0.60), SIZE, int(SIZE * 0.605)], fill=(31, 111, 235))

    f_small = load_font(70)
    f_big = load_font(150)
    f_mid = load_font(96)

    cx = SIZE / 2
    centered(d, cx, int(SIZE * 0.20), "MORNING", f_small, (120, 160, 230))
    centered(d, cx, int(SIZE * 0.30), "朝の", f_big, (255, 255, 255))
    centered(d, cx, int(SIZE * 0.44), "深掘りニュース", f_big, (255, 255, 255))
    centered(d, cx, int(SIZE * 0.68), "毎朝6時・話題の5本を5W1Hで", f_mid, (190, 205, 230))
    centered(d, cx, int(SIZE * 0.86), "for kota", f_small, (110, 120, 140))

    img.save(OUT, "PNG")
    print(f"cover -> {OUT}  ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
