# テックラジオ（lifehack）鮮度レビュー — 2026-06-26

> 依頼：テックラジオ（`LIFEHACK_ROUTINE.md`、SHOW=lifehack）の「内容が古い」という指摘を受けた鮮度診断・業界調査・改善提案。
> ルール：**実装変更は一切しない**。診断・調査・提案のみ。`LIFEHACK_ROUTINE.md` の修正は §7 に diff 案として置くだけ（編集はしない＝kota 承認待ち）。
> 調査者：Claude（メイン逐次、サブエージェント不使用）。出典 URL は各所と末尾にまとめた。

---

## 0. 結論サマリー（先に読む用）

- **総合鮮度評価：B−**。
- **誤解の解消**：実は「語っている**中身（ファクト）が古い**」わけではない。直近回は 2025〜2026 の最新事例・最新モデルを正しく参照できている（例 2026-06-26 回は METR 2025・Veracode 2025・Devin 値下げ・Claude Code on the web 2025-10 を引用、モデルも Gemini 3 Pro Image / GPT-5 mini と現役世代）。**台本の質と事実の鮮度は高い（A−相当）**。
- **本当の問題は「テーマ選定が旬を3〜12ヶ月遅れで拾いがち」という構造**。再現性（手順がある・始められる）を最優先にした結果、「ドキュメントが溜まった＝枯れ始めたツール」を選ぶバイアスがかかる。そして **`LIFEHACK_ROUTINE.md` に「鮮度を担保する仕組み（直近N日のトレンド源・recency フィルタ）」が一切ない**。
- **象徴的な事故**：番組初日 2026-06-18 の3本のうち2本が「NotebookLM 音声化」「RSS→AI要約で情報収集自動化」。これは `LIFEHACK_ROUTINE.md` 19行目が名指しで「kota が全部知ってる定番＝つまらない」と禁止している、まさにそのネタ。主観フィルタだけでは定番回避が効かないことを実証してしまっている。

---

## 1. 現状把握（一次情報）

### 1-1. ルーチンの構造
- `LIFEHACK_ROUTINE.md`：テーマ選定（STEP B）・リサーチ観点（STEP D）・台本の作り（STEP F）・冒頭結び定型を定義。
- `RADIO_BASE.md`：共通パイプライン（日付→選定→既出除外→並列サブエージェント深掘り→素朴疑問→台本化→ふりがな→ファクトチェック→読み検収→音声合成→配信→history追記→push）。
- 自動実行：scheduled-task `lifehack-radio` 毎朝3:30頃。**＝完全自動・無人**。これは後述の改善方針（人手キュレーションでなく、APIで取れるトレンド源を組み込む）に直結する重要な制約。

### 1-2. 取り上げた全テーマ（`data/lifehack_history.json` 全12件、2026-06-18〜06-26）

「内容の年代」は、その回の主役ツール／話題が**世に出た・話題化した**おおよその時期（各回の keywords とリサーチで裏取り）。

| 日付 | テーマ | 主役の登場/話題化時期 | 鮮度所見 |
|---|---|---|---|
| 06-18 | 音声ファースト術（Superwhisper / Wispr Flow / Aqua Voice） | 2023〜2024 | ツールは既に定番化しつつある |
| 06-18 | NotebookLM 音声概要 | 2024〜2025 | **定番ど真ん中。19行目の禁止例そのもの** |
| 06-18 | RSS→AI要約で情報収集自動化 | 汎用・恒常 | **定番。19行目で kota が名指しした「やってる」ネタ** |
| 06-19 | AIライフログ（PLAUD / Limitless） | 2024〜2025 | やや旬を過ぎ気味だが応用は新しめ |
| 06-20 | パーソナルCRM（Monica / Clay→Mesh） | Monica は数年前、Clay 改名は 2025 | 概念は古い、買収ニュースで鮮度を足している |
| 06-20 | LINE Harness × Claude Code | **2026-03** | **○ 旬。直近3ヶ月の新作OSS** |
| 06-21 | AIブラウザ（Comet / Atlas / Gemini in Chrome） | 2025-10 前後 | 半年落ち。動きは速い分野なので可 |
| 06-22 | 仕様駆動開発 / GitHub Spec Kit | 2025-09 | 9ヶ月落ち。ただし論争が続くテーマで可 |
| 06-23 | Raycast for Windows | 2025-11 公開ベータ | 7ヶ月落ち |
| 06-24 | 音声クローン入門 | 技術は 2023〜2024 | **恒常explainer。ニュースフックが弱い** |
| 06-25 | Nano Banana（Gemini 画像AI） | 2025-08 / Pro は 2025-11 | 定番化しつつあるが応用は具体的 |
| 06-26 | 非同期コーディングエージェント | 2025 通年〜現在進行形 | **◎ 最も旬。現在進行形を正しく束ねている** |

観察：
- **「◎旬」は12本中2本（LINE Harness、非同期エージェント）だけ**。残りは「半年〜数年落ちの枯れたツールを、丁寧に解説している」。
- 初日（番組改名と同日の indtruction 追加日）の3本に定番が集中。以降は改善傾向だが、**recency を担保する仕組みがないため「たまたま選者が新しめを引けた回」と「枯れネタ回」のムラ**になっている。

### 1-3. 台本の中身（サンプル）

過去台本は `_today_<SHOW>.txt`（毎日上書き）と一部 `scripts/_ep_*.txt` にしか残らない。サンプルできたのは:
- 2026-06-26（今日／非同期エージェント）：**質が高い**。「なぜ可能か／なぜ他はできないか」の深掘り作法が効いており、METR・Veracode・SWE-bench の数字、Devin 値下げ、注意点（45%脆弱性・レビュー渋滞）まで balanced。**事実の鮮度に問題なし**。
- `_ep_notebooklm.txt`（06-18／NotebookLM）：台本の出来は良いが、**題材が定番**。「2025年に日本語対応がぐっと進んだ」など、もう誰でも知っている情報。
- `_ep_lineharness.txt`（06-20／LINE Harness）：**良い回**。2026-03 の新作、作者の思想、第三者検証が少ない点まで正直に。これが目指すべき鮮度。

> ⚠️ 構造的問題として、**台本が日付別に保存されない**（`_today_lifehack.txt` は上書き）。過去回の鮮度を後から監査できない。改善の前提として、配信済み台本を `lifehack/scripts/<DATE>.txt` 等で残すことを別途検討すべき（本レビューの主題ではないが付記）。

---

## 2. 鮮度の問題の洗い出し（依頼 §2 への回答）

| 観点 | 診断 |
|---|---|
| **取り上げるツールの古さ** | 主役の中央値で**おおよそ半年落ち**。定番化・陳腐化したものが12本中4〜5本（NotebookLM・RSS要約・音声入力・音声クローン・パーソナルCRM概念）。 |
| **情報源の古さ/偏り** | **最大の盲点**。ルーチンは「general-purpose が日英 WebSearch」しか指定しておらず、**トレンド源（HN / GitHub Trending / Product Hunt / 各ニュースレター / RSS / X / arXiv）がゼロ**。WebSearch は「既にまとめ記事が書かれた＝枯れた」ものに当たりやすく、構造的に旬を逃す。 |
| **「kota がまだ知らない」フィルタ** | **効いていない**。主観判断のみで外部の鮮度シグナルに紐づいていないため、初日に定番（NotebookLM・RSS要約）を量産した。kota がヘビーユーザーである以上、「定番か否か」を人の勘でなくシグナル（トレンド初出か・kota の既知リストに無いか）で判定する必要。 |
| **AIモデル/ツールの世代** | **問題なし**。GPT-4世代やClaude 3世代を「最新」と誤って語っている形跡はない。直近回は Gemini 3 Pro Image・GPT-5 mini・Fable 5 級の現役世代を正しく参照。 |
| **2026年6月の最前線カバー** | **弱い**。「今週/今月出たもの」を拾う導線がないため、現在進行形（MCPの標準化進展、各社の非同期エージェント競争、Fable 5 / Mythos 5 を巡る輸出規制など 2026-06 の動き）は、選者がたまたま気づかない限り拾えない。 |

**まとめ**：鮮度の弱点は「**語る中身**」ではなく「**選ぶ題材のタイムスタンプ**」と「**題材を見つける情報源**」。前者は recency フィルタ、後者はトレンド源の追加で解ける。

---

## 3. 業界の現在地（依頼 §3：いまプロは何を見て最新を拾っているか）

WebSearch で 2026-06 時点を裏取りした。出典は各項末と §8。

### 3-1. 一線級ニュースレターと、その「鮮度の作り方」
- **TLDR AI**（日刊・約110万読者）：HN フロントだけに頼らず編集キュレーション。**毎日**配信＝鮮度の主戦場が日次であることの証左。
- **The Rundown AI**（200万超）：その日の「モデルリリース・プロダクトローンチ・研究」を毎日スキャナブルに圧縮。
- **Stratechery（Ben Thompson、$120/年）／Platformer**：速報でなく「戦略・力学の解釈」。深掘り（なぜ可能か／なぜ他はできないか）の手本＝本番組の深掘り作法と相性が良い。
- **Pragmatic Engineer / ByteByteGo**：開発者向けの深掘り週刊。
- 共通項：プロは「**日刊の速報レイヤー（TLDR/Rundown）＋週刊の深掘りレイヤー（Stratechery/Pragmatic）**」を組み合わせる。本番組は今、後者寄りの題材を、速報レイヤー抜きで選んでいる。
  - 出典：Readless「Best AI Newsletters 2026」, Dupple「Best Tech Newsletters 2026」, DataCamp。

### 3-2. 新ツールが「最初に」話題化する導線（パワーユーザーの一次ソース）
- **Hacker News / Show HN**：開発者の新作の初出。**Algolia API が無料・キー不要**で `search_by_date` により直近48hの高ポイント記事・Show HN を機械取得できる（自動番組に最適）。
- **GitHub Trending（daily）**：「他の開発者が今いちばん星を付けている」＝メインストリーム化前のインフラ/エージェント系を先取り。非公式 API（huchenme/github-trending-api 等）あり。
- **Product Hunt**：AI カテゴリの日次ローンチ。upvote velocity で「伸びている新作」を検出。
- **Top AI Product / Best of Show HN** 等のメタ・トラッカー：PH+HN+GitHub を横断集計。
  - 出典：hn.algolia.com/api, GitHub Trending API（huchenme 他）, topaiproduct.com, bestofshowhn.com。

### 3-3. 日本語コミュニティの導線
- **Zenn / Qiita のトレンド**：個人開発者の新ツール・使いこなしの初出。両者ともトレンド面＋RSS あり。
- **TechFeed**：複数メディアを分類・レーティングするキュレーション。情報量・鮮度が高いと評価。
- **Tech Drip**：エンジニア向け AI 要約ダイジェスト（GPT 要約）。
- **はてなブックマーク テクノロジー（人気）／note の AI タグ／X の日本AI系リスト**：話題化の二次波を検知。
- **Ledge.ai**：日本最大級の AI 特化メディア（メルマガ配信あり）。
  - 出典：Zenn 各記事（情報収集のすゝめ 他）, レバテックルーキー, Ledge.ai。

### 3-4. 自動キュレーション・AIポッドキャストの最新動向（ベンチマーク）
- **NotebookLM**：2026-03 に **Cinematic Video Overview**（Gemini 3 + Veo 3）をロールアウト。2026-06 時点で **Gemini 3.5 系**で動作。音声概要は80言語超・Deep Dive/Brief/Critique/Debate・インタラクティブ参加。
- **Spotify**：2026-05 に NotebookLM 対抗のパーソナルポッドキャスト・デスクトップアプリを発表。Adobe・ElevenLabs・Hero・Huxe もポッドキャスト生成形式を採用。
- **Granola 系**：会議メモ＋システム音声キャプチャ系が乱立。
- **含意**：「自分の資料を2人のAIが喋る」フォーマットは**もはやコモディティ**。本番組の差別化は「フォーマットの新しさ」ではなく「**題材の旬さ × 深掘りの質**」に置くべき。NotebookLM 系を題材に選ぶこと自体が時代遅れシグナル。
  - 出典：NotebookLM Wikipedia/9to5Google, TechCrunch「Spotify debuts…」(2026-05-21), blog.google。

---

## 4. 更新すべき情報源リスト（推奨セット）

**自動番組（3:30am 無人）なので「API/RSS で機械取得できるか」を最優先**にランク付け。

### Tier 1 — 毎日必ず巡回（機械取得可・recency の主軸）
| 源 | 取得方法 | 狙い |
|---|---|---|
| Hacker News（front + Show HN） | Algolia API `https://hn.algolia.com/api/v1/search_by_date?tags=story&numericFilters=created_at_i>{48h前のepoch},points>50` | 開発者の新作・新話題の初出。無料・キー不要 |
| GitHub Trending（daily, since=daily） | 非公式API or HTML | 急上昇OSS・エージェント/ツール |
| Product Hunt（AI カテゴリ Today） | PH API / スクレイパ | 新作プロダクトの upvote velocity |
| OpenAI / Anthropic / Google 公式 News RSS | `openai.com/news/rss.xml` 他 | 一次のモデル・機能リリース |

### Tier 2 — 毎日〜隔日（速報レイヤーの編集済みダイジェスト）
- TLDR AI（tldr.tech/ai、Webフェッチ可）／The Rundown AI
- Hugging Face Blog RSS／MarkTechPost RSS／The Verge AI／Last Week in AI／Ahead of AI（Raschka）
- arXiv `cs.AI` 新着（応用ネタの種・ただし噛み砕き前提）

### Tier 3 — 日本語の旬・二次波
- Zenn トレンド＋RSS／Qiita トレンド／TechFeed／Tech Drip
- はてブ テクノロジー人気／note AIタグ／Ledge.ai
- X：日本のAI系パワーユーザーのリスト（巡回はAPI制約があるため、まずは上記で代替し、X は補助）

### Tier 4 — 深掘りレイヤー（題材の「なぜ」を厚くする時に参照）
- Stratechery／Platformer／Pragmatic Engineer／ByteByteGo

---

## 5. テーマ選定ロジックの改善案（依頼 §4・最重要）

### 5-1. 2段構えにする
- **STEP B-0「トレンド収穫（新規）」**：選定の前に Tier 1〜3 を巡回し、**「直近48〜72hに動いた候補」をタイムスタンプ付きで5〜10件**リストアップ。各候補に「初出/更新日」を必ず付ける。
- **STEP B「選定」**：収穫した候補から、下のスコアで1本選ぶ。

### 5-2. 選定スコア（4軸・各5点）
1. **鮮度（recency）**：直近1週間に出た新作・新機能=5／1ヶ月以内=4／3ヶ月以内=3／半年以内=2／それ以上=1。**3未満は原則不採用**（恒常explainerで本当に非自明な切り口がある時だけ例外）。
2. **再現性**：kota が今日始められる具体手順がある=高。
3. **kota 未知度**：定番ブロックリスト（§6）に無く、トレンド初出に近いほど高。
4. **深掘り耐性**：「なぜ可能か／なぜ他はできないか」を2〜3段掘れる構造があるか。

> 現行ルーチンは①鮮度が**選定基準に存在しない**。②再現性を最優先にしている。これが「枯れたツールを丁寧に解説」バイアスの正体。**鮮度を第一基準に格上げし、再現性は足切り条件（始められること）に降格**するのが核心。

### 5-3. 具体的な選定戦略の例
- 「**HN front / Show HN で直近48h・points>100 のうち、kota が真似できる粒度のツール**」を最優先候補に。
- 「**特定キーワードの動き**」を常時監視：`MCP` `AGI` `agent` `Claude Code` `Codex` `Gemini` `音声` `自動化` `個人開発` 等。動きがあった週はそれを優先。
- 「**GitHub Trending daily の上位で、昨日まで圏外→今日急上昇**」のものを拾う。
- 日本語回が欲しい日は「**Zenn/Qiita トレンドで、海外では既出だが日本語の実践記事が今週立った**」ものを。

---

## 6. deprecation 候補（除外ルール）

### 6-1. 恒久ブロックリスト（kota 既知の定番＝選ばない）
- NotebookLM の音声化／動画化（題材として禁止。比較言及はOK）
- RSS→AI要約／Googleアラート→要約 等の「情報収集自動化」一般
- 音声入力→文字起こし→清書（Superwhisper 等の「基本的な使い方」）
- ChatGPT/Gemini/Claude の「使いこなしN選」listicle 系
- 「プロンプトエンジニアリング入門」「第二の脳/PKM 入門」などの恒常テーマ

### 6-2. recency 足切り
- 主役ツールが**12ヶ月超**前に登場 **かつ** 直近1ヶ月に目立った新展開が無いものは原則不採用。
- 「入門」「とは」で終わる恒常explainer（例：音声クローン入門）は、**今週のニュースフックが無ければ不採用**。

### 6-3. フォーマット陳腐化の自覚
- 「2人のAIが喋るポッドキャスト」「AIメモ」「AIブラウザの存在自体」は2026年にはコモディティ。**存在紹介でなく、今週の新展開・具体運用・落とし穴**に寄せる。

---

## 7. 音声台本の方法論への影響（依頼 §4最終）

台本の**質は維持**（深掘り作法・balanced・ファクトチェックは現状で良い）。鮮度を効かせるための微修正のみ：

1. **冒頭フックに「日付アンカー」を入れる**：「今週」「今月出た」「先日◯◯が発表した」のように、**旬であることを最初の一文で示す**。現状の導入は「困りがちな場面」起点で恒常的になりがち。
2. **題材の登場時期を本文で明言**：「これは◯年◯月に出たばかりで」と鮮度を聞き手に伝える（古い題材を選んだ時に自分でブレーキがかかる副次効果も）。
3. **「定番ではない理由」を一言**：なぜこれが“まだ知られていない/新しい”のかを示すと、kota の「へぇ」に刺さる。
4. 深掘り作法・読み検収・ファクトチェックの各 STEP は**変更不要**（むしろ強み）。

---

## 8. `LIFEHACK_ROUTINE.md` 修正案（diff・**提案のみ／未編集**）

> 下記は提案。実ファイルは編集していない。kota 承認後に適用のこと。

```diff
@@ ## STEP B. テーマ選定（毎日1つ） @@
+## STEP B-0. トレンド収穫（選定の前に必須・鮮度の主軸）
+
+- 選定の前に、**直近48〜72hに動いた候補を、初出/更新日つきで5〜10件**集める。最低限の巡回先（機械取得できるものを優先）：
+  1. Hacker News（front+Show HN）: `https://hn.algolia.com/api/v1/search_by_date?tags=story&numericFilters=created_at_i>{48h前のepoch}` を points 降順で。無料・キー不要。
+  2. GitHub Trending（daily）・Product Hunt（AI, Today）の急上昇。
+  3. 公式 News RSS（OpenAI/Anthropic/Google）・TLDR AI・The Rundown AI。
+  4. 日本語の旬：Zenn/Qiita トレンド・TechFeed・はてブ テクノロジー人気。
+- 各候補に **「初出/更新日」を必ず付ける**（後段の recency 足切りに使う）。
+- 詳細な推奨ソース表は `docs/TECH_RADIO_FRESHNESS_REVIEW_2026-06-26.md` §4。
+
 ## STEP B. テーマ選定（毎日1つ）

 - 「実在のツール・サービス・ワークフロー」で、**真似してテック活用が進む**ものを1つ選ぶ。
 - 領域：AIツール/モデル/エージェント・自動化（Claude Code等）・情報管理・効率化・開発/個人開発の道具・面白いWebサービス・ガジェット など。
-- **優先順位**：①AI活用・新しいテック ②再現性が高い（始められる）③kota に効きそう（PC/スマホ・自動化・仕組み化好き）。
+- **優先順位（鮮度を第一基準に格上げ）**：①**鮮度**（直近1週=最優先／1ヶ月以内=可／3ヶ月超は原則不可）②kota 未知度（定番ブロックリストに無い）③深掘り耐性（なぜ可能か/なぜ他はできないかを2〜3段掘れる）。
+  - **再現性（始められる）は「優先順位」ではなく足切り条件**：始められないネタは落とすが、再現性を理由に“枯れた定番”を選ばない。
+- **recency 足切り**：主役ツールが12ヶ月超前の登場 かつ 直近1ヶ月に新展開が無いものは原則不採用。「入門/とは」で終わる恒常explainerは今週のニュースフックが無ければ不採用。
 - ⚠️ **AI活用ネタは「kota がまだやっていない・知らない」ものを選ぶ**（kota 指示 2026-06-18）。（…中略…）定番ど真ん中は避ける。
+- **恒久ブロックリスト（題材に選ばない・比較言及はOK）**：NotebookLM 音声/動画化／RSS→AI要約・情報収集自動化／音声入力→文字起こし清書（基本）／ChatGPT・Gemini・Claude の「使いこなしN選」／プロンプト入門・第二の脳入門 等の恒常テーマ。
 - 「話題性」より「実用・真似できる・進化できる」を重視。（※鮮度足切りを通った候補の中での話）
 - `data/lifehack_history.json` の既出と被らないこと。

@@ ## STEP D. リサーチの観点（RADIO_BASE のリサーチに加えて） @@
 1. そのツール/ワザの**具体的な中身**（何が・どんな手順で・どう使う）
 2. **作っている人・やっている人・出典**（公式／個人ブログ／X／GitHub／記事。実在の事例として）
 3. **必要なもの・コスト・難易度**（無料か有料か、初期設定の重さ）
 4. **始め方の最初の一歩**（今日からできる具体アクション）
 5. **落とし穴・注意点**（うまくいかない条件、セキュリティ・プライバシー・規約等）
+6. **初出/最新更新の日付を必ず特定**（「いつ出た・いつ更新された」を出典付きで）。半年超落ちなら、今語る“新しい角度”があるか明記。無ければ題材を差し替える。

@@ ### 冒頭・結びの定型 @@
-- 冒頭：「こんにちは。テックラジオ、今日のワザは『○○』です。」
+- 冒頭：「こんにちは。テックラジオ、今日のワザは『○○』です。」**続く1〜2文に日付アンカー**（「今週/今月出たばかり」「先日◯◯が発表した」）を入れ、旬であることを最初に示す。
 - 結び：「以上、今日のテックラジオでした。まずは○○から、試してみてください。」
```

---

## 9. 出典（主要）

- Readless「Best AI Newsletters in 2026」 https://www.readless.app/blog/best-ai-newsletters-to-subscribe
- Readless「Best RSS Feeds for AI News in 2026」 https://www.readless.app/blog/best-ai-news-rss-feeds-2026
- Dupple「Best Tech Newsletters 2026」 https://dupple.com/blog/best-tech-newsletters
- DataCamp「Best AI Newsletters 2026」 https://www.datacamp.com/blog/best-ai-newsletters
- Hacker News Algolia API https://hn.algolia.com/api
- GitHub Trending API（huchenme） https://github.com/huchenme/github-trending-api
- Top AI Product（PH+HN+GitHub 横断トラッカー） https://topaiproduct.com/
- Best of Show HN https://bestofshowhn.com/
- NotebookLM（Wikipedia / 9to5Google / blog.google） https://en.wikipedia.org/wiki/NotebookLM ・ https://blog.google/innovation-and-ai/products/notebooklm-audio-overviews/
- TechCrunch「Spotify debuts a new desktop app for creating personal podcasts」(2026-05-21) https://techcrunch.com/2026/05/21/spotify-debuts-a-new-desktop-app-for-creating-personal-podcasts/
- Zenn「日々の情報収集のすゝめ」 https://zenn.dev/tyamap/articles/information-gathering-media
- レバテックルーキー「エンジニア向け情報収集サイトまとめ」 https://rookie.levtech.jp/guide/detail/545/
- Ledge.ai https://ledge.ai/
- awesome-ai-agents-2026 https://github.com/Zijian-Ni/awesome-ai-agents-2026
- O'Reilly「The AI Agents Stack (2026 Edition)」 https://www.oreilly.com/radar/the-ai-agents-stack-2026-edition/

---

## 10. 一次データ（本レビューが参照した番組内ファイル）

- `LIFEHACK_ROUTINE.md` / `RADIO_BASE.md`
- `data/lifehack_history.json`（全12件、2026-06-18〜06-26）
- `scripts/_today_lifehack.txt`（2026-06-26 回）, `scripts/_meta_lifehack.json`
- `scripts/_ep_notebooklm.txt`（06-18 NotebookLM 回）, `scripts/_ep_lineharness.txt`（06-20 LINE Harness 回）
</content>
</invoke>
