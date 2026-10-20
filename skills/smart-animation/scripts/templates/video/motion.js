/* motion.js - seek-safe motion helpers for video-loop scenes (smart-animation).
 * Loaded once by index.html after GSAP; every scene's <template> script can call them.
 * Every helper is a pure function of timeline time: no Date.now(), no random, no real-time playback.
 * Lessons behind each helper are in references/wiki/video/loop/reference-assets.md.
 */
(function (w) {
  // Closed-form damped spring: position at time t (s). zeta < 1 overshoots, omega sets speed. 0 -> 1.
  function spring(t, zeta, omega) {
    if (t <= 0) return 0;
    var wd = omega * Math.sqrt(1 - zeta * zeta);
    return 1 - Math.exp(-zeta * omega * t) * (Math.cos(wd * t) + (zeta * omega / wd) * Math.sin(wd * t));
  }
  // GSAP ease over a tween of dur seconds. Keep dur >= ~4 / (zeta * omega) so the spring settles.
  function springEase(dur, zeta, omega) {
    return function (p) { return p >= 1 ? 1 : spring(p * dur, zeta, omega); };
  }
  var SPRING = { snappy: [0.75, 22], settle: [0.9, 14], playful: [0.5, 18] };
  // Smoothstep: for slow pushes, fades and blur, where a spring's overshoot would read as a glitch.
  function glide(p) { return p * p * (3 - 2 * p); }

  // Words resolve in place, left to right: blur and opacity glide (never overshoot, so a later word can
  // never look sharper than an earlier one), the small rise springs. Time the gap to the voice.
  function words(tl, selector, t, gap, opt) {
    opt = opt || {};
    var dur = opt.dur || 0.55;
    document.querySelectorAll(selector).forEach(function (el, i) {
      var at = t + i * gap;
      tl.fromTo(el, { opacity: 0, filter: 'blur(' + (opt.blur || 10) + 'px)' },
        { opacity: 1, filter: 'blur(0px)', duration: dur, ease: glide }, at);
      tl.fromTo(el, { y: opt.rise || 14 }, { y: 0, duration: dur, ease: springEase(dur, 0.85, 16) }, at);
    });
  }

  // A number counts to `to` on a settling spring; fmt(v) formats it (use a monospace font).
  function count(tl, el, from, to, t, dur, fmt) {
    var o = { v: from };
    tl.to(o, { v: to, duration: dur, ease: springEase(dur, 0.95, 9),
      onUpdate: function () { el.textContent = fmt(o.v); } }, t);
  }

  // Constant-velocity drift for camera pushes. An eased push stops at both ends, and two eased pushes
  // chained across a cut read as a stall right at the cut; a drift keeps moving through it.
  function drift(p) { return p; }
  // Slow push on the scene's stage. Chain scenes so each starts where the last ended
  // (A: 1 -> 1.02, B: 1.02 -> 1): a push that restarts at 1 snaps visibly at every cut.
  function push(tl, selector, dur, from, to) {
    tl.fromTo(selector, { scale: from }, { scale: to, duration: dur, ease: drift }, 0);
  }

  // Morph an element from its own box into another box (x, y, w, h in the same parent space) with
  // transforms only: tweening left/top/width/height fails `hyperframes check --strict`.
  function morph(tl, el, box, t, dur, extra) {
    var r = { x: el.offsetLeft, y: el.offsetTop, w: el.offsetWidth, h: el.offsetHeight };
    var to = { transformOrigin: '0 0', x: box.x - r.x, y: box.y - r.y, scaleX: box.w / r.w, scaleY: box.h / r.h,
      duration: dur, ease: springEase(dur, 0.85, 12) };
    for (var k in (extra || {})) to[k] = extra[k];
    tl.to(el, to, t);
  }

  // The accent cursor always moves to a target (a word, a row, a bar), never parks on text.
  function lead(tl, cursor, x, y, t, dur) {
    tl.to(cursor, { x: x, y: y, duration: dur || 0.5, ease: springEase(dur || 0.5, 0.85, 14) }, t);
  }

  w.motion = { spring: spring, springEase: springEase, SPRING: SPRING, glide: glide, drift: drift, words: words,
    count: count, push: push, morph: morph, lead: lead };
})(window);
