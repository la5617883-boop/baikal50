#!/bin/bash
# 用 Chrome headless 截图指定 URL，并裁切出页脚区域
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

shot_footer() {
  local url="$1" out="$2"
  "$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars \
    --window-size=760,1000 --screenshot="$out" --virtual-time-budget=6000 \
    "$url" >/dev/null 2>&1
  echo "saved: $out"
}

shot_full() {
  local url="$1" out="$2" h="$3"
  "$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars \
    --window-size=760,$h --screenshot="$out" --virtual-time-budget=6000 \
    "$url" >/dev/null 2>&1
  echo "saved: $out"
}

shot_full "https://baikal50.cn/license.html" /tmp/baikal_license.png 2100
