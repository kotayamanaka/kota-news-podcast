#!/usr/bin/env python3
"""台本テキスト -> ラジオ仕立ての mp3。

synth.py（読み正規化＋edge-tts）を使って台本を音声化し、
オープニング/エンディングのジングルと、トピック区切りのスティングを
ffmpeg（imageio-ffmpeg 同梱バイナリ）で結合する。

台本中で `[STING]` だけの行をトピックの区切りに置くと、そこにスティングが入る。
区切りが無ければ「ジングル＋本編＋ジングル」だけになる。

usage:
  python produce.py <script.txt> <out.mp3> [yomi_dict.json] [rate]

音源は assets/jingle.* と assets/sting.* を使う（make_jingle.py で生成。SUNO 製に差し替え可）。
ジングル/スティングが存在しなければ、その箇所は単に省略される（音声だけ出力）。
"""
import os
import re
import sys
import asyncio
import pathlib
import tempfile
import subprocess

import edge_tts
import imageio_ffmpeg

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import synth  # normalize() と VOICE を再利用

REPO = pathlib.Path(__file__).resolve().parents[1]
ASSETS = REPO / "assets"
DEFAULT_DICT = REPO / "data" / "yomi_dict.json"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
STING_RE = re.compile(r"^\s*\[STING\]\s*$")

# 読み上げエンジン。環境変数 TTS_BACKEND=openai で OpenAI に切替（既定は無料の edge-tts）。
TTS_BACKEND = os.environ.get("TTS_BACKEND", "edge").lower()
# OpenAI TTS 設定。声は OPENAI_TTS_VOICE で上書き可（alloy/ash/ballad/coral/echo/fable/nova/onyx/sage/shimmer/verse）。
OPENAI_TTS_MODEL = os.environ.get("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
OPENAI_TTS_VOICE = os.environ.get("OPENAI_TTS_VOICE", "shimmer")
OPENAI_TTS_INSTRUCTIONS = os.environ.get(
    "OPENAI_TTS_INSTRUCTIONS",
    "日本語のラジオ番組のナレーション。落ち着いた、自然で親しみやすい会話のトーンで、"
    "明瞭に、適度な間をとって読む。固有名詞や数字は正確に。",
)


def _openai_key():
    """OPENAI_API_KEY 環境変数か、gitignore した scripts/local/openai_key.txt から鍵を読む。"""
    k = os.environ.get("OPENAI_API_KEY")
    if k:
        return k.strip()
    kf = REPO / "scripts" / "local" / "openai_key.txt"
    if kf.exists():
        return kf.read_text(encoding="utf-8").strip()
    raise SystemExit(
        "OpenAI の鍵が見つかりません。OPENAI_API_KEY を設定するか、"
        "scripts/local/openai_key.txt に鍵を保存してください。"
    )


def _tts_openai(text, out_mp3):
    """OpenAI TTS で1セグメントを合成。OpenAI は日本語をネイティブに読むので、
    カナ変換（synth.to_kana）は通さず原文をそのまま渡す（その方が自然）。"""
    from openai import OpenAI
    client = OpenAI(api_key=_openai_key())
    with client.audio.speech.with_streaming_response.create(
        model=OPENAI_TTS_MODEL,
        voice=OPENAI_TTS_VOICE,
        input=text,
        instructions=OPENAI_TTS_INSTRUCTIONS,
        response_format="mp3",
    ) as resp:
        resp.stream_to_file(str(out_mp3))


def _find_asset(stem):
    for ext in (".wav", ".mp3", ".m4a", ".ogg"):
        p = ASSETS / f"{stem}{ext}"
        if p.exists():
            return p
    return None


def split_segments(text):
    """`[STING]` 行で分割。各セグメントは1つ以上の段落のかたまり。"""
    segs, cur = [], []
    for line in text.split("\n"):
        if STING_RE.match(line):
            segs.append("\n".join(cur).strip())
            cur = []
        else:
            cur.append(line)
    segs.append("\n".join(cur).strip())
    return [s for s in segs if s]


async def _tts(text, out_mp3, dict_path, rate):
    norm = synth.normalize(text, dict_path)
    com = edge_tts.Communicate(norm, synth.VOICE, rate=rate)
    await com.save(str(out_mp3))


def _concat(parts, out_mp3):
    """parts: 結合する音声ファイルのパス列。ffmpeg concat フィルタで mp3 化。"""
    inputs = []
    for p in parts:
        inputs += ["-i", str(p)]
    labels = ""
    for i in range(len(parts)):
        # 全入力を 44100Hz / ステレオ / fltp に揃えてから concat
        labels += f"[{i}:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[a{i}];"
    chain = "".join(f"[a{i}]" for i in range(len(parts)))
    filtergraph = labels + f"{chain}concat=n={len(parts)}:v=0:a=1[out]"
    cmd = [FFMPEG, "-y", *inputs, "-filter_complex", filtergraph,
           "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "128k", str(out_mp3)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2000:])
        raise SystemExit(f"ffmpeg failed ({r.returncode})")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    script = pathlib.Path(sys.argv[1])
    out_mp3 = pathlib.Path(sys.argv[2])
    dict_path = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_DICT
    rate = sys.argv[4] if len(sys.argv) > 4 else "+0%"

    jingle = _find_asset("jingle")
    sting = _find_asset("sting")
    segs = split_segments(script.read_text(encoding="utf-8"))
    if not segs:
        raise SystemExit("script is empty")

    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        seg_files = []
        for i, seg in enumerate(segs):
            sf = td / f"seg{i}.mp3"
            if TTS_BACKEND == "openai":
                _tts_openai(seg, sf)
            else:
                asyncio.run(_tts(seg, sf, dict_path, rate))
            seg_files.append(sf)

        parts = []
        if jingle:
            parts.append(jingle)
        for i, sf in enumerate(seg_files):
            if i > 0 and sting:
                parts.append(sting)
            parts.append(sf)
        if jingle:
            parts.append(jingle)

        _concat(parts, out_mp3)

    n_st = (len(seg_files) - 1) if sting else 0
    voice = f"openai:{OPENAI_TTS_VOICE}" if TTS_BACKEND == "openai" else "edge:Nanami"
    print(f"produced {out_mp3}  segments={len(seg_files)}  stings={n_st}  "
          f"jingle={'yes' if jingle else 'no'}  tts={voice}")


if __name__ == "__main__":
    main()
