# kota-news-podcast

kota 専用の音声 Podcast。1つのリポジトリで **2つの独立番組**（feed）を相乗りホストする。

| 番組 | 内容 | 配信フィード（Pod購読URL） | 時刻 |
|---|---|---|---|
| 朝の深掘りニュース | 話題のニュース5本を5W1Hで深掘り（約15分） | `https://kotayamanaka.github.io/kota-news-podcast/feed.xml` | 毎朝5:40頃 |
| 語れるラジオ | 話題だけど実はよく知らない単語・人物・現象を1つ深掘り（約5〜8分） | `https://kotayamanaka.github.io/kota-news-podcast/katareru.xml` | 毎朝5:15頃 |
| ライフハックラジオ | 生活・健康を進化させる実践ワザ（特にAI活用） | `https://kotayamanaka.github.io/kota-news-podcast/lifehack.xml` | 毎朝3:30頃 |
| 知識ラジオ | 企業/商品/駅周辺/世界の国/経営者/業界をローテ | `https://kotayamanaka.github.io/kota-news-podcast/chishiki.xml` | 毎朝4:00頃 |
| 鑑賞ふりかえりラジオ | Notion鑑賞記録の最新（無ければ直近）を特集 | `https://kotayamanaka.github.io/kota-news-podcast/kanshou.xml` | 毎朝4:30頃 |
| 福祉ラジオ | 落穂会支援向け・障害者支援を体系学習 | `https://kotayamanaka.github.io/kota-news-podcast/fukushi.xml` | 毎朝4:45頃 |

> 全番組を朝6時までに仕上げる方針（kota指示）。生成は早朝に25分間隔で実行（git push衝突回避）。新番組の追加は `NEW_SERIES.md`、共通制作手順は `RADIO_BASE.md`。

- **声**: edge-tts / `ja-JP-NanamiNeural`（両番組共通）
- **保持**: 各番組 直近30本（古いものは自動削除）
- 2番組は `data/yomi_dict.json`（読み辞書）と `synth.py`・git push 動線を共有する。

## 構成

```
feed.xml                 朝ニュースの配信フィード（自動生成・編集しない）
cover-v2.png / cover.png 朝ニュースのカバー画像
index.html               朝ニュースの簡易ランディング
episodes/<DATE>.mp3       朝ニュースの各エピソード音声
katareru.xml             語れるラジオの配信フィード（自動生成・ルート直下）
katareru/
  index.html             語れるラジオの簡易ランディング
  episodes/<DATE>.mp3     語れるラジオの各エピソード音声
katareru-cover.png       語れるラジオのカバー画像
data/
  yomi_dict.json         読み辞書（誤読対策・両番組共通）
  history.json           朝ニュースの既出トピック（重複回避）
  episodes.json          朝ニュースのエピソード台帳（自動生成）
  katareru_history.json  語れるラジオの既出テーマ（重複回避）
  katareru_episodes.json 語れるラジオのエピソード台帳（自動生成）
scripts/
  synth.py               台本テキスト -> mp3（読み辞書を適用・両番組共通）
  publish.py             エピソード追加 + feed.xml 再生成 + 30本剪定（--show で番組切替）
  make_cover.py          カバー生成（引数 katareru で語れるラジオ用）
ROUTINE.md               朝ニュースの毎朝の生成手順書（scheduled-task が実行）
KATARERU_ROUTINE.md      語れるラジオの毎日の生成手順書（scheduled-task が実行）
```

## 手動で1本作る場合

朝ニュース（既定）：
```
python scripts/synth.py scripts/_today.txt episodes/2026-06-14.mp3
python scripts/publish.py episodes/2026-06-14.mp3 2026-06-14 "2026-06-14 朝の深掘りニュース" "見出し1・見出し2・..."
git add -A && git commit -m "episode 2026-06-14" && git push
```

語れるラジオ（`--show katareru` を必ず付ける）：
```
python scripts/synth.py scripts/_today_katareru.txt katareru/episodes/2026-06-14.mp3
# scripts/_meta_katareru.json に {"title":"...","desc":"..."} を UTF-8 で書いてから:
python scripts/publish.py --show katareru katareru/episodes/2026-06-14.mp3 2026-06-14
git add -A && git commit -m "katareru 2026-06-14: テーマ名" && git push
```

## 誤読を直す

`data/yomi_dict.json` に `"表記": "よみ"` を追記する。長いキーから順に置換される。
