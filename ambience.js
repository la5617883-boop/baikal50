/* 贝加尔湖50径 · 环境音播放器
   点击才播，绝不自动播。不加载音频文件直到首次点击（lazy），
   因此对页面体积、加载速度、SEO、AI 爬虫均零影响。

   2026-10-19 修复：原实现用 <source> 子元素 + preload='none'，
   点击 play() 后 Chrome 不发起请求（readyState 一直 0、无网络请求、Promise 永不落定）。
   改为：点击时才创建 src（直接设 src 属性，兼容 iOS/微信内置浏览器），
   失败自动回退到 mp3，并显式调用 load()。 */

(function () {
  'use strict';

  var SOURCES = ['/audio/ambience-loop.m4a', '/audio/ambience-loop.mp3'];

  function build() {
    var btn = document.createElement('button');
    btn.className = 'baikal-amb';
    btn.type = 'button';
    btn.setAttribute('aria-label', '播放贝加尔湖西岸环境音');
    btn.setAttribute('aria-pressed', 'false');
    btn.title = '播放／暂停　贝加尔湖西岸环境音';
    btn.innerHTML =
      '<svg class="baikal-amb__icon" viewBox="0 0 24 24" fill="none" ' +
      'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" ' +
      'stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M3 9v6h4l5 4V5L7 9H3z"/>' +
      '<path class="baikal-amb__wave" d="M16.5 8.5a5 5 0 0 1 0 7"/>' +
      '</svg>' +
      '<span class="baikal-amb__bars" aria-hidden="true"><i></i><i></i><i></i><i></i></span>' +
      '<span class="baikal-amb__label">贝加尔湖　环境音</span>';

    var audio = null;
    var srcIndex = 0;
    var fadeTimer = null;

    function setVol(el, v) {
      try { el.volume = v; } catch (e) { /* iOS 忽略 volume，不报错 */ }
    }

    function fadeIn(el) {
      if (fadeTimer) clearInterval(fadeTimer);
      setVol(el, 0);
      var target = 0.55;
      fadeTimer = setInterval(function () {
        var v = 0;
        try { v = el.volume; } catch (e) { v = target; }
        if (v + 0.05 >= target) { setVol(el, target); clearInterval(fadeTimer); fadeTimer = null; }
        else { setVol(el, Math.min(target, v + 0.05)); }
      }, 60);
    }

    function fadeOut(el, cb) {
      if (fadeTimer) clearInterval(fadeTimer);
      fadeTimer = setInterval(function () {
        var v = 0;
        try { v = el.volume; } catch (e) { v = 0.06; }
        if (v - 0.06 <= 0) {
          setVol(el, 0);
          clearInterval(fadeTimer); fadeTimer = null;
          el.pause();
          if (cb) cb();
        } else { setVol(el, Math.max(0, v - 0.06)); }
      }, 45);
    }

    /* 首次点击时才创建 audio 并赋 src —— 保证未点击前零请求 */
    function ensureAudio() {
      if (audio) return audio;
      audio = new Audio();
      audio.loop = true;
      audio.preload = 'auto';          // 此时用户已点击，允许加载
      setVol(audio, 0.55);
      audio.setAttribute('playsinline', '');
      audio.setAttribute('webkit-playsinline', '');

      audio.addEventListener('playing', function () {
        btn.classList.add('is-playing');
        btn.setAttribute('aria-pressed', 'true');
        btn.title = '暂停　贝加尔湖西岸环境音';
        fadeIn(audio);
      });
      audio.addEventListener('pause', function () {
        btn.classList.remove('is-playing');
        btn.setAttribute('aria-pressed', 'false');
        btn.title = '播放　贝加尔湖西岸环境音';
      });
      audio.addEventListener('error', function () {
        // m4a 不行就退到 mp3；两个都不行才隐藏按钮
        if (srcIndex < SOURCES.length - 1) {
          srcIndex++;
          loadSrc();
          var p = audio.play();
          if (p && p.catch) { p.catch(function () {}); }
        } else {
          btn.style.display = 'none';
        }
      });

      loadSrc();
      return audio;
    }

    function loadSrc() {
      audio.src = SOURCES[srcIndex];
      try { audio.load(); } catch (e) {}
    }

    btn.addEventListener('click', function () {
      var a = ensureAudio();
      if (!a.paused) { fadeOut(a); return; }

      var marked = false;
      function mark() {
        if (marked) return;
        marked = true;
        btn.classList.add('is-playing');
        btn.setAttribute('aria-pressed', 'true');
        btn.title = '暂停　贝加尔湖西岸环境音';
      }

      /* 微信内 iOS：WeixinJSBridge.invoke('getNetworkType') 是官方推荐的“解锁音频”手法，
         必须在 click 回调的同步栈里发起，否则会丢掉用户手势上下文（NotAllowedError）。 */
      function wxUnlock(next) {
        try {
          if (window.WeixinJSBridge && window.WeixinJSBridge.invoke) {
            window.WeixinJSBridge.invoke('getNetworkType', {}, function () { next(); });
            return true;
          }
        } catch (e) {}
        return false;
      }

      function attempt(depth) {
        var p;
        try {
          p = a.play();
        } catch (e) {
          return fallback(depth);
        }
        if (p && p.then) {
          p.then(mark).catch(function () { fallback(depth); });
        } else {
          mark();
        }
      }

      function fallback(depth) {
        if (depth === 0) {
          /* 首次被拒：走微信解锁，成功后立刻再播一次 */
          if (wxUnlock(function () { attempt(1); })) return;
          try { a.load(); } catch (e) {}
          setTimeout(function () { attempt(2); }, 120);
          return;
        }
        if (depth === 1) {
          try { a.load(); } catch (e) {}
          attempt(2);
          return;
        }
        /* 兜底：保持按钮可再次点击，不隐藏 */
      }

      /* ① 第一件事：在同步栈里直接播，抢住用户手势 */
      attempt(0);
    });

    document.body.appendChild(btn);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
