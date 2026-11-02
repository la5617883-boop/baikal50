/* 贝加尔湖50径 · 小贝（AI 替身）对话逻辑 —— 与首页同一套 */
(function(){
  var API='https://ai.baikal50.cn/api/chat';
  var btn=document.getElementById('bai-btn');
  var wrap=document.getElementById('bai-wrap');
  var log=document.getElementById('bai-log');
  var q=document.getElementById('bai-q');
  var send=document.getElementById('bai-send');
  var closeBtn=document.getElementById('bai-close');
  if(!btn||!wrap||!log) return;
  var hist=[], busy=false, opened=false;

  function bubble(cls, text){
    var d=document.createElement('div');
    d.className='m '+cls; d.textContent=text;
    log.appendChild(d); log.scrollTop=log.scrollHeight; return d;
  }
  function bubbleHTML(cls, html){
    var d=document.createElement('div');
    d.className='m '+cls; d.innerHTML=html;
    log.appendChild(d); log.scrollTop=log.scrollHeight; return d;
  }
  function setBusy(v){ busy=v; send.disabled=v; send.textContent=v?'…':'发送'; }

  function open(){
    wrap.classList.add('on'); wrap.setAttribute('aria-hidden','false');
    document.body.style.overflow='hidden';
    if(!opened){
      opened=true;
      bubbleHTML('it wide',
        '<div>这一页是这条线的实地记录，想细看线路可以走<a href="/route-3d.html">云上 3D</a></div>' +
        '<div>如果您对难度有疑虑，可以试下<a href="/planner.html">行程规划器</a>呦</div>');
    }
    setTimeout(function(){ q.focus(); }, 200);
  }
  function close(){
    wrap.classList.remove('on'); wrap.setAttribute('aria-hidden','true');
    document.body.style.overflow='';
  }

  function ask(text){
    text=(text||'').trim();
    if(!text||busy) return;
    q.value=''; q.style.height='auto';
    bubble('me', text);
    hist.push({role:'user',content:text});
    if(hist.length>8) hist=hist.slice(-8);
    setBusy(true);
    var wait=bubble('th','正在想…');
    var ctrl=new AbortController();
    var timer=setTimeout(function(){ ctrl.abort(); }, 45000);
    fetch(API,{
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({messages:hist}), signal:ctrl.signal
    }).then(function(r){ clearTimeout(timer); if(!r.ok) throw new Error('HTTP '+r.status); return r.json(); })
      .then(function(d){
        wait.remove();
        var a=d.answer||'我没能组织出答案。可以直接问领队：微信 youla7982。';
        bubble('it', a);
        hist.push({role:'assistant',content:a});
        if(hist.length>8) hist=hist.slice(-8);
      })
      .catch(function(e){
        clearTimeout(timer); wait.remove();
        bubble('it', (e&&e.name==='AbortError')
          ? '这一步等太久没回来（网络慢）。可以直接问领队：微信 youla7982，或者再发一次。'
          : '连接出了点问题。可以直接问领队：微信 youla7982 ｜ 电话 18618375879。');
      })
      .then(function(){ setBusy(false); });
  }

  btn.addEventListener('click', open);
  closeBtn.addEventListener('click', close);
  document.getElementById('bai-mask').addEventListener('click', close);
  document.addEventListener('keydown', function(e){ if(e.key==='Escape' && wrap.classList.contains('on')) close(); });
  send.addEventListener('click', function(){ ask(q.value); });
  q.addEventListener('keydown', function(e){
    if(e.key==='Enter' && !e.shiftKey && !e.isComposing){ e.preventDefault(); ask(q.value); }
  });
  q.addEventListener('input', function(){ q.style.height='auto'; q.style.height=Math.min(q.scrollHeight,90)+'px'; });
  Array.prototype.forEach.call(document.querySelectorAll('#bai-tips button'), function(b){
    b.addEventListener('click', function(){ ask(b.textContent); });
  });
})();
