#!/usr/bin/env python3
"""台本テキストの「漢字を含む語」の読みを形態素解析で洗い出す、ふりがな事前チェッカー。

毎朝のルーチンで synth.py に渡す前に必ず実行する。出力されたリストを AI が確認し、
読みが誤り・紛らわしいものは台本中で **カタカナに直す**（edge-tts はカタカナを正しく読む）。
恒久的に直したいものは data/yomi_dict.json に積む。

usage:
  python yomi_check.py <script.txt>
"""
import sys
import re
import json
import pathlib
import fugashi

# Windows のリダイレクト時も UTF-8 で出力（cp932 文字化け防止）
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

REPO = pathlib.Path(__file__).resolve().parents[1]
YOMI_DICT = REPO / "data" / "yomi_dict.json"
KANJI = re.compile(r"[一-鿿々]")  # CJK統合漢字 + 々

# よく誤読される定番の語（読みが割れる・TTSが外しやすい）。レポートで★を付けて注意喚起する。
TRAP_HINTS = {
    "行方": "ゆくえ", "私": "わたし", "何": "なに/なん", "筋": "きん/すじ",
    "他": "ほか/た", "海老": "えび", "一日": "いちにち/ついたち", "二日": "ふつか",
    "市場": "しじょう/いちば", "上手": "じょうず/うわて", "分": "ふん/ぶん/わ.け",
    "生": "せい/なま/き", "間": "あいだ/かん/ま", "気色": "けしき/きしょく",
}


def load_dict_keys():
    if YOMI_DICT.exists():
        return set(json.loads(YOMI_DICT.read_text(encoding="utf-8")).keys())
    return set()


def reading_of(word):
    f = word.feature
    return getattr(f, "kana", None) or getattr(f, "pron", None) or word.surface


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
    dict_keys = load_dict_keys()
    tagger = fugashi.Tagger()

    seen = {}
    for w in tagger(text):
        s = w.surface
        if KANJI.search(s):
            seen.setdefault(s, reading_of(w))

    if not seen:
        print("漢字を含む語は見つかりませんでした。")
        return

    print(f"=== ふりがなチェック: 漢字語 {len(seen)} 種 ===")
    print("（表記 -> 解析器の読み）  ★=定番の誤読注意語  ◎=辞書登録済み(自動置換される)\n")
    for surface, yomi in sorted(seen.items()):
        marks = ""
        if surface in dict_keys:
            marks += "◎"
        if surface in TRAP_HINTS:
            marks += f"★(本来:{TRAP_HINTS[surface]})"
        print(f"  {surface}  ->  {yomi}  {marks}")

    print(
        "\n[AIへの指示] 上のうち、読みが文脈に対して誤り or 紛らわしい語、"
        "および固有名詞・人名・地名は、台本中で **カタカナ表記に書き換える**。"
        "毎回出る定常的な誤読は data/yomi_dict.json に追記しておく（kota に聞かない）。"
    )


if __name__ == "__main__":
    main()
