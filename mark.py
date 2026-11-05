#!/usr/bin/env python3
"""標記題目完成 / 取消完成。

用法：
  python3 mark.py 63 75-78          # 把編號 63、75~78 標成完成（完成日期=今天）
  python3 mark.py 63 --date 2026-11-04   # 指定完成日期
  python3 mark.py 63 --undo         # 取消完成
  python3 mark.py --status          # 顯示目前進度
"""
import argparse, datetime, json, pathlib, re, sys

PATH = pathlib.Path(__file__).with_name("data.json")
TZ = datetime.timezone(datetime.timedelta(hours=8))  # 台灣時間


def load():
    return json.loads(PATH.read_text(encoding="utf-8"))


def save(data):
    s = json.dumps(data, ensure_ascii=False, indent=1)
    s = re.sub(r'\{\n\s+"id": (.*?)\n\s+\}',
               lambda m: '{"id": ' + re.sub(r',\n\s+', ', ', m[1]) + '}', s, flags=re.S)
    PATH.write_text(s + "\n", encoding="utf-8")


def parse_ids(tokens):
    ids = set()
    for t in tokens:
        for part in t.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                a, b = part.split("-", 1)
                ids.update(range(int(a), int(b) + 1))
            else:
                ids.add(int(part))
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--undo", action="store_true")
    ap.add_argument("--date")
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()
    data = load()
    items = [it for d in data["days"] for it in d["items"]]
    today = datetime.datetime.now(TZ).date().isoformat()

    if a.ids:
        want = parse_ids(a.ids)
        found = set()
        for it in items:
            if it["id"] in want:
                found.add(it["id"])
                it["done"] = not a.undo
                it["doneAt"] = None if a.undo else (a.date or today)
        missing = sorted(want - found)
        if missing:
            print("找不到編號：", missing, file=sys.stderr)
        data["updated"] = today
        save(data)
        print(("取消完成：" if a.undo else "已完成：") + ", ".join(map(str, sorted(found))))

    done = sum(it["done"] for it in items)
    print(f"總進度 {done}/{len(items)}")
    if a.status:
        for d in data["days"]:
            marks = " ".join(("✓" if it["done"] else "·") + str(it["id"]) for it in d["items"])
            print(d["date"], d["weekday"], marks)


if __name__ == "__main__":
    main()
