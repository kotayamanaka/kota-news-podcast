#!/usr/bin/env python3
"""台本テキスト -> mp3（edge-tts / Nanami）。読み辞書を適用してから合成する。

usage:
  python synth.py <in_text> <out_mp3> [yomi_dict.json] [rate]
    rate 例: "+0%"（既定）, "-10%"（ゆっくり）, "+15%"（速め）
"""
import sys
import json
import asyncio
import pathlib
import edge_tts

VOICE = "ja-JP-NanamiNeural"
REPO = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_DICT = REPO / "data" / "yomi_dict.json"


def apply_yomi(text: str, dict_path: pathlib.Path) -> str:
    if not dict_path.exists():
        return text
    d = json.loads(dict_path.read_text(encoding="utf-8"))
    # 長いキーから置換（部分一致の事故を防ぐ。例: OpenAI を AI より先に処理）
    for key in sorted(d.keys(), key=len, reverse=True):
        text = text.replace(key, d[key])
    return text


async def synth(in_text: pathlib.Path, out_mp3: pathlib.Path, dict_path: pathlib.Path, rate: str):
    text = in_text.read_text(encoding="utf-8")
    text = apply_yomi(text, dict_path)
    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    com = edge_tts.Communicate(text, VOICE, rate=rate)
    await com.save(str(out_mp3))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    in_text = pathlib.Path(sys.argv[1])
    out_mp3 = pathlib.Path(sys.argv[2])
    dict_path = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_DICT
    rate = sys.argv[4] if len(sys.argv) > 4 else "+0%"
    asyncio.run(synth(in_text, out_mp3, dict_path, rate))
    print(f"synth ok -> {out_mp3}")


if __name__ == "__main__":
    main()
