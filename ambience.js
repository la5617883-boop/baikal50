/* 贝加尔湖50径 · 环境音播放器
   点击才播，绝不自动播。不加载音频文件直到首次点击(lazy)，
   因此对页面体积、加载速度、SEO、AI 爬虫均零影响。 */
(function () {
  'use strict';

  var SRC = [
    { src: '/audio/ambience-loop.m4a', type: 'audio/mp4' },
    { src: '/audio/ambience-loop.mp3', type: 'audio/mpeg' }
  ];

  // 尊重"减少动态效果"偏好的同时保留功能; 无 JS 环境直接不显示按钮
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
    var ready = false;

    function initAudio() {
      if (audio) return;
      audio = new Audio();
      for (var i = 0; i < SRC.length; i++) {
        var s = document.createElement('source');
        s.src = SRC[i].src;
        s.type = SRC[i].type;
        audio.appendChild(s);
      }
      audio.loop = false;       // 原时长完整音轨,放完自然停; 再点可重播
      audio.preload = 'none';   // 关键：不点不加载
      audio.volume = 0.55;      // 温和,不抢戏
      // 淡入,避免突兀
      audio.addEventListener('playing', function () {
        fadeIn(audio);
      });
      // 播完复位按钮状态
      audio.addEventListener('ended', function () {
        btn.classList.remove('is-playing');
        btn.setAttribute('aria-pressed', 'false');
        btn.title = '播放　贝加尔湖西岸环境音';
      });
      audio.addEventListener('error', function () {
        btn.style.display = 'none';  // 播放失败就藏起来,不留死按钮
      });
    }

    var fadeTimer = null;
    function fadeIn(el) {
      if (fadeTimer) clearInterval(fadeTimer);
      el.volume = 0;
      var target = 0.55, step = 0.05;
      fadeTimer = setInterval(function () {
        if (el.volume + step >= target) { el.volume = target; clearInterval(fadeTimer); fadeTimer = null; }
        else { el.volume = Math.min(target, el.volume + step); }
      }, 60);
    }
    function fadeOut(el, cb) {
      if (fadeTimer) clearInterval(fadeTimer);
      var step = 0.06;
      fadeTimer = setInterval(function () {
        if (el.volume - step <= 0) {
          el.volume = 0; clearInterval(fadeTimer); fadeTimer = null;
          el.pause();
          if (cb) cb();
        } else { el.volume = Math.max(0, el.volume - step); }
      }, 45);
    }

    btn.addEventListener('click', function () {
      initAudio();
      if (!ready) { ready = true; }
      // 已播完的,再点从头开始
      if (audio.ended) { audio.currentTime = 0; }
      var playing = !audio.paused;
      if (playing) {
        btn.classList.remove('is-playing');
        btn.setAttribute('aria-pressed', 'false');
        btn.title = '播放　贝加尔湖西岸环境音';
        fadeOut(audio);
      } else {
        var p = audio.play();
        if (p && p.catch) {
          p.then(function () {
            btn.classList.add('is-playing');
            btn.setAttribute('aria-pressed', 'true');
            btn.title = '暂停　贝加尔湖西岸环境音';
          }).catch(function () {
            /* 播放被拒(极少见,用户已点击不受自动播放策略限制) */
          });
        } else {
          btn.classList.add('is-playing');
          btn.setAttribute('aria-pressed', 'true');
        }
      }
    });

    document.body.appendChild(btn);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
