# ラジオ番組 共通制作手順（RADIO_BASE）

> このファイルは「語れるラジオ系」の各番組（katareru / lifehack / chishiki / kanshou / fukushi）が**共通で踏む制作パイプライン**。
> 各番組の scheduled-task は、まず自分の `<SHOW>_ROUTINE.md`（テーマ選定・情報源の差分）を読み、本体の制作はこの RADIO_BASE に従う。
> 作業ディレクトリ：`C:\Users\kota\Documents\Claude\kota-news-podcast`
> 記事方法論の大元：Vault `Projects/語れるようになりたい/article_playbook.md`（矛盾したらこちら優先）。

各番組の `<SHOW>`（番組ID）と日本語名：

| SHOW | 番組 | 情報源 | ルーチン |
|---|---|---|---|
| katareru | 語れるラジオ | 話題の単語をWeb調査 | KATARERU_ROUTINE.md |
| lifehack | ライフハックラジオ | 実践ワザ・AI活用事例をWeb調査 | LIFEHACK_ROUTINE.md |
| chishiki | 知識ラジオ | 6テーマ巡回・Web調査 | CHISHIKI_ROUTINE.md |
| kanshou | 鑑賞ふりかえりラジオ | Notion鑑賞記録DB | KANSHOU_ROUTINE.md |
| fukushi | 福祉ラジオ | 福祉知識を体系的にWeb調査 | FUKUSHI_ROUTINE.md |

---

## STEP A. 日付確定
- 今日の日付を `YYYY-MM-DD`（JST）で確定。以降 `<DATE>`。

## STEP B. テーマ選定
- **`<SHOW>_ROUTINE.md` の選定ロジックに従って、今日の1テーマを決める**（番組ごとに違う）。

## STEP C. 既出除外
- `data/<SHOW>_history.json` を読み、過去に取り上げたテーマと被るものを除外。

## STEP D. 深掘りリサーチ（並列サブエージェント・article_playbook §3 準拠）
- general-purpose サブエージェントを**3〜5体並列**で投げ、観点を分ける（正体/基本・ヒストリー・きっかけ/数字・現在の展開・関連人物 等。番組により観点は調整）。
- 各エージェントに必ず指示：**仮説・推測禁止／出典URL全件／日英両方で検索／公式・取材・本人発言に限定／未確認は「未確認」と明記／面白い小ネタTop5**。
- ファクトチェック：人名・固有名詞の表記は公式orWikipedia、数値は公式・大手メディアで裏取れたものだけ。取れない数値は使わない。

## STEP E. 素朴疑問チェック（必須）
- 「普通の人がこのテーマで浮かべる素朴な疑問」を3〜5個書き出し、台本で答えられているか点検。当たり前の問いは避け、非自明な「なぜ」に寄せる。

## STEP F. 音声台本化（約1800〜2200字＝約6〜8分）
構成（article_playbook §1 を音声向けに適応）：
```
導入（話題性フック・事実ベース。kotaの実体験は捏造しない）
 → まず、○○とは（正体・現在地の数字を最小限）＋「○○を3つ共有します」予告
[STING]
 → トピック1（「実は〜」or「ポイント1」具体タイトル）
[STING]
 → トピック2
[STING]
 → トピック3 ＋ おわりに（小ネタ1個・余韻）
```
- **トピックの境目に `[STING]` だけの行を入れる**（produce.py がそこに区切り音を入れる）。3トピックなら [STING] は3つ。
- やらない（playbook §2）：抽象化・補助線・系譜論／締めの断定キャッチコピー／独立した小ネタ集／会社情報や受賞歴の羅列／題材に合わないフレーミング／空振りの数値フック。
- 文体：ですます調・会話寄り（「〜なんですよね」「実はこうなってて」「ちなみに」）。演説調は避ける。
- 冒頭・結びの定型は各 `<SHOW>_ROUTINE.md` に従う（無ければ「こんにちは。○○ラジオ、今日のテーマは『△△』です。」「以上、今日の『△△』でした。これで明日、ちょっと語れますね。」）。

## STEP G. 読み上げ用カナ台本（Claude本人がふりがな・必須）
- 漢字を文脈に合う正しい読みでカナ化（固有名詞・人名・新語は WebSearch で読み確認）。**数字・日付・金額・件数は数字のまま**（synth が保護）。英略語・記号はカナ/言葉に。
- `[STING]` 行はそのまま残す（produce.py が解釈する）。
- 保存先：`scripts/_today_<SHOW>.txt`。毎回出る固有名詞は `data/yomi_dict.json` に追記（全番組共通・kotaに聞かず追記可）。

## STEP H. 音声合成（音楽入り）
```
python scripts/produce.py scripts/_today_<SHOW>.txt <SHOW>/episodes/<DATE>.mp3
```
- produce.py が：各セグメントを edge-tts（ナナミ固定）で合成 → **オープニング/エンディングのジングル＋[STING]位置に区切り音**を ffmpeg で合体。
- 音源は `assets/jingle.*` `assets/sting.*`（make_jingle.py 生成。SUNO製に差し替え可）。

## STEP I. メタ情報（日本語を引数で渡さない）
- `scripts/_meta_<SHOW>.json` を UTF-8 で書く：`{ "title": "...", "desc": "1〜2文。3トピックの要点＋主な出典名を入れると説明欄が充実" }`

## STEP J. 配信
```
python scripts/publish.py --show <SHOW> <SHOW>/episodes/<DATE>.mp3 <DATE>
```
- ⚠️ `--show <SHOW>` を必ず付ける（忘れると別番組のfeedを壊す）。

## STEP K. history 追記
- `data/<SHOW>_history.json` に今日のテーマを追記（date / theme / keywords）。STEP L の前に。

## STEP L. git push
```
git add -A && git commit -m "<SHOW> <DATE>: <テーマ名>" && git push
```

---

## 失敗時
- 詰まったら、その時点までをログに残して中断。不完全・壊れた音声は配信しない（push しない）。edge-tts/ffmpeg が落ちたら時間を置いて1回リトライ。

## 購読（kota 用メモ）
- Apple ポッドキャスト「ライブラリ→右上→番組をURLでフォロー」に **`<feed>?v=2` を貼る**（例 `https://kotayamanaka.github.io/kota-news-podcast/<SHOW>.xml?v=2`）。新規フィードは末尾 `?v=N` を付けないと「サーバまたは配信が見つからない」になる（Appleキャッシュ回避）。ダメなら `?v=3`。

## 完了報告
- 選んだテーマと「なぜ」を1行、トピック3つの見出し、音声の長さ。
