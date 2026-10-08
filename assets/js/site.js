/* Maison Môa — interactions (GSAP + ScrollTrigger + Lenis) */
(function () {
  'use strict';
  var d = document, html = d.documentElement, body = d.body;
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var G = window.gsap, ST = window.ScrollTrigger;
  var motion = !!(G && ST) && !reduce;
  var store = {
    get: function (k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} },
    del: function (k) { try { sessionStorage.removeItem(k); } catch (e) {} }
  };
  var WA = '41782238909', MAIL = 'info@maisonmoa.ch';
  var OPENING = new Date('2026-11-02T09:00:00+01:00');
  if (motion) G.registerPlugin(ST);

  /* ---------------------------------------------------------------- défilement doux */
  var lenis = null;
  if (motion && fine && window.Lenis) {
    lenis = new window.Lenis({ duration: 1.15, easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); } });
    lenis.on('scroll', ST.update);
    G.ticker.add(function (t) { lenis.raf(t * 1000); });
    G.ticker.lagSmoothing(0);
  }
  var hdr = $('.hdr');
  var scrollToEl = function (el) {
    var off = -((hdr && hdr.offsetHeight) || 80) - ($('.toc') ? 60 : 10);
    if (lenis) lenis.scrollTo(el, { offset: off, duration: 1.4 });
    else window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY + off, behavior: reduce ? 'auto' : 'smooth' });
  };
  var lock = function (on) { if (lenis) { on ? lenis.stop() : lenis.start(); } body.style.overflow = on ? 'hidden' : ''; };

  /* ---------------------------------------------------------------- en-tête */
  var lastY = window.scrollY, mbar = $('.mbar');
  var onScroll = function () {
    var y = window.scrollY;
    if (hdr) {
      hdr.classList.toggle('scrolled', y > 30);
      var busy = html.classList.contains('menu-open') || !!$('.dd.open');
      if (!busy && y > 500 && y > lastY + 6) hdr.classList.add('hide');
      else if (y < lastY - 6 || y < 500) hdr.classList.remove('hide');
    }
    if (mbar) { var on = y > window.innerHeight * 0.55; mbar.classList.toggle('on', on); html.classList.toggle('mbar-on', on); }
    lastY = y;
  };
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  var dd = $('.dd');
  if (dd) {
    var ddBtn = $('button', dd);
    var setDD = function (on) { dd.classList.toggle('open', on); ddBtn.setAttribute('aria-expanded', on ? 'true' : 'false'); };
    ddBtn.addEventListener('click', function () { setDD(!dd.classList.contains('open')); });
    d.addEventListener('click', function (e) { if (!dd.contains(e.target)) setDD(false); });
    dd.addEventListener('mouseleave', function () { setDD(false); });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape') setDD(false); });
  }
  var burger = $('.burger'), mm = $('.mmenu');
  var setMenu = function (on) {
    html.classList.toggle('menu-open', on); lock(on);
    if (burger) { burger.setAttribute('aria-expanded', on ? 'true' : 'false'); burger.setAttribute('aria-label', on ? 'Fermer le menu' : 'Ouvrir le menu'); }
    if (mm) { mm.setAttribute('aria-hidden', on ? 'false' : 'true'); }
    if (on && motion) G.fromTo($$('.mmenu nav > a, .mmenu .sub a, .mmenu .mfoot'), { y: 30, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: .8, stagger: .035, ease: 'power3.out', delay: .25 });
  };
  if (burger) burger.addEventListener('click', function () { setMenu(!html.classList.contains('menu-open')); });
  $$('.mmenu a').forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });

  /* ---------------------------------------------------------------- tiroir de réservation */
  var book = $('#book'), lastFocus = null;
  var waLink = function (msg) { return 'https://wa.me/' + WA + '?text=' + encodeURIComponent(msg); };
  var openBook = function (soin) {
    if (!book) return;
    lastFocus = d.activeElement;
    var name = $('[data-soin-name]', book);
    name.textContent = soin ? 'Pour : ' + soin : '';
    $('[data-wa]', book).href = waLink('Bonjour Charlène, j’aimerais prendre rendez-vous chez Maison Môa' + (soin ? ' pour le soin « ' + soin + ' »' : '') + '.');
    var f = $('[data-form]', book); f.href = 'contact' + (soin ? '?soin=' + encodeURIComponent(soin) : '') + '#demande';
    book.classList.add('open'); book.setAttribute('aria-hidden', 'false'); lock(true);
    setTimeout(function () { var o = $('.opt', book); if (o) o.focus(); }, 350);
  };
  var closeBook = function () {
    if (!book || !book.classList.contains('open')) return;
    book.classList.remove('open'); book.setAttribute('aria-hidden', 'true'); lock(false);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  };
  d.addEventListener('click', function (e) {
    var t = e.target.closest('[data-book]');
    if (t) { e.preventDefault(); setMenu(false); openBook(t.getAttribute('data-soin') || ''); return; }
    if (e.target.closest('[data-close]')) closeBook();
  });
  d.addEventListener('keydown', function (e) {
    if (!book || !book.classList.contains('open')) return;
    if (e.key === 'Escape') { closeBook(); return; }
    if (e.key === 'Tab') {
      var f = $$('a,button', book), first = f[0], last = f[f.length - 1];
      if (e.shiftKey && d.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && d.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
  $$('a', book || d.createElement('div')).forEach(function (a) { a.addEventListener('click', function () { setTimeout(closeBook, 200); }); });

  /* ---------------------------------------------------------------- formulaires (WhatsApp / e-mail) */
  var fmtDate = function (v) { if (!v) return ''; var p = v.split('-'); return p[2] + '.' + p[1] + '.' + p[0]; };
  $$('form[data-form]').forEach(function (form) {
    var kind = form.getAttribute('data-form'), msgEl = $('.form-msg', form);
    var q = new URLSearchParams(location.search).get('soin');
    if (q && form.soin) { $$('option', form.soin).forEach(function (o) { if (o.textContent === q) form.soin.value = q; }); }
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var via = (e.submitter && e.submitter.value) || 'wa', v = function (n) { var el = form.elements[n]; return el ? (el.value || '').trim() : ''; };
      var need = kind === 'rdv' ? ['nom', 'tel'] : ['de', 'tel'], miss = need.filter(function (n) { return !v(n); });
      if (miss.length) { msgEl.textContent = 'Merci d’indiquer votre ' + (miss[0] === 'tel' ? 'téléphone' : 'nom') + '.'; form.elements[miss[0]].focus(); return; }
      if (!form.elements.ok.checked) { msgEl.textContent = 'Merci de cocher la case de consentement.'; form.elements.ok.focus(); return; }
      msgEl.textContent = '';
      var lines, subject;
      if (kind === 'rdv') {
        var mom = (form.querySelector('input[name=moment]:checked') || {}).value || '';
        subject = 'Demande de rendez-vous · Maison Môa';
        lines = ['Bonjour Charlène,', 'J’aimerais prendre rendez-vous chez Maison Môa.', '',
          v('soin') ? '• Soin : ' + v('soin') : '', v('date') || mom ? '• Date souhaitée : ' + [fmtDate(v('date')), mom].filter(Boolean).join(', ') : '',
          '• Nom : ' + v('nom'), '• Téléphone : ' + v('tel'), v('email') ? '• E-mail : ' + v('email') : '', v('message') ? '\n' + v('message') : '', '', 'Merci et à bientôt !'];
      } else {
        var mt = (form.querySelector('input[name=montant]:checked') || {}).value || '';
        subject = 'Bon cadeau · Maison Môa';
        lines = ['Bonjour Charlène,', 'J’aimerais préparer un bon cadeau Maison Môa.', '',
          mt ? '• Montant : ' + mt : '', v('soin') ? '• Soin : ' + v('soin') : '', '• De la part de : ' + v('de'), v('pour') ? '• Pour : ' + v('pour') : '',
          v('date') ? '• Retrait souhaité : ' + fmtDate(v('date')) : '', '• Téléphone : ' + v('tel'), v('message') ? '\nPetit mot : ' + v('message') : '', '', 'Merci !'];
      }
      var text = lines.filter(function (l, i) { return l !== '' || i < 3 || i === lines.length - 2; }).join('\n');
      if (via === 'mail') location.href = 'mailto:' + MAIL + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(text);
      else window.open(waLink(text), '_blank', 'noopener');
      msgEl.style.color = 'var(--olive)'; msgEl.textContent = 'Votre message est prêt : il ne reste plus qu’à l’envoyer ♡';
    });
  });

  /* ---------------------------------------------------------------- ouverture, horaires du jour */
  var zurich = function () {
    try {
      var p = new Intl.DateTimeFormat('fr-CH', { timeZone: 'Europe/Zurich', weekday: 'short', hour: 'numeric', minute: 'numeric', hour12: false }).formatToParts(new Date());
      var o = {}; p.forEach(function (x) { o[x.type] = x.value; });
      var days = ['lun.', 'mar.', 'mer.', 'jeu.', 'ven.', 'sam.', 'dim.'];
      return { day: Math.max(0, days.indexOf(o.weekday)), h: (+o.hour % 24) + (+o.minute) / 60 };
    } catch (e) { var n = new Date(); return { day: (n.getDay() + 6) % 7, h: n.getHours() + n.getMinutes() / 60 }; }
  };
  var SLOTS = [null, [9, 19], [9, 19], [9, 19], [9, 19], [8, 16], null];
  var NAMES = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'];
  var now = new Date(), z = zurich(), pre = now < OPENING;
  var daysLeft = Math.ceil((OPENING - now) / 86400000);
  $$('[data-hours] li').forEach(function (li) { if (+li.getAttribute('data-day') === z.day) li.classList.add('today'); });
  var status = (function () {
    if (pre) return { open: false, txt: 'Ouverture le lundi 2 novembre 2026 · ' + (daysLeft > 1 ? 'dans ' + daysLeft + ' jours' : daysLeft === 1 ? 'demain' : 'aujourd’hui') };
    var s = SLOTS[z.day];
    if (s && z.h >= s[0] && z.h < s[1]) return { open: true, txt: 'Ouvert maintenant · jusqu’à ' + s[1] + 'h' };
    if (s && z.h < s[0]) return { open: false, txt: 'Fermé · ouvre aujourd’hui à ' + s[0] + 'h' };
    for (var k = 1; k < 8; k++) { var dd2 = (z.day + k) % 7; if (SLOTS[dd2]) return { open: false, txt: 'Fermé · ouvre ' + (k === 1 ? 'demain' : NAMES[dd2]) + ' à ' + SLOTS[dd2][0] + 'h' }; }
    return { open: false, txt: '' };
  })();
  $$('[data-status]').forEach(function (el) { el.classList.toggle('open', status.open); $('span', el).textContent = status.txt; });
  $$('[data-status-text]').forEach(function (el) { el.textContent = status.txt; });
  $$('[data-open-pill]').forEach(function (el) {
    if (pre) el.innerHTML = 'Ouverture le <b>lundi 2 novembre</b> · J-' + Math.max(0, daysLeft);
    else el.textContent = status.txt;
  });

  /* ---------------------------------------------------------------- découpe des titres en lignes */
  var splitLines = function (el) {
    var orig = el.innerHTML, words = [];
    (function walk(node, em) {
      Array.prototype.forEach.call(node.childNodes, function (n) {
        if (n.nodeType === 3) n.textContent.split(/(\s+)/).forEach(function (t) { if (!t) return; words.push(/^\s+$/.test(t) ? { sp: 1 } : { t: t, em: em }); });
        else if (n.nodeName === 'BR') words.push({ br: 1 });
        else walk(n, em || n.nodeName === 'EM');
      });
    })(el, false);
    el.innerHTML = '';
    var spans = [];
    words.forEach(function (w) {
      if (w.sp) { el.appendChild(d.createTextNode(' ')); return; }
      if (w.br) { el.appendChild(d.createElement('br')); spans.push('br'); return; }
      var s = d.createElement('span'); s.className = 'w' + (w.em ? ' em' : ''); s.textContent = w.t; el.appendChild(s); spans.push(s);
    });
    var lines = [], cur = null, top = null;
    spans.forEach(function (s) {
      if (s === 'br') { top = null; return; }
      var t = s.offsetTop;
      if (top === null || Math.abs(t - top) > 5) { cur = []; lines.push(cur); top = t; }
      cur.push(s);
    });
    el.innerHTML = '';
    var inners = lines.map(function (ln) {
      var o = d.createElement('span'), i = d.createElement('span'); o.className = 'ln';
      ln.forEach(function (s, k) { if (k) i.appendChild(d.createTextNode(' ')); i.appendChild(s); });
      o.appendChild(i); el.appendChild(o); return i;
    });
    return { inners: inners, revert: function () { el.innerHTML = orig; } };
  };

  /* ---------------------------------------------------------------- animations */
  var loader = $('.loader'), curtain = $('.curtain');
  var arriving = html.classList.contains('trans');
  store.del('mm-trans');

  var playCurtainOut = function () {
    if (!curtain) return;
    if (!motion) { html.classList.remove('trans'); return; }
    G.fromTo(curtain, { yPercent: 0 }, { yPercent: -100, duration: 1, ease: 'expo.inOut', delay: .05, onComplete: function () { html.classList.remove('trans'); G.set(curtain, { yPercent: 100 }); } });
  };

  var initMotion = function () {
    /* intro du héros */
    var intro = G.timeline({ paused: true });
    var h1 = $('main h1[data-split]');
    if (h1) {
      var sp = splitLines(h1);
      intro.from(sp.inners, { yPercent: 118, duration: 1.3, stagger: .1, ease: 'power4.out', onComplete: sp.revert }, .05);
    }
    var introEls = $$('.hero-copy > :not(h1), [data-intro], .hero-meta').filter(function (el) { return !el.closest('h1'); });
    if (introEls.length) intro.from(introEls, { y: 28, autoAlpha: 0, duration: 1.1, stagger: .08, ease: 'power3.out' }, .3);
    var heroScene = $('.hero .scene');
    if (heroScene) intro.from(heroScene, { scale: 1.06, duration: 2.2, ease: 'power3.out' }, 0);
    html.classList.remove('pre-intro');

    /* préchargeur (1re visite) puis intro */
    var firstVisit = !html.classList.contains('no-loader') && loader;
    store.set('mm-seen', '1');
    if (firstVisit) {
      var use = $('use', loader), len = 3200;
      try { len = Math.ceil($('#mono path').getTotalLength()) || len; } catch (e) {}
      G.set(use, { strokeDasharray: len, strokeDashoffset: len });
      var tl = G.timeline();
      tl.to(use, { strokeDashoffset: 0, duration: 1.6, ease: 'power2.inOut' }, 0)
        .to(use, { fillOpacity: 1, duration: .6, ease: 'power1.out' }, 1.1)
        .from($('.w span', loader), { yPercent: 110, duration: 1, ease: 'power3.out' }, .35)
        .to($('.bar i', loader), { scaleX: 1, duration: 1.5, ease: 'power2.inOut' }, 0)
        .to(loader, { yPercent: -100, duration: 1.1, ease: 'expo.inOut' }, 1.85)
        .add(function () { intro.play(); }, 2.15)
        .set(loader, { display: 'none' });
    } else {
      if (loader) loader.style.display = 'none';
      if (arriving) { playCurtainOut(); G.delayedCall(.35, function () { intro.play(); }); }
      else intro.play();
    }

    /* titres découpés au défilement */
    $$('[data-split]').forEach(function (el) {
      if (el === h1) return;
      G.set(el, { autoAlpha: 0 });
      ST.create({ trigger: el, start: 'top 88%', once: true, onEnter: function () {
        var s = splitLines(el); G.set(el, { autoAlpha: 1 });
        G.from(s.inners, { yPercent: 115, duration: 1.2, stagger: .09, ease: 'power4.out', onComplete: s.revert });
      } });
    });

    /* apparitions */
    var rv = $$('[data-rv]').filter(function (el) { return !el.closest('.hero-copy'); });
    G.set(rv, { autoAlpha: 0, y: 36 });
    ST.batch(rv, { start: 'top 90%', once: true, onEnter: function (els) { G.to(els, { autoAlpha: 1, y: 0, duration: 1.1, stagger: .08, ease: 'power3.out', overwrite: true }); } });

    /* voiles d'images */
    $$('[data-img]').forEach(function (fr) {
      var veil = $('.veil', fr), im = $('img', fr);
      if (!veil) return;
      G.set(veil, { scaleY: 1, transformOrigin: 'top' });
      ST.create({ trigger: fr, start: 'top 90%', once: true, onEnter: function () {
        G.to(veil, { scaleY: 0, duration: 1.3, ease: 'expo.inOut' });
        if (im && !fr.hasAttribute('data-par')) G.fromTo(im, { scale: 1.16 }, { scale: 1, duration: 1.8, ease: 'expo.out' });
      } });
    });
    $$('[data-par]').forEach(function (fr) {
      var im = $('img', fr); if (!im) return;
      G.fromTo(im, { yPercent: -7 }, { yPercent: 7, ease: 'none', scrollTrigger: { trigger: fr, start: 'top bottom', end: 'bottom top', scrub: true } });
    });

    /* lignes de progression des étapes */
    $$('.steps .prog').forEach(function (p) {
      G.to(p, { scaleY: 1, ease: 'none', scrollTrigger: { trigger: p.parentNode, start: 'top 75%', end: 'bottom 60%', scrub: .6 } });
    });

    /* compteurs */
    $$('[data-count]').forEach(function (el) {
      var to = +el.getAttribute('data-count'), o = { v: 0 };
      ST.create({ trigger: el, start: 'top 92%', once: true, onEnter: function () {
        G.to(o, { v: to, duration: 2, ease: 'power3.out', onUpdate: function () { el.textContent = Math.round(o.v); } });
      } });
    });

    /* monogramme dessiné */
    $$('[data-draw]').forEach(function (svg) {
      var u = $('use', svg), len = 3200;
      try { len = Math.ceil($('#mono path').getTotalLength()) || len; } catch (e) {}
      G.set(u, { strokeDasharray: len, strokeDashoffset: len, fillOpacity: 0 });
      ST.create({ trigger: svg, start: 'top 85%', once: true, onEnter: function () {
        G.to(u, { strokeDashoffset: 0, duration: 2.4, ease: 'power2.inOut' });
        G.to(u, { fillOpacity: 1, duration: .9, delay: 1.7 });
      } });
    });

    /* galerie horizontale épinglée */
    var hs = $('.hscroll');
    if (hs && window.innerWidth > 900) {
      var track = $('.hs-track', hs);
      var dist = function () { return Math.max(0, track.scrollWidth - window.innerWidth); };
      hs.classList.add('pinned');
      G.to(track, { x: function () { return -dist(); }, ease: 'none', scrollTrigger: { trigger: hs, start: 'top top', end: function () { return '+=' + dist(); }, pin: true, scrub: .8, invalidateOnRefresh: true } });
    }

    /* sommaire actif */
    var toc = $$('.toc a[href^="#"]');
    toc.forEach(function (a) {
      var t = $(a.getAttribute('href')); if (!t) return;
      ST.create({ trigger: t, start: 'top 55%', end: 'bottom 55%', onToggle: function (self) {
        if (self.isActive) { toc.forEach(function (x) { x.classList.toggle('on', x === a); }); a.scrollIntoView({ block: 'nearest', inline: 'center' }); }
      } });
    });

    /* pied de page */
    var fw = $('.ftr-word');
    if (fw) G.from(fw, { yPercent: 40, autoAlpha: 0, duration: 1.6, ease: 'power3.out', scrollTrigger: { trigger: fw, start: 'top 98%', once: true } });

    window.addEventListener('load', function () { ST.refresh(); });
    setTimeout(function () {
      $$('[data-rv],[data-split]').forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.top < window.innerHeight && r.bottom > 0 && +getComputedStyle(el).opacity < .05) G.to(el, { autoAlpha: 1, y: 0, duration: .6 });
      });
    }, 4000);
  };

  if (motion) {
    var go = function () { try { initMotion(); } catch (err) { console.warn(err); html.classList.remove('pre-intro', 'trans'); if (loader) loader.style.display = 'none'; } };
    var fr = d.fonts && d.fonts.ready ? Promise.race([d.fonts.ready, new Promise(function (r) { setTimeout(r, 1500); })]) : Promise.resolve();
    fr.then(go, go);
  } else {
    html.classList.remove('pre-intro', 'trans');
    if (loader) loader.style.display = 'none';
    store.set('mm-seen', '1');
  }

  /* ---------------------------------------------------------------- liens : ancres & transitions */
  d.addEventListener('click', function (e) {
    var a = e.target.closest('a[href]');
    if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button) return;
    if (a.target === '_blank' || a.hasAttribute('download') || /^(mailto|tel|https?:\/\/wa\.me)/.test(a.getAttribute('href'))) return;
    var url; try { url = new URL(a.href, location.href); } catch (err) { return; }
    if (url.origin !== location.origin) return;
    var same = url.pathname.replace(/\.html$/, '').replace(/\/index$/, '/') === location.pathname.replace(/\.html$/, '').replace(/\/index$/, '/');
    if (same && url.hash) {
      var t = $(url.hash); if (t) { e.preventDefault(); scrollToEl(t); history.replaceState(null, '', url.hash); }
      return;
    }
    if (same && !url.hash && url.search === location.search) { e.preventDefault(); if (lenis) lenis.scrollTo(0); else window.scrollTo(0, 0); return; }
    if (!motion || !curtain) return;
    e.preventDefault();
    store.set('mm-trans', '1');
    G.fromTo(curtain, { yPercent: 100 }, { yPercent: 0, duration: .75, ease: 'expo.inOut', onComplete: function () { location.href = a.href; } });
  });
  window.addEventListener('pageshow', function (e) {
    if (e.persisted && curtain && G) { G.set(curtain, { yPercent: 100 }); html.classList.remove('trans', 'menu-open'); body.style.overflow = ''; if (lenis) lenis.start(); }
  });
  if (location.hash && lenis) { var tgt = $(location.hash); if (tgt) setTimeout(function () { scrollToEl(tgt); }, 500); }

  /* ---------------------------------------------------------------- survol : image qui suit (liste des soins) */
  var hov = $('.hover-img');
  if (hov && fine && motion) {
    var xTo = G.quickTo(hov, 'x', { duration: .6, ease: 'power3' }), yTo = G.quickTo(hov, 'y', { duration: .6, ease: 'power3' });
    var imgs = {};
    $$('.svc-row[data-hover]').forEach(function (row) {
      var src = row.getAttribute('data-hover');
      row.addEventListener('mouseenter', function () {
        if (!imgs[src]) { var im = new Image(); im.src = src; im.alt = ''; hov.appendChild(im); imgs[src] = im; }
        Object.keys(imgs).forEach(function (k) { imgs[k].classList.toggle('on', k === src); });
        hov.classList.add('on');
      });
      row.addEventListener('mouseleave', function () { hov.classList.remove('on'); });
    });
    window.addEventListener('mousemove', function (e) { xTo(e.clientX + 40); yTo(e.clientY); }, { passive: true });
  }

  /* ---------------------------------------------------------------- boutons magnétiques */
  if (fine && motion) {
    $$('.mag').forEach(function (b) {
      var xs = G.quickTo(b, 'x', { duration: .5, ease: 'power3' }), ys = G.quickTo(b, 'y', { duration: .5, ease: 'power3' });
      b.addEventListener('mousemove', function (e) { var r = b.getBoundingClientRect(); xs((e.clientX - r.left - r.width / 2) * .22); ys((e.clientY - r.top - r.height / 2) * .32); });
      b.addEventListener('mouseleave', function () { xs(0); ys(0); });
    });
  }
})();
