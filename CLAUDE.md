# 物奧進度網站

靜態網站（GitHub Pages，從 `main` 分支根目錄發佈）。
- `index.html`：頁面，讀取 `data.json` 顯示。
- `data.json`：所有題目與完成狀態（唯一資料來源）。
- `mark.py`：修改完成狀態的工具。

## 使用者說「XX 題完成了」時

1. 用 `mark.py` 修改，不要手動編輯 JSON：
   - `python3 mark.py 63 75-78` → 標成完成（完成日期預設今天，台灣時間）
   - `python3 mark.py 63 --date 2026-11-04` → 指定完成日期
   - `python3 mark.py 63 --redo` → 標成「重做」（網站上黃色 ↻，先算進完成數；之後標完成會自動清掉重做）
   - `python3 mark.py 63 --undo` → 取消完成 / 取消重做
   - `python3 mark.py --status` → 查看進度
   - 使用者說「今天的都完成了」→ 先 `--status` 找出今天那天的編號再標記。
   - 數字指的是每行最前面的「編號」（例如 63、75），不是 Q 幾。
   - 第二期影片編號 901–924（901 = LEC24、902 = LEC25 … 912 = LEC35-1、913 = LEC35-2 … 924 = LEC46）。使用者說「看完 LEC27」→ 標 904。
2. commit 並直接 push 到 `main`（網站從 main 發佈，使用者已同意直接推 main）：
   `git add data.json && git commit -m "進度：完成 #63 #75" && git push origin main`
3. 回報目前總進度。網站約 1 分鐘後更新。

## 新增 / 調整題目
直接編輯 `data.json` 的 `days` 陣列，每題格式：
`{"id": 編號, "lesson": "L16", "topic": "熱量", "q": "Q8", "diff": "E|M|H|空字串", "done": false, "doneAt": null}`
可選欄位：`"note": "附註"`（顯示在題目下方，可用 `mark.py --note` 設定）；日期區間用 day 的 `"dateEnd"`。
（標成重做的題目另有 `"redo": true, "redoAt": "日期"`，由 mark.py 管理）

## 每日學習縮時影片
- 影片存在使用者 Google Drive 資料夾「物奧縮時錄影」（ID `1HTqCFjg44NhjZvueX2JFfL5FUU-eajJE`，https://drive.google.com/drive/folders/1HTqCFjg44NhjZvueX2JFfL5FUU-eajJE ），資料夾設為「知道連結的任何人可檢視」。
- 使用者說「今天的影片傳好了」時：
  1. 用 Google Drive 工具搜尋 `parentId = '1HTqCFjg44NhjZvueX2JFfL5FUU-eajJE' and mimeType contains 'video/'`（依 modifiedTime 排序），找到當天的檔案 ID。
  2. `python3 video.py today <檔案ID或連結> [--title "今天內容"]`（指定日期就把 today 換成 2026-11-09）
  3. commit + push 到 main。
- 也支援 YouTube 連結。`python3 video.py --list` 列出、`--remove 日期` 刪除。
- 網站：上方「每日學習縮時」橫列 + 每天卡片上的「▶ 影片」按鈕，點開彈窗播放。
