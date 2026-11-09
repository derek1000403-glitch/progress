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
   - 第二期習題編號 1001–1099（lesson 欄位為「二期LECxx」，note 標「必做」或「建議（Easy）」）。使用者說題號時用「二期 LEC25 P03」這種講法，先在 data.json 找對應 id。
     1001–1005 LEC23｜1006–1011 LEC24｜1012–1019 LEC25｜1020–1025 LEC26｜1026–1031 LEC27｜1032–1039 LEC34｜1040–1046 LEC35(表面張力)｜1047–1054 LEC35(站在水上)｜1055–1067 LEC36｜1068–1078 LEC37｜1079–1099 LEC38｜1100 LEC26 P09（建議）
2. commit 並直接 push 到 `main`（網站從 main 發佈，使用者已同意直接推 main）：
   `git add data.json && git commit -m "進度：完成 #63 #75" && git push origin main`
3. 回報目前總進度。網站約 1 分鐘後更新。

## 新增 / 調整題目
直接編輯 `data.json` 的 `days` 陣列，每題格式：
`{"id": 編號, "lesson": "L16", "topic": "熱量", "q": "Q8", "diff": "E|M|H|空字串", "done": false, "doneAt": null}`
可選欄位：`"note": "附註"`（顯示在題目下方，可用 `mark.py --note` 設定）；日期區間用 day 的 `"dateEnd"`。
（標成重做的題目另有 `"redo": true, "redoAt": "日期"`，由 mark.py 管理）

## 每日學習縮時影片
- **主要方式：影片放在網站裡（`videos/日期.mp4` + `videos/日期.jpg` 封面）**，用網站自己的 `<video>` 播放器（進度條在下面、iPhone 可全螢幕）。Google Drive 的嵌入播放器在 iPhone 上進度條跑到上面、畫面偏低，使用者不要那種。
- 使用者在對話裡直接傳影片檔時：
  1. `ffprobe` 看大小。GitHub 單檔上限 100 MB，目標 ≤ 40 MB：
     - 已經夠小（例如 720p、~25 MB）→ 只重新封裝：`ffmpeg -i 原檔 -c copy -movflags +faststart videos/2026-11-10.mp4`
     - 太大 → 壓縮：`ffmpeg -i 原檔 -vf scale=-2:720 -c:v libx264 -preset veryfast -crf 26 -c:a aac -b:a 96k -movflags +faststart videos/日期.mp4`
  2. 封面：`ffmpeg -ss 20 -i videos/日期.mp4 -frames:v 1 -vf scale=960:-2 -q:v 4 videos/日期.jpg`
  3. `python3 video.py 日期 videos/日期.mp4 --title "今天內容"`（舊影片的標題沿用）
  4. `git add videos data.json && git commit && git push origin main`
- 這個工作環境的網路下載不到 Google Drive 檔案，所以要請使用者直接把檔案傳到對話。
- 原檔仍在使用者 Google Drive 資料夾「物奧縮時錄影」（ID `1HTqCFjg44NhjZvueX2JFfL5FUU-eajJE`）。若只給 Drive 連結/ID 或 YouTube 連結，`video.py` 也接受，網站會改用嵌入播放器。
- `python3 video.py --list` 列出、`--remove 日期` 刪除。
- 網站是月曆版面：影片縮圖顯示在當天的日期格裡（一天一部，video.py 同一天會取代舊的），點縮圖開大播放器。
