#!/bin/bash
# 只截 hero 区域：用 JS 把 hero 定位到视口内，截固定高度
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

make_view() {
  local w="$1" h="$2" url="$3" out="$4" scroll="$5"
  cat > /tmp/hv.html <<HTML
<!DOCTYPE html><html><head><meta charset="utf-8">
<style>html,body{margin:0;padding:0;overflow:hidden}
iframe{width:${w}px;height:4000px;border:0;position:absolute;top:-${scroll}px;left:0}
</style></head><body>
<iframe src="${url}"></iframe></body></html>
HTML
  "$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars \
    --window-size=$w,$h --screenshot="$out" --virtual-time-budget=7000 \
    "file:///tmp/hv.html" >/dev/null 2>&1
  echo "$out"
}

# hero 高度约 78vh，截其下半部分（文字所在处）
make_view 1024 420 "https://baikal50.cn/index.html" /tmp/hero_desktop.png 330
make_view 390 420 "https://baikal50.cn/index.html" /tmp/hero_mobile.png 200
