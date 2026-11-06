# 物奧進度網站

靜態網站（GitHub Pages，從 `main` 分支根目錄發佈）。
- `index.html`：頁面，讀取 `data.json` 顯示。
- `data.json`：所有題目與完成狀態（唯一資料來源）。
- `mark.py`：修改完成狀態的工具。

## 使用者說「XX 題完成了」時

1. 用 `mark.py` 修改，不要手動編輯 JSON：
   - `python3 mark.py 63 75-78` → 標成完成（完成日期預設今天，台灣時間）
   - `python3 mark.py 63 --date 2026-11-04` → 指定完成日期
   - `python3 mark.py 63 --redo` → 標成「重做」（網站上黃色 ↻，不算完成；之後標完成會自動清掉重做）
   - `python3 mark.py 63 --undo` → 取消完成 / 取消重做
   - `python3 mark.py --status` → 查看進度
   - 使用者說「今天的都完成了」→ 先 `--status` 找出今天那天的編號再標記。
   - 數字指的是每行最前面的「編號」（例如 63、75），不是 Q 幾。
2. commit 並直接 push 到 `main`（網站從 main 發佈，使用者已同意直接推 main）：
   `git add data.json && git commit -m "進度：完成 #63 #75" && git push origin main`
3. 回報目前總進度。網站約 1 分鐘後更新。

## 新增 / 調整題目
直接編輯 `data.json` 的 `days` 陣列，每題格式：
`{"id": 編號, "lesson": "L16", "topic": "熱量", "q": "Q8", "diff": "E|M|H|空字串", "done": false, "doneAt": null}`
（標成重做的題目另有 `"redo": true, "redoAt": "日期"`，由 mark.py 管理）
