#!/usr/bin/env python3
"""エピソードmp3を配信に追加し、feed.xml を再生成する。直近30本だけ保持。

このリポジトリは2つの独立した番組（feed）を相乗りでホストする：
  - news    : 「kota 朝の深掘りニュース」（既定）。/feed.xml /episodes/
  - katareru: 「kota 語れるラジオ」。/katareru.xml /katareru/episodes/
番組ごとに manifest・episodes ディレクトリ・カバー・チャンネル情報・配信時刻が分かれる。

usage:
  python publish.py [--show news|katareru] <mp3_src> <date YYYY-MM-DD> [title] [description]

--show 省略時は news（後方互換）。title/desc 省略時は scripts/<meta> から読む
（Windows で日本語を引数渡しすると化けるため、日本語は必ず meta ファイル経由）。
git push はこのスクリプトでは行わない（呼び出し側で明示的に実行する）。
"""
import sys
import json
import shutil
import pathlib
import datetime
from xml.sax.saxutils import escape
from mutagen.mp3 import MP3

REPO = pathlib.Path(__file__).resolve().parents[1]
BASE_URL = "https://kotayamanaka.github.io/kota-news-podcast"
MAX_EP = 30

# 番組ごとの設定。news を弄ると朝ニュースが壊れるので、追加は新エントリで行う。
SHOWS = {
    "news": {
        "ep_subdir": "episodes",          # repo 直下からの相対。feed/episodes の配置
        "feed_path": "feed.xml",
        "manifest": "episodes.json",
        "meta": "_meta.json",
        "cover": "cover-v2.png",
        "hour": 6,                         # pubDate の時刻（JST）
        "channel_title": "kota 朝の深掘りニュース",
        "channel_desc": "毎朝6時、いま話題のニュース5本を5W1Hで深掘りする、kota専用の音声ダイジェスト。",
        "category": "News",
        "default_title": "{date} 朝の深掘りニュース",
    },
    "katareru": {
        "ep_subdir": "katareru/episodes",
        "feed_path": "katareru.xml",
        "manifest": "katareru_episodes.json",
        "meta": "_meta_katareru.json",
        "cover": "katareru-cover.png",
        "hour": 6,
        "channel_title": "kota 語れるラジオ",
        "channel_desc": "毎日1本、いま話題だけど実はよく知らない単語・人物・現象を1つ選び、他人に語れるレベルまで深掘りして解説する、kota専用の音声番組。",
        "category": "Society & Culture",
        "default_title": "「{date}のテーマ」について語れるようになりたい",
    },
}


def load_manifest(manifest_path):
    if manifest_path.exists():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    return []


def rfc2822(date_str: str, hour: int) -> str:
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(hour=hour, minute=0, second=0)
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0900")


def hms(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def build_feed(eps, cfg, feed_path):
    ep_subdir = cfg["ep_subdir"]
    feed_rel = cfg["feed_path"]
    chan_link = f"{BASE_URL}/{ep_subdir.rsplit('/', 1)[0]}/" if "/" in ep_subdir else f"{BASE_URL}/"
    items = []
    for e in eps:
        url = f"{BASE_URL}/{ep_subdir}/{e['file']}"
        items.append(
            "    <item>\n"
            f"      <title>{escape(e['title'])}</title>\n"
            f"      <description>{escape(e['desc'])}</description>\n"
            f"      <itunes:summary>{escape(e['desc'])}</itunes:summary>\n"
            f"      <pubDate>{rfc2822(e['date'], cfg['hour'])}</pubDate>\n"
            f'      <enclosure url="{url}" length="{e["bytes"]}" type="audio/mpeg"/>\n'
            f'      <guid isPermaLink="true">{url}</guid>\n'
            f"      <itunes:duration>{hms(e['duration'])}</itunes:duration>\n"
            f"      <itunes:explicit>false</itunes:explicit>\n"
            "    </item>"
        )
    chan_pubdate = rfc2822(eps[0]["date"], cfg["hour"]) if eps else rfc2822("2026-06-14", cfg["hour"])
    cover_url = f"{BASE_URL}/{cfg['cover']}"
    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" '
        'xmlns:content="http://purl.org/rss/1.0/modules/content/" '
        'xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        f"    <title>{escape(cfg['channel_title'])}</title>\n"
        f"    <link>{chan_link}</link>\n"
        f'    <atom:link href="{BASE_URL}/{feed_rel}" rel="self" type="application/rss+xml"/>\n'
        "    <language>ja</language>\n"
        f"    <description>{escape(cfg['channel_desc'])}</description>\n"
        f"    <pubDate>{chan_pubdate}</pubDate>\n"
        f"    <lastBuildDate>{chan_pubdate}</lastBuildDate>\n"
        "    <generator>kota-news-podcast</generator>\n"
        "    <itunes:author>kota</itunes:author>\n"
        f"    <itunes:summary>{escape(cfg['channel_desc'])}</itunes:summary>\n"
        "    <itunes:type>episodic</itunes:type>\n"
        f'    <itunes:image href="{cover_url}"/>\n'
        f"    <image><url>{cover_url}</url><title>{escape(cfg['channel_title'])}</title>"
        f"<link>{chan_link}</link></image>\n"
        f'    <itunes:category text="{escape(cfg["category"])}"/>\n'
        "    <itunes:explicit>false</itunes:explicit>\n"
        "    <itunes:owner><itunes:name>kota</itunes:name>"
        "<itunes:email>292089821+kotayamanaka@users.noreply.github.com</itunes:email></itunes:owner>\n"
        + "\n".join(items)
        + "\n  </channel>\n</rss>\n"
    )
    feed_path.write_text(feed, encoding="utf-8")


def main():
    argv = sys.argv[1:]
    show = "news"
    if argv and argv[0] == "--show":
        show = argv[1]
        argv = argv[2:]
    elif argv and argv[0].startswith("--show="):
        show = argv[0].split("=", 1)[1]
        argv = argv[1:]
    if show not in SHOWS:
        print(f"unknown show: {show}. choose from {list(SHOWS)}")
        sys.exit(1)
    cfg = SHOWS[show]

    if len(argv) < 2:
        print(__doc__)
        sys.exit(1)
    mp3_src = pathlib.Path(argv[0])
    date_str = argv[1]

    ep_dir = REPO / cfg["ep_subdir"]
    manifest_path = REPO / "data" / cfg["manifest"]
    feed_path = REPO / cfg["feed_path"]

    # タイトル/概要：Windows では日本語をコマンドライン引数で渡すと文字化けするため、
    # 既定では scripts/<meta>（UTF-8）から読む。ROUTINE はこの方式を使う。
    # 引数で渡された場合はそれを優先（ASCII 用途・手動実行用）。
    meta_path = REPO / "scripts" / cfg["meta"]
    default_title = cfg["default_title"].format(date=date_str)
    if len(argv) > 2:
        title = argv[2]
        desc = argv[3] if len(argv) > 3 else title
    elif meta_path.exists():
        m = json.loads(meta_path.read_text(encoding="utf-8"))
        title = m.get("title") or default_title
        desc = m.get("desc") or title
    else:
        title = default_title
        desc = title

    ep_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{date_str}.mp3"
    dst = ep_dir / fname
    # synth.py が直接 <ep_dir>/<DATE>.mp3 に書く運用だと src==dst になる。その場合はコピー不要。
    if mp3_src.resolve() != dst.resolve():
        shutil.copy(mp3_src, dst)

    audio = MP3(dst)
    duration = int(audio.info.length)
    size = dst.stat().st_size

    eps = [e for e in load_manifest(manifest_path) if e["file"] != fname]
    eps.append({
        "date": date_str, "title": title, "desc": desc,
        "file": fname, "bytes": size, "duration": duration,
    })
    eps.sort(key=lambda e: e["date"], reverse=True)

    keep, removed = eps[:MAX_EP], eps[MAX_EP:]
    for e in removed:
        p = ep_dir / e["file"]
        if p.exists():
            p.unlink()

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(keep, ensure_ascii=False, indent=2), encoding="utf-8")
    build_feed(keep, cfg, feed_path)
    print(f"[{show}] published {fname}  duration={duration}s  size={size}B  total_episodes={len(keep)}")


if __name__ == "__main__":
    main()
