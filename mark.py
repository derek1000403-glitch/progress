#!/usr/bin/env python3
"""標記題目完成 / 取消完成。

用法：
  python3 mark.py 63 75-78          # 把編號 63、75~78 標成完成（完成日期=今天）
  python3 mark.py 63 --date 2026-11-04   # 指定完成日期
  python3 mark.py 63 --redo         # 標成「重做」（黃色，先算完成）
  python3 mark.py 63 --redo --note "推導不連貫"   # 重做並附註（網站上顯示）
  python3 mark.py 63 --undo         # 取消完成 / 取消重做，回到未做
  python3 mark.py --summary "今天專注 3 小時" [--date 2026-11-12]   # 每日小結
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
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--undo", action="store_true")
    g.add_argument("--redo", action="store_true")
    ap.add_argument("--date")
    ap.add_argument("--note", help="附註；空字串則清除")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--summary", help="寫每日小結（配合 --date，預設今天）；空字串則清除")
    a = ap.parse_args()
    data = load()
    items = [it for d in data["days"] for it in d["items"]]
    today = datetime.datetime.now(TZ).date().isoformat()

    if a.summary is not None:
        d = a.date or today
        day = next((x for x in data["days"] if x["date"] <= d <= x.get("dateEnd", x["date"])), None)
        if day is None:
            day = {"date": d, "weekday": "日一二三四五六"[(datetime.date.fromisoformat(d).weekday() + 1) % 7], "items": []}
            data["days"].append(day)
            data["days"].sort(key=lambda x: x["date"])
        if a.summary:
            day["summary"] = a.summary
        else:
            day.pop("summary", None)
        data["updated"] = today
        save(data)
        print("每日小結", d, "：", a.summary or "（已清除）")

    if a.ids:
        want = parse_ids(a.ids)
        found = set()
        for it in items:
            if it["id"] in want:
                found.add(it["id"])
                it["done"] = not (a.undo or a.redo)
                it["doneAt"] = None if (a.undo or a.redo) else (a.date or today)
                if a.redo:
                    it["redo"] = True
                    it["redoAt"] = a.date or today
                else:
                    it.pop("redo", None)
                    it.pop("redoAt", None)
                    if a.note is None:
                        it.pop("note", None)
                if a.note:
                    it["note"] = a.note
                elif a.note == "":
                    it.pop("note", None)
        missing = sorted(want - found)
        if missing:
            print("找不到編號：", missing, file=sys.stderr)
        data["updated"] = today
        save(data)
        label = "取消：" if a.undo else "標成重做：" if a.redo else "已完成："
        print(label + ", ".join(map(str, sorted(found))))

    done = sum(bool(it["done"] or it.get("redo")) for it in items)  # 重做先算完成
    redo = [it["id"] for it in items if it.get("redo")]
    print(f"總進度 {done}/{len(items)}" + (f"（含待重做 {len(redo)} 題：{redo}）" if redo else ""))
    if a.status:
        for d in data["days"]:
            marks = " ".join(("✓" if it["done"] else "↻" if it.get("redo") else "·") + str(it["id"]) for it in d["items"])
            print(d["date"], d["weekday"], marks)


if __name__ == "__main__":
    main()
