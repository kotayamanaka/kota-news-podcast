#!/usr/bin/env python3
"""エピソードmp3を配信に追加し、feed.xml を再生成する。直近30本だけ保持。

usage:
  python publish.py <mp3_src> <date YYYY-MM-DD> <title> [description]

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
EP_DIR = REPO / "episodes"
MANIFEST = REPO / "data" / "episodes.json"
FEED = REPO / "feed.xml"
MAX_EP = 30

CHANNEL_TITLE = "kota 朝の深掘りニュース"
CHANNEL_DESC = "毎朝6時、いま話題のニュース5本を5W1Hで深掘りする、kota専用の音声ダイジェスト。"


def load_manifest():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return []


def rfc2822(date_str: str) -> str:
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(hour=6, minute=0, second=0)
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0900")


def hms(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def build_feed(eps):
    items = []
    for e in eps:
        url = f"{BASE_URL}/episodes/{e['file']}"
        items.append(
            "    <item>\n"
            f"      <title>{escape(e['title'])}</title>\n"
            f"      <description>{escape(e['desc'])}</description>\n"
            f"      <itunes:summary>{escape(e['desc'])}</itunes:summary>\n"
            f"      <pubDate>{rfc2822(e['date'])}</pubDate>\n"
            f'      <enclosure url="{url}" length="{e["bytes"]}" type="audio/mpeg"/>\n'
            f'      <guid isPermaLink="true">{url}</guid>\n'
            f"      <itunes:duration>{hms(e['duration'])}</itunes:duration>\n"
            f"      <itunes:explicit>false</itunes:explicit>\n"
            "    </item>"
        )
    chan_pubdate = rfc2822(eps[0]["date"]) if eps else "Sat, 14 Jun 2026 06:00:00 +0900"
    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" '
        'xmlns:content="http://purl.org/rss/1.0/modules/content/" '
        'xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        f"    <title>{escape(CHANNEL_TITLE)}</title>\n"
        f"    <link>{BASE_URL}/</link>\n"
        f'    <atom:link href="{BASE_URL}/feed.xml" rel="self" type="application/rss+xml"/>\n'
        "    <language>ja</language>\n"
        f"    <description>{escape(CHANNEL_DESC)}</description>\n"
        f"    <pubDate>{chan_pubdate}</pubDate>\n"
        f"    <lastBuildDate>{chan_pubdate}</lastBuildDate>\n"
        "    <generator>kota-news-podcast</generator>\n"
        "    <itunes:author>kota</itunes:author>\n"
        f"    <itunes:summary>{escape(CHANNEL_DESC)}</itunes:summary>\n"
        "    <itunes:type>episodic</itunes:type>\n"
        f'    <itunes:image href="{BASE_URL}/cover.png"/>\n'
        f"    <image><url>{BASE_URL}/cover.png</url><title>{escape(CHANNEL_TITLE)}</title>"
        f"<link>{BASE_URL}/</link></image>\n"
        '    <itunes:category text="News"/>\n'
        "    <itunes:explicit>false</itunes:explicit>\n"
        "    <itunes:owner><itunes:name>kota</itunes:name>"
        "<itunes:email>292089821+kotayamanaka@users.noreply.github.com</itunes:email></itunes:owner>\n"
        + "\n".join(items)
        + "\n  </channel>\n</rss>\n"
    )
    FEED.write_text(feed, encoding="utf-8")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    mp3_src = pathlib.Path(sys.argv[1])
    date_str = sys.argv[2]
    # タイトル/概要：Windows では日本語をコマンドライン引数で渡すと文字化けすることが
    # あるため、既定では scripts/_meta.json（UTF-8）から読む。ROUTINE はこの方式を使う。
    # 引数で渡された場合はそれを優先（ASCII 用途・手動実行用）。
    meta_path = REPO / "scripts" / "_meta.json"
    if len(sys.argv) > 3:
        title = sys.argv[3]
        desc = sys.argv[4] if len(sys.argv) > 4 else title
    elif meta_path.exists():
        m = json.loads(meta_path.read_text(encoding="utf-8"))
        title = m.get("title") or f"{date_str} 朝の深掘りニュース"
        desc = m.get("desc") or title
    else:
        title = f"{date_str} 朝の深掘りニュース"
        desc = title

    EP_DIR.mkdir(parents=True, exist_ok=True)
    fname = f"{date_str}.mp3"
    dst = EP_DIR / fname
    # synth.py が直接 episodes/<DATE>.mp3 に書く運用だと src==dst になる。その場合はコピー不要。
    if mp3_src.resolve() != dst.resolve():
        shutil.copy(mp3_src, dst)

    audio = MP3(dst)
    duration = int(audio.info.length)
    size = dst.stat().st_size

    eps = [e for e in load_manifest() if e["file"] != fname]
    eps.append({
        "date": date_str, "title": title, "desc": desc,
        "file": fname, "bytes": size, "duration": duration,
    })
    eps.sort(key=lambda e: e["date"], reverse=True)

    keep, removed = eps[:MAX_EP], eps[MAX_EP:]
    for e in removed:
        p = EP_DIR / e["file"]
        if p.exists():
            p.unlink()

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(keep, ensure_ascii=False, indent=2), encoding="utf-8")
    build_feed(keep)
    print(f"published {fname}  duration={duration}s  size={size}B  total_episodes={len(keep)}")


if __name__ == "__main__":
    main()
