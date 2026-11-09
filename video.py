#!/usr/bin/env python3
"""管理每日學習縮時影片（存在 data.json 的 "videos"）。

用法：
  python3 video.py 2026-11-09 https://drive.google.com/file/d/XXXX/view   # 新增/取代某天的影片
  python3 video.py today XXXX --title "熱力過程"                            # today = 今天（台灣時間）；也可只給 Drive 檔案 ID 或 YouTube 連結
  python3 video.py --remove 2026-11-09
  python3 video.py --list
"""
import argparse, datetime, sys
from mark import load, save, TZ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("date", nargs="?")
    ap.add_argument("url", nargs="?")
    ap.add_argument("--title")
    ap.add_argument("--remove")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    data = load()
    vids = data.setdefault("videos", [])
    today = datetime.datetime.now(TZ).date().isoformat()

    if a.remove:
        d = today if a.remove == "today" else a.remove
        before = len(vids)
        vids[:] = [v for v in vids if v["date"] != d]
        print("已刪除" if len(vids) < before else "找不到", d)
    elif a.date and a.url:
        d = today if a.date == "today" else a.date
        datetime.date.fromisoformat(d)
        vids[:] = [v for v in vids if v["date"] != d]
        v = {"date": d, "url": a.url}
        if a.title:
            v["title"] = a.title
        vids.append(v)
        vids.sort(key=lambda v: v["date"])
        print("已加入影片", d, a.url)
    elif not a.list:
        ap.print_help()
        sys.exit(1)

    if a.remove or a.date:
        data["updated"] = today
        save(data)
    print(f"共 {len(vids)} 部影片")
    for v in vids:
        print(" ", v["date"], v.get("title", ""), v["url"])


if __name__ == "__main__":
    main()
