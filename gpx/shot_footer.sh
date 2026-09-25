#!/bin/bash
# 生成一个只显示页脚的临时 HTML（把首页滚到底），改用 JS 定位截图
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W=760
H=520

# 用 data URL 包装：iframe 加载首页并滚到底部
cat > /tmp/footer_view.html <<'HTML'
<!DOCTYPE html><html><head><meta charset="utf-8">
<style>html,body{margin:0;padding:0;background:#faf9f7}
iframe{width:760px;height:12000px;border:0;position:absolute;top:-11480px;left:0}
</style></head><body>
<iframe src="https://baikal50.cn/index.html" onload="this.contentWindow.scrollTo(0,999999)"></iframe>
</body></html>
HTML

"$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars \
  --window-size=760,$H --screenshot=/tmp/footer_only.png \
  --virtual-time-budget=9000 "file:///tmp/footer_view.html" >/dev/null 2>&1
echo "saved /tmp/footer_only.png"
