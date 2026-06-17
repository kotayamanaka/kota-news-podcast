#!/usr/bin/env python3
"""Podcast カバー画像（正方形PNG）を生成する。

usage:
  python make_cover.py            # 朝の深掘りニュース（cover-v2.png / cover.png）
  python make_cover.py katareru   # 語れるラジオ（katareru-cover.png）
"""
import sys
import pathlib
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = pathlib.Path(__file__).resolve().parents[1]
OUTS = [REPO / "cover-v2.png", REPO / "cover.png"]
SIZE = 3000

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\msgothic.ttc",
]


def load_font(size, bold=True):
    candidates = FONT_CANDIDATES if bold else [
        r"C:\Windows\Fonts\BIZ-UDGothicR.ttc",
        r"C:\Windows\Fonts\YuGothM.ttc",
        r"C:\Windows\Fonts\meiryo.ttc",
    ]
    for p in candidates:
        if pathlib.Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def add_noise(img, amount=18):
    random.seed(42)
    noise = Image.new("RGBA", img.size, (0, 0, 0, 0))
    px = noise.load()
    for _ in range(42000):
        x = random.randrange(img.width)
        y = random.randrange(img.height)
        alpha = random.randrange(3, amount)
        v = random.choice((0, 255))
        px[x, y] = (v, v, v, alpha)
    return Image.alpha_composite(img, noise.filter(ImageFilter.GaussianBlur(0.35)))


def draw_waveform(d, x0, y0, x1, y1, color):
    width = x1 - x0
    bars = 54
    gap = 15
    bar_w = (width - gap * (bars - 1)) / bars
    center = (y0 + y1) / 2
    max_h = (y1 - y0) * 0.76
    for i in range(bars):
        t = i / (bars - 1)
        envelope = 0.35 + 0.65 * abs(0.5 - t) * 2
        jitter = 0.78 + 0.22 * ((i * 17) % 9) / 8
        h = max_h * envelope * jitter
        x = x0 + i * (bar_w + gap)
        d.rounded_rectangle(
            [x, center - h / 2, x + bar_w, center + h / 2],
            radius=bar_w / 2,
            fill=color,
        )


def draw_tag(d, xy, text, font, fill, text_fill, pad_x=34, pad_y=18):
    x, y = xy
    w, h = text_size(d, text, font)
    box = [x, y, x + w + pad_x * 2, y + h + pad_y * 2]
    d.rounded_rectangle(box, radius=34, fill=fill)
    d.text((x + pad_x, y + pad_y - 4), text, font=font, fill=text_fill)
    return box


def main():
    img = Image.new("RGBA", (SIZE, SIZE), (247, 248, 244, 255))
    d = ImageDraw.Draw(img)

    ink = (18, 22, 25, 255)
    muted = (83, 92, 99, 255)
    blue = (24, 93, 255, 255)
    lime = (202, 244, 55, 255)
    coral = (255, 91, 72, 255)
    pale_blue = (223, 233, 255, 255)

    # Offset panels give the cover a podcast-app friendly, editorial look.
    d.rectangle([0, 0, SIZE, 360], fill=(18, 22, 25, 255))
    d.rectangle([0, 2380, SIZE, SIZE], fill=(18, 22, 25, 255))
    d.rounded_rectangle([190, 500, 2810, 2250], radius=96, fill=(255, 255, 255, 255))
    d.rounded_rectangle([230, 540, 2770, 2210], radius=74, outline=(18, 22, 25, 255), width=9)

    # Modern audio/news motif: sunrise rings plus a simple waveform.
    ring_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring_layer)
    for idx, radius in enumerate([780, 1040, 1300]):
        color = [(24, 93, 255, 42), (255, 91, 72, 30), (202, 244, 55, 42)][idx]
        rd.ellipse([1510 - radius, 1150 - radius, 1510 + radius, 1150 + radius], outline=color, width=22)
    rd.ellipse([1920, 610, 2620, 1310], fill=(202, 244, 55, 255))
    rd.ellipse([1986, 676, 2554, 1244], fill=(255, 255, 255, 255))
    rd.rectangle([1590, 1080, 2740, 1210], fill=(255, 255, 255, 255))
    img = Image.alpha_composite(img, ring_layer)
    d = ImageDraw.Draw(img)

    draw_waveform(d, 360, 1820, 2640, 2040, blue)
    d.rounded_rectangle([360, 2072, 2640, 2098], radius=13, fill=(18, 22, 25, 255))

    f_label = load_font(82)
    f_title = load_font(270)
    f_title2 = load_font(250)
    f_tag = load_font(66)
    f_mono = load_font(58, bold=False)

    d.text((170, 128), "KOTA PRIVATE PODCAST", font=f_label, fill=(247, 248, 244, 255))
    d.text((2050, 128), "NEWS / 5W1H", font=f_label, fill=lime)

    draw_tag(d, (360, 640), "毎朝 6:00", f_tag, ink, (255, 255, 255, 255))
    draw_tag(d, (800, 640), "話題の5本", f_tag, pale_blue, ink)

    d.text((360, 900), "朝の", font=f_title, fill=ink)
    d.text((360, 1190), "深掘り", font=f_title, fill=ink)
    d.text((360, 1480), "ニュース", font=f_title2, fill=ink)

    d.text((170, 2550), "FOR KOTA", font=f_label, fill=(247, 248, 244, 255))
    d.text((170, 2660), "15 MIN AUDIO DIGEST", font=f_mono, fill=(178, 186, 194, 255))
    d.rounded_rectangle([2250, 2530, 2830, 2748], radius=56, fill=coral)
    d.text((2368, 2584), "5W1H", font=f_label, fill=(255, 255, 255, 255))

    img = add_noise(img)
    img = img.convert("RGB")
    for out in OUTS:
        img.save(out, "PNG", optimize=True)
        print(f"cover -> {out}  ({out.stat().st_size} bytes)")


def make_katareru_cover():
    """語れるラジオのカバー。ニュースとは別系統の配色・モチーフ（大きな「?」）。"""
    out = REPO / "katareru-cover.png"
    img = Image.new("RGBA", (SIZE, SIZE), (250, 246, 240, 255))
    d = ImageDraw.Draw(img)

    ink = (28, 22, 30, 255)
    purple = (124, 77, 255, 255)
    coral = (255, 91, 72, 255)
    pale_purple = (231, 222, 255, 255)
    cream_panel = (255, 255, 255, 255)

    d.rectangle([0, 0, SIZE, 360], fill=ink)
    d.rectangle([0, 2380, SIZE, SIZE], fill=ink)
    d.rounded_rectangle([190, 500, 2810, 2250], radius=96, fill=cream_panel)
    d.rounded_rectangle([230, 540, 2770, 2210], radius=74, outline=ink, width=9)

    # 大きな「?」モチーフ（note シリーズのカバーと呼応）＋吹き出しの余韻
    ring_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring_layer)
    for idx, radius in enumerate([760, 1020, 1280]):
        color = [(124, 77, 255, 40), (255, 91, 72, 28), (124, 77, 255, 40)][idx]
        rd.ellipse([1500 - radius, 1180 - radius, 1500 + radius, 1180 + radius], outline=color, width=22)
    img = Image.alpha_composite(img, ring_layer)
    d = ImageDraw.Draw(img)

    f_label = load_font(82)
    f_title = load_font(300)
    f_q = load_font(900)
    f_tag = load_font(66)
    f_mono = load_font(58, bold=False)

    d.text((170, 128), "KOTA PRIVATE PODCAST", font=f_label, fill=(250, 246, 240, 255))
    d.text((2150, 128), "TALK / DEEP DIVE", font=f_label, fill=pale_purple)

    # 巨大な「?」を右上に
    d.text((2000, 560), "?", font=f_q, fill=(124, 77, 255, 90))

    draw_tag(d, (360, 660), "毎日更新", f_tag, ink, (255, 255, 255, 255))
    draw_tag(d, (820, 660), "1テーマ深掘り", f_tag, pale_purple, ink)

    d.text((360, 980), "語れる", font=f_title, fill=ink)
    d.text((360, 1320), "ように", font=f_title, fill=ink)
    d.text((360, 1660), "なりたい", font=f_title, fill=purple)

    d.text((170, 2550), "FOR KOTA", font=f_label, fill=(250, 246, 240, 255))
    d.text((170, 2660), "ONE TOPIC, EXPLAINED", font=f_mono, fill=(188, 180, 196, 255))
    d.rounded_rectangle([2250, 2530, 2830, 2748], radius=56, fill=purple)
    d.text((2410, 2584), "TALK", font=f_label, fill=(255, 255, 255, 255))

    img = add_noise(img)
    img = img.convert("RGB")
    img.save(out, "PNG", optimize=True)
    print(f"cover -> {out}  ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "katareru":
        make_katareru_cover()
    else:
        main()
