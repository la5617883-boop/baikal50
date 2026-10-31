#!/bin/bash
# 多宽度下测 hero-def 的实际折行数（用 Chrome --dump-dom 不行，改用截图高度反推不方便）
# 改为：注入 script 到 iframe 内量测，结果写到 document.title，再用 dump-dom 读取
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for W in 390 500 600 699 700 760 900 1024 1280; do
cat > /tmp/m_$W.html <<HTML
<!DOCTYPE html><html><head><meta charset="utf-8"><style>html,body{margin:0}
iframe{width:${W}px;height:900px;border:0}</style></head><body>
<iframe id="f" src="http://127.0.0.1:8899/index.html"></iframe>
<script>
document.getElementById('f').onload = function(){
  var d = this.contentDocument, w = this.contentWindow;
  var el = d.querySelector('.hero-def');
  if(!el){ document.title='NODATA'; return; }
  var cs = w.getComputedStyle(el), r = el.getBoundingClientRect();
  var lines = Math.round(r.height / parseFloat(cs.lineHeight));
  document.title = W_LABEL + '|ws=' + cs.whiteSpace + '|lines=' + lines + '|w=' + Math.round(r.width);
};
</script></body></html>
HTML
sed -i '' "s/W_LABEL/$W/" /tmp/m_$W.html
  R=$("$CHROME" --headless --disable-gpu --no-sandbox --dump-dom \
    --virtual-time-budget=6000 "file:///tmp/m_$W.html" 2>/dev/null \
    | grep -o '<title>[^<]*</title>' | sed 's/<[^>]*>//g')
  echo "$W px  ->  $R"
done
