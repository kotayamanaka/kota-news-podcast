# 新シリーズ（番組）の追加レシピ

> このリポジトリは1つで複数のポッドキャスト番組（feed）を相乗りホストする。新番組を足す手順を**穴埋め式**でまとめたもの。所要：10分程度。

新番組のIDを `<SHOW>`（半角英小文字）とする。例：`lifehack`。

## 1. `scripts/publish.py` の `SHOWS` にエントリを追加
```python
"<SHOW>": {
    "ep_subdir": "<SHOW>/episodes",
    "feed_path": "<SHOW>.xml",            # フィードはルート直下（Apple取り込みが安定）
    "manifest": "<SHOW>_episodes.json",
    "meta": "_meta_<SHOW>.json",
    "cover": "<SHOW>-cover.png",
    "hour": 7,                            # pubDate の時刻（配信枠）
    "channel_title": "kota ○○ラジオ",
    "channel_desc": "番組説明（1〜2文）。",
    "category": "Education",              # Apple カテゴリ（News/Education/Technology/Arts/Society & Culture 等）
    "default_title": "○○（{date}）",
},
```

## 2. カバー画像
- `scripts/make_cover.py` の `GENERIC_COVERS` に `<SHOW>` を追加（配色・大漢字・タイトル3行・タグ・ラベル）。
- 生成：`python scripts/make_cover.py <SHOW>`（または全部まとめて `all-new`）。
- 目視確認すること（3000pxの正方形PNG・大漢字がはみ出し過ぎていないか）。

## 3. ディレクトリと台帳
```
mkdir -p <SHOW>/episodes
echo "[]" > data/<SHOW>_episodes.json
echo "[]" > data/<SHOW>_history.json
```

## 4. 差分ルーチン `<SHOW>_ROUTINE.md`
- **テーマ選定と情報源**だけを書く（制作本体は `RADIO_BASE.md` を踏む）。
- 既存の `LIFEHACK_ROUTINE.md` 等をテンプレにコピーして書き換えるのが速い。

## 5. 空フィードを生成（URLを有効化）
```
python - <<'PY'
import importlib.util,pathlib
s=importlib.util.spec_from_file_location('p','scripts/publish.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
cfg=m.SHOWS["<SHOW>"]; m.build_feed([],cfg,pathlib.Path(cfg["feed_path"]))
PY
```

## 6. scheduled-task を登録
- `mcp__scheduled-tasks__create_scheduled_task`：taskId `<SHOW>-radio`、cron は**他番組と30分ずらす**（git push衝突回避。例 朝7:00/7:30/8:00/8:30）。
- prompt：「作業ディレクトリで `<SHOW>_ROUTINE.md` と `RADIO_BASE.md` を読み、手順通り実行」。

## 7. git push → 初回エピソード → 購読
- push 後、scheduled-task の初回実行で**1本目のエピソードを必ず作る**（空のまま公開しない）。
- kota は Apple ポッドキャストの「番組をURLでフォロー」に **`https://kotayamanaka.github.io/kota-news-podcast/<SHOW>.xml?v=2`** を貼る（`?v=N` 必須。Appleキャッシュ回避）。

## ⚠️ 重要な落とし穴（既出）
- **空フィードを先に公開→subscribe すると Apple がそのURLを空のままキャッシュして固まる**。必ず1本入れてから購読。
- 新規フィードは **`?v=2` を付けないと「サーバまたは配信が見つからない」**になる。
- **本数を散らす**：全番組を同時刻に毎日だと聴ききれない＆push衝突。cronをずらす。
