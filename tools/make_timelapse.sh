#!/bin/bash
# make_timelapse.sh 原檔 日期 每格秒數 日期字 備註　（面板只顯示時長，不顯示時間）
set -e
SRC=$1; DT=$2; IV=$3; DS=$4; NOTE=$5
cd "$(dirname "$0")"
L=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SRC")
python3 -c "import json,sys;json.dump({'dur':$L,'interval':$IV,'start':None,'date':sys.argv[1],'note':sys.argv[2]},open('p_$DT.json','w'),ensure_ascii=False)" "$DS" "$NOTE"
F=$(python3 -c "print(max(0,$L-2))")
OUT=/home/claude/progress/videos/$DT
python3 overlay.py raw p_$DT.json | ffmpeg -v error -y -i "$SRC" -f rawvideo -pix_fmt rgba -s 700x210 -r 30000/1001 -i - -i /home/claude/progress/assets/bgm.m4a \
 -filter_complex "[0:v]scale=-2:720[b];[1:v]scale=470:-1[o];[b][o]overlay=W-w-26:24:shortest=1[v]" -map "[v]" -map 2:a \
 -c:v libx264 -preset veryfast -crf 26 -af "afade=t=out:st=$F:d=2" -c:a aac -b:a 96k -t $L -movflags +faststart $OUT.tmp.mp4
mv $OUT.tmp.mp4 $OUT.mp4
ffmpeg -v error -y -ss 20 -i $OUT.mp4 -frames:v 1 -vf scale=960:-2 -q:v 4 $OUT.jpg
ls -la $OUT.mp4
