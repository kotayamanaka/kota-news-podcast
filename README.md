# kota-news-podcast

kota 専用の「朝の深掘りニュース」Podcast。毎朝6時、いま話題のニュース5本を5W1Hで深掘りした約15分の音声を自動生成して配信する。

- **配信フィード（Pod購読URL）**: `https://kotayamanaka.github.io/kota-news-podcast/feed.xml`
- **声**: edge-tts / `ja-JP-NanamiNeural`
- **保持**: 直近30本（古いものは自動削除）

## 構成

```
feed.xml              配信フィード（自動生成・編集しない）
cover-v2.png          カバー画像（RSS/サイト参照）
cover.png             カバー画像（互換用コピー）
index.html            簡易ランディング
episodes/<DATE>.mp3   各エピソード音声
data/
  yomi_dict.json      読み辞書（誤読対策・置換ルール）
  history.json        既出トピックのログ（重複回避用）
  episodes.json       エピソード台帳（自動生成）
scripts/
  synth.py            台本テキスト -> mp3（読み辞書を適用）
  publish.py          エピソード追加 + feed.xml 再生成 + 30本剪定
ROUTINE.md            毎朝の生成手順書（scheduled-task が実行）
```

## 手動で1本作る場合

```
python scripts/synth.py scripts/_today.txt episodes/2026-06-14.mp3
python scripts/publish.py episodes/2026-06-14.mp3 2026-06-14 "2026-06-14 朝の深掘りニュース" "見出し1・見出し2・..."
git add -A && git commit -m "episode 2026-06-14" && git push
```

## 誤読を直す

`data/yomi_dict.json` に `"表記": "よみ"` を追記する。長いキーから順に置換される。
