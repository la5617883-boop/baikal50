#!/bin/bash
# 真实视口宽度下截 hero 区域（本地文件已改，直接测本地）
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# 本地服务已在 8899
for W in 360 390 500 600 700 1024; do
  "$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars \
    --window-size=$W,900 --screenshot="/tmp/vp_$W.png" \
    --virtual-time-budget=6000 "http://127.0.0.1:8899/index.html" >/dev/null 2>&1
  echo "视口 $W -> /tmp/vp_$W.png"
done
