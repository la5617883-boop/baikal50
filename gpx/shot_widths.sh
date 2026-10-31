#!/bin/bash
# 多宽度实测 hero-def 折行情况（用 Chrome headless + JS 注入量测）
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for W in 390 600 700 760 1024; do
  "$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars \
    --window-size=$W,900 --screenshot="/tmp/hero_$W.png" \
    --virtual-time-budget=6000 "https://baikal50.cn/index.html" >/dev/null 2>&1
  echo "已截 $W px -> /tmp/hero_$W.png"
done
