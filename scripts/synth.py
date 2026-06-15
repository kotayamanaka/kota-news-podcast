#!/usr/bin/env python3
"""台本テキスト -> mp3（edge-tts / Nanami）。

根本的な誤読対策：edge-tts に渡す前に、台本の漢字を形態素解析器(unidic)の読みで
**カナに自動変換**する。edge-tts はカナを誤読しないので、「漢字の読み間違い」という
カテゴリごと消える。語を1個ずつ辞書登録する必要がない。

処理順：
  1. yomi_dict.json を適用（unidic 自体が誤る稀な語の上書き用・任意）
  2. 漢字を含むトークンを unidic の読み(カナ)に変換（数字・カナ・記号・英字はそのまま）
  3. edge-tts で合成

usage:
  python synth.py <in_text> <out_mp3> [yomi_dict.json] [rate]
  python synth.py --preview-kana <in_text> [out_txt]   # 変換後テキストを確認（合成しない）
"""
import re
import sys
import json
import asyncio
import pathlib
import edge_tts

VOICE = "ja-JP-NanamiNeural"
REPO = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_DICT = REPO / "data" / "yomi_dict.json"
KANJI_RE = re.compile(r"[一-鿿々〆ヶ]")

_TAGGER = None


def _tagger():
    global _TAGGER
    if _TAGGER is None:
        import fugashi
        _TAGGER = fugashi.Tagger()
    return _TAGGER


def apply_yomi(text: str, dict_path: pathlib.Path) -> str:
    if not dict_path or not dict_path.exists():
        return text
    d = json.loads(dict_path.read_text(encoding="utf-8"))
    for key in sorted(d.keys(), key=len, reverse=True):  # 長いキー優先（OpenAI を AI より先に）
        text = text.replace(key, d[key])
    return text


def _reading(word):
    f = word.feature
    for attr in ("kana", "pron"):
        r = getattr(f, attr, None)
        if r and r != "*":
            return r
    return None


def to_kana(text: str) -> str:
    """漢字を含むトークンを unidic の読み(カナ)へ。改行は保持。

    ただし **接尾辞（助数詞）は変換しない**。日付や数量（15日・220本・2026年・5％）は
    edge-tts が「数字＋漢字の助数詞」のまとまりで正しく読むため、漢字のまま残す。
    （解析器は「15日」の日を『カ』と外すなど、ここでむしろ誤るので触らない。）
    """
    tagger = _tagger()
    out_lines = []
    for line in text.split("\n"):
        if not line.strip():
            out_lines.append(line)
            continue
        buf = []
        for w in tagger(line):
            s = w.surface
            pos1 = getattr(w.feature, "pos1", "") or ""
            if KANJI_RE.search(s) and pos1 != "接尾辞":
                r = _reading(w)
                buf.append(r if r else s)
            else:
                buf.append(s)
        out_lines.append("".join(buf))
    return "\n".join(out_lines)


def normalize(text: str, dict_path: pathlib.Path) -> str:
    text = apply_yomi(text, dict_path)
    text = to_kana(text)
    return text


async def synth(in_text: pathlib.Path, out_mp3: pathlib.Path, dict_path: pathlib.Path, rate: str):
    text = normalize(in_text.read_text(encoding="utf-8"), dict_path)
    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    com = edge_tts.Communicate(text, VOICE, rate=rate)
    await com.save(str(out_mp3))


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--preview-kana":
        src = pathlib.Path(sys.argv[2])
        converted = normalize(src.read_text(encoding="utf-8"), DEFAULT_DICT)
        if len(sys.argv) > 3:
            pathlib.Path(sys.argv[3]).write_text(converted, encoding="utf-8")
            print(f"preview -> {sys.argv[3]}")
        else:
            try:
                sys.stdout.reconfigure(encoding="utf-8")
            except Exception:
                pass
            print(converted)
        return

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
