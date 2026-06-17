#!/usr/bin/env python3
"""語れるラジオのジングル/スティング音源を生成する（numpy 合成・著作権フリー）。

出力:
  assets/jingle.wav  オープニング/エンディング用（数秒・ベル系アルペジオ）
  assets/sting.wav   トピック区切り用（短い2音）

SUNO 等で作った音源に差し替える場合は、同じファイル名で assets/ に置けばよい。
（produce.py は assets/jingle.* と assets/sting.* を拡張子問わず拾う）
"""
import wave
import pathlib
import struct
import math

REPO = pathlib.Path(__file__).resolve().parents[1]
ASSETS = REPO / "assets"
SR = 44100


def _tone(freq, dur, decay=6.0, partials=((1, 1.0), (2, 0.5), (3, 0.22))):
    """ベル/マリンバ風の単音（指数減衰 + 倍音）。float リスト[-1,1]を返す。"""
    n = int(SR * dur)
    out = [0.0] * n
    for k, amp in partials:
        w = 2 * math.pi * freq * k
        for i in range(n):
            t = i / SR
            out[i] += amp * math.sin(w * t) * math.exp(-decay * t)
    return out


def _mix_at(buf, samples, start, gain=1.0):
    for i, v in enumerate(samples):
        idx = start + i
        if 0 <= idx < len(buf):
            buf[idx] += v * gain


def _note(name):
    # MIDI 風: A4=440。name 例 "C5"
    table = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    p = table[name[0]]
    octave = int(name[1])
    midi = 12 * (octave + 1) + p
    return 440.0 * 2 ** ((midi - 69) / 12)


def _write_wav(path, mono, peak=0.9):
    m = max(1e-9, max(abs(x) for x in mono))
    scale = peak / m
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for x in mono:
            v = int(max(-1.0, min(1.0, x * scale)) * 32767)
            frames += struct.pack("<hh", v, v)
        w.writeframes(bytes(frames))
    print(f"wrote {path}  ({len(mono)/SR:.2f}s)")


def make_jingle():
    total = int(SR * 4.2)
    buf = [0.0] * total
    # 明るい上行アルペジオ C5 E5 G5 C6 → 余韻の和音
    seq = [("C5", 0.00), ("E5", 0.18), ("G5", 0.36), ("C6", 0.54)]
    for name, t in seq:
        _mix_at(buf, _tone(_note(name), 1.6, decay=4.0), int(SR * t), gain=0.7)
    # 余韻の和音（柔らかく）
    for name in ("C5", "E5", "G5"):
        _mix_at(buf, _tone(_note(name), 2.6, decay=2.2), int(SR * 0.95), gain=0.4)
    # 全体フェードアウト
    for i in range(total):
        t = i / SR
        if t > 2.6:
            buf[i] *= max(0.0, 1.0 - (t - 2.6) / 1.6)
    _write_wav(ASSETS / "jingle.wav", buf)


def make_sting():
    total = int(SR * 0.85)
    buf = [0.0] * total
    # 短い2音 G5 → C6（区切り用）。前後に軽い無音
    _mix_at(buf, _tone(_note("G5"), 0.5, decay=9.0), int(SR * 0.06), gain=0.6)
    _mix_at(buf, _tone(_note("C6"), 0.55, decay=8.0), int(SR * 0.20), gain=0.6)
    _write_wav(ASSETS / "sting.wav", buf)


if __name__ == "__main__":
    make_jingle()
    make_sting()
