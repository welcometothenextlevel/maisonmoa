# -*- coding: utf-8 -*-
"""Génère le site statique Maison Môa à la racine du dépôt : python3 _build/build.py"""
import html, json, os, re, sys
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import *  # noqa
from PIL import Image

OUT = ROOT
IMG = os.path.join(ROOT, 'assets', 'img')
E = lambda s: html.escape(str(s), quote=False)
A = lambda s: html.escape(str(s), quote=True)
VER = '7'

def chf(n, prefix=''):
    return f'{prefix}CHF {n}.–'

_dims = {}
def dims(name):
    if name not in _dims:
        with Image.open(os.path.join(IMG, name + '.webp')) as im:
            _dims[name] = im.size
    return _dims[name]

def img(name, alt, sizes='(max-width: 900px) 100vw, 50vw', cls='', eager=False, lazy=True):
    w, h = dims(name)
    mw = 820 if os.path.exists(os.path.join(IMG, name + '-m.webp')) else None
    srcset = f' srcset="assets/img/{name}-m.webp 820w, assets/img/{name}.webp {w}w" sizes="{sizes}"' if mw else ''
    load = 'fetchpriority="high"' if eager else ('loading="lazy"' if lazy else '')
    c = f' class="{cls}"' if cls else ''
    return f'<img src="assets/img/{name}.webp"{srcset} width="{w}" height="{h}" alt="{A(alt)}" {load} decoding="async"{c}>'

def frame(name, alt, kind='tall', par=True, sizes='(max-width: 900px) 100vw, 50vw', extra='', lazy=True):
    p = ' data-par' if par else ''
    return f'<figure class="frame {kind}" data-img{p}{extra}>{img(name, alt, sizes, "par" if par else "", lazy=lazy)}<i class="veil" aria-hidden="true"></i></figure>'

# ---------------------------------------------------------------- icônes
I = dict(
    arrow='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M3.5 12h16M13.5 5.5 20 12l-6.5 6.5"/></svg>',
    ne='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M6 18 18 6M8 6h10v10"/></svg>',
    down='<svg viewBox="0 0 12 8" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="m1 1.5 5 5 5-5"/></svg>',
    wa='<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.16-.17.2-.35.22-.64.08-.3-.15-1.26-.47-2.39-1.48-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.6.13-.14.3-.35.45-.52.15-.18.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.61-.92-2.2-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.07c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.7.63.71.22 1.36.19 1.87.12.57-.09 1.76-.72 2-1.42.25-.69.25-1.29.18-1.41-.08-.13-.28-.2-.57-.35M12.05 21.79h-.01a9.87 9.87 0 0 1-5.03-1.38l-.36-.21-3.74.98 1-3.65-.24-.37a9.86 9.86 0 0 1-1.51-5.26c0-5.45 4.44-9.88 9.89-9.88 2.64 0 5.12 1.03 6.99 2.9a9.83 9.83 0 0 1 2.89 6.99c0 5.45-4.44 9.88-9.88 9.88m8.41-18.3A11.82 11.82 0 0 0 12.05 0C5.5 0 .16 5.34.16 11.89c0 2.1.55 4.14 1.59 5.95L.06 24l6.3-1.65a11.88 11.88 0 0 0 5.68 1.45h.01c6.55 0 11.89-5.34 11.89-11.89a11.82 11.82 0 0 0-3.48-8.41Z"/></svg>',
    phone='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M5.2 3.5h3.2l1.6 4.2-2.1 1.4a11 11 0 0 0 7 7l1.4-2.1 4.2 1.6v3.2a2 2 0 0 1-2.2 2A17 17 0 0 1 3.2 5.7a2 2 0 0 1 2-2.2Z"/></svg>',
    mail='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><rect x="3" y="5.5" width="18" height="13" rx="1.5"/><path d="m3.5 6.5 8.5 6.5 8.5-6.5"/></svg>',
    cal='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15" rx="1.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>',
    clock='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>',
    pin='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M12 21s-6.5-6.1-6.5-11.2a6.5 6.5 0 0 1 13 0C18.5 14.9 12 21 12 21Z"/><circle cx="12" cy="9.8" r="2.3"/></svg>',
    car='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M4 16.5V12l2-5h12l2 5v4.5M4 16.5h16M4 16.5V19h2.5v-2.5M17.5 16.5V19H20v-2.5M7 13.5h1M16 13.5h1"/></svg>',
    bus='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><rect x="5" y="3.5" width="14" height="14" rx="2"/><path d="M5 11h14M8 17.5V20M16 17.5V20M8.5 14.5h.5M15 14.5h.5"/></svg>',
    card='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><rect x="3" y="6" width="18" height="12.5" rx="1.5"/><path d="M3 10h18M6.5 15h4"/></svg>',
    stairs='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M3.5 20h4v-4h4v-4h4V8h5"/></svg>',
    sun='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4"/></svg>',
    tag='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M3.5 12.5V4.5h8l9 9-8 8-9-9Z"/><circle cx="8" cy="9" r="1.3"/></svg>',
    x='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M5 5l14 14M19 5 5 19"/></svg>',
    ig='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><rect x="3.2" y="3.2" width="17.6" height="17.6" rx="5"/><circle cx="12" cy="12" r="4.1"/><circle cx="17.3" cy="6.7" r="1" fill="currentColor" stroke="none"/></svg>',
    fb='<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13.6 21v-7.6h2.6l.4-3h-3V8.5c0-.9.3-1.5 1.5-1.5h1.6V4.3c-.3 0-1.2-.1-2.3-.1-2.3 0-3.9 1.4-3.9 4v2.2H7.8v3h2.7V21h3.1Z"/></svg>',
    leaf='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M5 19c0-8 5-13 14-14-1 9-6 14-14 14Zm0 0 7-7"/></svg>',
    gift='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><rect x="3.5" y="9" width="17" height="11.5" rx="1"/><path d="M2.5 9h19M12 9v11.5M12 9c-1.5-3-5.5-4.5-6-2s3 2 6 2Zm0 0c1.5-3 5.5-4.5 6-2s-3 2-6 2Z"/></svg>',
)

MONO_D = json.load(open(os.path.join(ROOT, '_src', 'logo_parts.json')))['mono']
SPRITE = f'<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="mono" viewBox="350 20 245 385"><path fill-rule="evenodd" d="{MONO_D}"/></symbol></svg>'

def wa_link(msg='Bonjour Charlène, j’aimerais prendre rendez-vous chez Maison Môa.'):
    from urllib.parse import quote
    return f'https://wa.me/{SITE["wa"]}?text={quote(msg)}'

# ---------------------------------------------------------------- JSON-LD
def ld_business():
    offers = []
    for s in SERVICES:
        offers.append({'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': s['name'], 'url': BASE + s['slug']},
                       'priceSpecification': {'@type': 'PriceSpecification', 'priceCurrency': 'CHF', 'minPrice': s['from']}})
    return {
        '@context': 'https://schema.org', '@type': 'BeautySalon', '@id': BASE + '#institut',
        'name': 'Maison Môa – Institut de beauté', 'alternateName': 'Maison Môa', 'slogan': 'Pensé avec intention',
        'description': "Institut de beauté indépendant à Riaz, près de Bulle : soins du visage, épilations à la cire végane, beauté du regard, des mains et des pieds, soins du corps.",
        'url': BASE, 'image': [BASE + 'assets/img/og.jpg', BASE + 'assets/img/corps-des-alpes-pipette.webp'], 'logo': BASE + 'assets/img/logo-maison-moa.svg',
        'telephone': SITE['tel'], 'email': SITE['email'], 'priceRange': 'CHF 10 – 160', 'currenciesAccepted': 'CHF', 'paymentAccepted': 'Carte bancaire, espèces',
        'address': {'@type': 'PostalAddress', 'streetAddress': SITE['street'], 'postalCode': SITE['zip'], 'addressLocality': SITE['city'], 'addressRegion': 'FR', 'addressCountry': 'CH'},
        'geo': {'@type': 'GeoCoordinates', 'latitude': SITE['lat'], 'longitude': SITE['lng']},
        'areaServed': ['Riaz', 'Bulle', 'La Gruyère', 'Vuadens', 'Marsens', 'Echarlens', 'Morlon', 'Le Pâquier', 'Broc', 'Gruyères'],
        'openingHoursSpecification': [
            {'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Tuesday', 'Wednesday', 'Thursday', 'Friday'], 'opens': '09:00', 'closes': '19:00', 'validFrom': '2026-11-02'},
            {'@type': 'OpeningHoursSpecification', 'dayOfWeek': 'Saturday', 'opens': '08:00', 'closes': '16:00', 'validFrom': '2026-11-02'}],
        'founder': {'@type': 'Person', 'name': 'Charlène', 'jobTitle': 'Esthéticienne CFC'},
        'sameAs': [SITE['instagram'], SITE['facebook'], SITE['salonkee']],
        'potentialAction': {'@type': 'ReserveAction', 'target': SITE['salonkee']},
        'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': 'Soins Maison Môa', 'itemListElement': offers},
    }

def ld_crumbs(items):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': BASE + u} for i, (n, u) in enumerate(items)]}

def ld_faq(faq):
    return {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}

# ---------------------------------------------------------------- gabarit
def head(slug, title, desc, scene=False, ld=(), og='og.jpg', preload_img=None):
    url = BASE + ('' if slug == 'index' else slug)
    lds = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False, separators=(",", ":"))}</script>' for x in ld)
    imap = '<script type="importmap">{"imports":{"three":"./assets/js/vendor/three.module.min.js"}}</script><link rel="modulepreload" href="assets/js/vendor/three.module.min.js"><link rel="modulepreload" href="assets/js/scenes.js">' if scene else ''
    pre = f'<link rel="preload" as="image" href="assets/img/{preload_img}.webp">' if preload_img else ''
    return f'''<!doctype html>
<html lang="fr-CH">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{A(desc)}">
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#f3eee7">
<meta property="og:type" content="website"><meta property="og:locale" content="fr_CH"><meta property="og:site_name" content="Maison Môa">
<meta property="og:title" content="{A(title)}"><meta property="og:description" content="{A(desc)}"><meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}assets/img/{og}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml"><link rel="icon" href="assets/img/favicon-32.png" sizes="32x32"><link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="preload" href="assets/fonts/cormorant.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="assets/fonts/jost.woff2" as="font" type="font/woff2" crossorigin>{pre}
<link rel="stylesheet" href="assets/css/fonts.css?v={VER}"><link rel="stylesheet" href="assets/css/site.css?v={VER}">
<script>(function(d){{var h=d.documentElement,p=location.pathname;h.classList.add('js');try{{if(sessionStorage.getItem('mm-seen'))h.classList.add('no-loader');if(sessionStorage.getItem('mm-trans'))h.classList.add('trans')}}catch(e){{}}if(!matchMedia('(prefers-reduced-motion: reduce)').matches)h.classList.add('pre-intro');if(/\\/index\\.html$/.test(p))history.replaceState(null,'',p.slice(0,-10)+location.search+location.hash);else if(p.slice(-5)==='.html')history.replaceState(null,'',p.slice(0,-5)+location.search+location.hash)}})(document)</script>
{imap}{lds}
</head>'''

NAV = [('la-maison', 'La Maison'), ('tarifs', 'Tarifs'), ('bons-cadeaux', 'Bons cadeaux'), ('contact', 'Contact')]

def header(active=''):
    cards = ''.join(f'<a class="mega-card" href="{s["slug"]}"><div class="ph">{img(s["hover"], s["name"], "220px")}</div><b>{E(s["name"])}</b><span>dès {chf(s["from"])}</span></a>' for s in SERVICES)
    cards += f'<a class="mega-card" href="bons-cadeaux"><div class="ph">{img("bon-cadeau-coffret", "Bon cadeau Maison Môa", "220px")}</div><b>Bons cadeaux</b><span>Offrir un moment</span></a>'
    cards += f'<a class="mega-card" href="tarifs"><div class="ph">{img("post-tarifs-1", "Carte des tarifs Maison Môa", "220px")}</div><b>Tous les tarifs</b><span>{TOTAL_SOINS} soins à la carte</span></a>'
    on = ' on' if active in SVC else ''
    cur = ' aria-current="page"'
    navl = ''.join(f'<a href="{u}"{cur if u == active else ""}>{n}</a>' for u, n in NAV)
    sub = ''.join(f'<a href="{s["slug"]}">{E(s["name"])}</a>' for s in SERVICES)
    return f'''<body data-page="{active or 'index'}">
{SPRITE}
<a class="skip" href="#main">Aller au contenu</a>
<div class="loader" aria-hidden="true"><div class="lg"><svg class="m" viewBox="0 0 245 385"><use href="#mono"/></svg><div class="w"><span>MAISON MÔA</span></div><div class="bar"><i></i></div></div></div>
<div class="curtain" aria-hidden="true"></div>
<header class="hdr" id="top">
 <div class="wrap">
  <a class="brand" href="./" aria-label="Maison Môa, accueil"><svg class="mono" viewBox="0 0 245 385" fill="currentColor" aria-hidden="true"><use href="#mono"/></svg><span class="word"><b>MAISON MÔA</b><i>Institut de beauté</i></span></a>
  <nav class="nav" aria-label="Navigation principale">
   <div class="dd{on}"><button type="button" aria-expanded="false" aria-controls="mega">Soins {I["down"]}</button>
    <div class="mega" id="mega"><div class="mega-in"><div class="mega-intro"><span class="eyebrow">La carte des soins</span><p class="h-s">Six univers, <em>un même soin du détail.</em></p><p>Visage, épilations, regard, mains, pieds et corps : chaque prestation est pensée pour prendre soin de vous avec précision.</p><a class="lnk" href="tarifs">Voir tous les tarifs {I["arrow"]}</a></div><div class="mega-grid">{cards}</div></div></div>
   </div>
   {navl}
  </nav>
  <div class="hdr-cta">
   <a class="icon-btn" href="{wa_link()}" target="_blank" rel="noopener" aria-label="Écrire sur WhatsApp">{I["wa"]}</a>
   <a class="icon-btn" href="tel:{SITE["tel"]}" aria-label="Appeler le {SITE["phone"]}">{I["phone"]}</a>
   <button class="btn solid mag" type="button" data-book>Réserver</button>
   <button class="burger" type="button" aria-label="Ouvrir le menu" aria-expanded="false" aria-controls="mmenu"><i></i><i></i></button>
  </div>
 </div>
</header>
<div class="mmenu" id="mmenu" aria-hidden="true">
 <nav aria-label="Menu mobile">
  <a href="./">Accueil <small>Maison Môa</small></a>
  <a href="./#soins">Les soins <small>{len(SERVICES)} univers</small></a>
  <div class="sub">{sub}</div>
  <a href="la-maison">La Maison <small>Charlène</small></a>
  <a href="tarifs">Tarifs <small>{TOTAL_SOINS} soins</small></a>
  <a href="bons-cadeaux">Bons cadeaux <small>Offrir</small></a>
  <a href="contact">Contact <small>Accès</small></a>
 </nav>
 <div class="mfoot">
  <div class="ctas"><button class="btn light solid" type="button" data-book>Réserver</button><a class="btn light" href="{wa_link()}" target="_blank" rel="noopener">{I["wa"]} WhatsApp</a></div>
  <p>{E(SITE["street"])}, {SITE["zip"]} {SITE["city"]} · <a href="tel:{SITE["tel"]}">{SITE["phone"]}</a></p>
 </div>
</div>
<main id="main">'''

def hours_list():
    return '<ul class="hours" data-hours>' + ''.join(f'<li data-day="{i}"><span>{d}</span><span>{h or "Fermé"}</span></li>' for i, (d, h) in enumerate(HOURS)) + '</ul>'

def footer():
    links = ''.join(f'<li><a href="{s["slug"]}">{E(s["name"])}</a></li>' for s in SERVICES)
    return f'''</main>
<footer class="ftr">
 <div class="wrap">
  <div class="ftr-top">
   <div>
    <img class="logo" src="assets/img/logo-ivoire.svg" alt="Maison Môa, institut de beauté" width="250" height="197" loading="lazy">
    <p>Institut de beauté à Riaz, à deux pas de Bulle.<br>Pensé avec intention ♡</p>
    <div class="soc"><a href="{SITE["instagram"]}" target="_blank" rel="noopener" aria-label="Instagram {SITE["ig_handle"]}">{I["ig"]}</a><a href="{SITE["facebook"]}" target="_blank" rel="noopener" aria-label="Facebook Maison Môa">{I["fb"]}</a><a href="{wa_link()}" target="_blank" rel="noopener" aria-label="WhatsApp">{I["wa"]}</a></div>
   </div>
   <div><h4>Les soins</h4><ul>{links}<li><a href="bons-cadeaux">Bons cadeaux</a></li></ul></div>
   <div><h4>Horaires</h4><ul><li>Mardi – vendredi · 9h – 19h</li><li>Samedi · 8h – 16h</li><li>Dimanche & lundi · fermé</li><li class="muted" data-status-text>Ouverture le {SITE["opening_txt"]}</li></ul></div>
   <div><h4>Contact</h4><ul><li><a href="tel:{SITE["tel"]}">{SITE["phone"]}</a></li><li><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></li><li><a href="{SITE["maps"]}" target="_blank" rel="noopener">{E(SITE["street"])}<br>{SITE["zip"]} {SITE["city"]}</a></li><li>{E(SITE["access"])}</li><li><a href="{SITE["salonkee"]}" target="_blank" rel="noopener">Réserver sur Salonkee</a></li></ul></div>
  </div>
  <div class="ftr-word" aria-hidden="true">Maison Môa</div>
  <div class="ftr-bot"><span>© {date.today().year} Maison Môa · Institut de beauté · Riaz (FR)</span><span><a href="tarifs">Tarifs</a> · <a href="contact">Contact</a> · <a href="politique-de-confidentialite">Confidentialité</a></span></div>
 </div>
</footer>
<div class="fab"><a class="wa" href="{wa_link()}" target="_blank" rel="noopener" aria-label="Écrire à Maison Môa sur WhatsApp">{I["wa"]}</a></div>
<nav class="mbar" aria-label="Actions rapides"><a href="tel:{SITE["tel"]}">{I["phone"]} Appeler</a><a href="{wa_link()}" target="_blank" rel="noopener">{I["wa"]} WhatsApp</a><a class="pri" href="#" data-book>{I["cal"]} Réserver</a></nav>
<div class="book" id="book" role="dialog" aria-modal="true" aria-labelledby="book-t" aria-hidden="true">
 <div class="scrim" data-close></div>
 <div class="sheet">
  <button class="x" type="button" data-close aria-label="Fermer">{I["x"]}</button>
  <span class="eyebrow">Réservation</span>
  <h2 class="h-m" id="book-t">Comment souhaitez-vous <em>réserver ?</em></h2>
  <p class="soin-name" data-soin-name></p>
  <a class="opt" href="{SITE["salonkee"]}" target="_blank" rel="noopener"><span class="ic">{I["cal"]}</span><span><b>En ligne, 24 h/24</b><span>Choisissez votre soin et votre créneau sur Salonkee.</span></span>{I["ne"]}</a>
  <a class="opt" href="{wa_link()}" target="_blank" rel="noopener" data-wa><span class="ic">{I["wa"]}</span><span><b>Sur WhatsApp</b><span>Écrivez-moi, je vous réponds dès que possible.</span></span>{I["ne"]}</a>
  <a class="opt" href="tel:{SITE["tel"]}"><span class="ic">{I["phone"]}</span><span><b>Par téléphone</b><span>{SITE["phone"]}</span></span>{I["ne"]}</a>
  <a class="opt" href="contact#demande" data-form><span class="ic">{I["mail"]}</span><span><b>Par message</b><span>Envoyez une demande de rendez-vous.</span></span>{I["ne"]}</a>
  <p class="small">Premiers rendez-vous dès le {SITE["opening_txt"]}. Pour toute annulation ou modification, merci de prévenir au minimum 24 h à l’avance.</p>
 </div>
</div>
'''

def scripts(scene=False):
    s = f'<script src="assets/js/vendor/gsap.min.js"></script><script src="assets/js/vendor/ScrollTrigger.min.js"></script><script src="assets/js/vendor/lenis.min.js"></script><script src="assets/js/site.js?v={VER}"></script>'
    if scene:
        s += f'<script type="module" src="assets/js/scenes.js?v={VER}"></script>'
    return s + '\n</body>\n</html>\n'

# ---------------------------------------------------------------- blocs partagés
def hero(scene, eyebrow, h1, lead, ctas, cls='', meta='', crumbs='', facts='', fallback='', cx=None):
    dx = f' data-cx="{cx}"' if cx else ''
    if 'svc-hero' in cls:
        dx += ' data-cy="0.56" data-rh="0.74"'
    fb = f'<div class="fallback" style="background-image:url(assets/img/{fallback}.webp)"></div>' if fallback else ''
    return f'''<section class="hero {cls}">
 <div class="scene" data-scene="{scene}"{dx}>{fb}</div>
 <div class="wrap"><div class="hero-copy">
  {crumbs}<span class="eyebrow">{eyebrow}</span>
  <h1 class="h-xl" data-split>{h1}</h1>
  <p class="lead">{lead}</p>
  <div class="ctas">{ctas}</div>{facts}
 </div></div>
 {meta}
</section>'''

def open_pill():
    return f'<div class="hero-meta"><div class="wrap"><span class="open-pill"><i class="dot"></i><span data-open-pill>Ouverture le <b>{SITE["opening_txt"]}</b></span></span><span class="scroll-cue"><i></i>Découvrir</span></div></div>'

def cta_buttons(soin=''):
    d = f' data-soin="{A(soin)}"' if soin else ''
    return (f'<button class="btn solid mag" type="button" data-book{d}>Réserver mon rituel</button>'
            f'<a class="btn mag" href="{wa_link()}" target="_blank" rel="noopener">{I["wa"]} WhatsApp</a>'
            f'<a class="icon-btn" href="tel:{SITE["tel"]}" aria-label="Appeler le {SITE["phone"]}">{I["phone"]}</a>')

def info_cards():
    cards = [(I['stairs'], 'Accès', f'{SITE["access"]}, {SITE["street"]}, {SITE["zip"]} {SITE["city"]}.'),
             (I['car'], 'Parking', "Places disponibles du côté de l'école primaire de Riaz, à quelques minutes à pied."),
             (I['bus'], 'Transports publics', 'Riaz est desservi par les transports publics, facilement accessible depuis Bulle.'),
             (I['card'], 'Paiement', 'Carte bancaire ou espèces. TWINT n’est pas encore disponible.'),
             (I['sun'], 'Pause déjeuner', 'Des créneaux sont proposés sur l’heure de midi, selon les disponibilités.'),
             (I['cal'], 'Annulation', 'Merci de prévenir au minimum 24 h à l’avance pour toute annulation ou modification.')]
    return '<div class="cards" data-rv-group>' + ''.join(f'<div data-rv><h4>{ic} {t}</h4><p>{E(p)}</p></div>' for ic, t, p in cards) + '</div>'

def infos_section(cls='bg-paper', title='Infos <em>pratiques</em>'):
    return f'''<section class="sec {cls}" id="infos">
 <div class="wrap info-grid">
  <div>
   <span class="eyebrow">Venir à l’institut</span>
   <h2 class="h-l" data-split style="margin:22px 0 10px">{title}</h2>
   <p class="addr">{E(SITE["street"])}, {SITE["zip"]} {SITE["city"]}</p>
   <p class="muted">{E(SITE["access"])} · à 5 minutes de Bulle</p>
   <p class="status" data-status><i></i><span>Ouverture le {SITE["opening_txt"]}</span></p>
   {hours_list()}
   {info_cards()}
  </div>
  <div>
   <a class="map" href="{SITE["maps"]}" target="_blank" rel="noopener" aria-label="Ouvrir l’itinéraire vers Maison Môa dans Google Maps" data-img>{img("plan-riaz", "Plan de Riaz avec l’emplacement de Maison Môa", "(max-width: 900px) 100vw, 45vw")}<span class="pin"><b>Maison Môa</b><i></i></span><span class="open">{I["pin"]} Itinéraire</span><small>© OpenStreetMap</small><i class="veil" aria-hidden="true"></i></a>
   <div class="ctas mt-m"><button class="btn solid mag" type="button" data-book>Réserver</button><a class="btn" href="tel:{SITE["tel"]}">{I["phone"]} {SITE["phone"]}</a></div>
  </div>
 </div>
</section>'''

def cta_band(title='Votre parenthèse <em>commence ici.</em>', lead='Réservez votre soin en ligne en quelques clics, ou écrivez-moi : je vous conseille volontiers sur le rituel qui vous ressemble.', bg='corps-des-alpes-pipette'):
    return f'''<section class="sec bg-olive cta-band">
 <div class="bgimg" aria-hidden="true">{img(bg, "", "100vw")}</div>
 <div class="wrap">
  <span class="eyebrow c">Réserver</span>
  <h2 class="h-l" data-split>{title}</h2>
  <p class="lead" data-rv>{lead}</p>
  <div class="ctas" data-rv><a class="btn light solid mag" href="{SITE["salonkee"]}" target="_blank" rel="noopener">{I["cal"]} Réserver en ligne</a><a class="btn light mag" href="{wa_link()}" target="_blank" rel="noopener">{I["wa"]} WhatsApp</a></div>
  <a class="tel" href="tel:{SITE["tel"]}" data-rv>{SITE["phone"]}</a>
 </div>
</section>'''

def faq_block(items):
    return '<div class="faq" data-rv-group>' + ''.join(f'<details data-rv><summary>{E(q)}<i aria-hidden="true"></i></summary><div class="ans"><p>{E(a)}</p></div></details>' for q, a in items) + '</div>'

def steps_html(steps, prog=True):
    li = ''
    for s in steps:
        opts = ''.join(f'<li>{E(o)}</li>' for o in s.get('opts', []))
        li += f'<li><b>{E(s["t"])}</b>{"<span>" + E(s["d"]) + "</span>" if s.get("d") else ""}{"<ul>" + opts + "</ul>" if opts else ""}</li>'
    return f'<ol class="steps">{"<i class=prog></i>" if prog else ""}{li}</ol>'

# ---------------------------------------------------------------- accueil
def page_index():
    rows = ''
    for s in SERVICES:
        rows += f'''<a class="svc-row" href="{s["slug"]}" data-hover="assets/img/{s["hover"]}-m.webp" data-rv>
 <span class="n">{s["n"]}</span><span class="thumb">{img(s["hover"], s["name"], "88px")}</span>
 <span><h3>{E(s["name"])}</h3><small class="sr-m">dès {chf(s["from"])}</small></span><p>{E(s["teaser"])}</p>
 <span class="from">dès<b>{chf(s["from"])}</b></span><span class="go">{I["arrow"]}</span></a>'''
    sig = VISAGE[4]
    ig = ['post-tarifs-1', 'post-tarifs-2', 'post-tarifs-3', 'post-tarifs-4', 'post-tarifs-5', 'post-tarifs-6', 'post-ouverture', 'post-bien-etre', 'lieu-charpente-1', 'post-prestations', 'post-sur-mesure', 'post-arrive-bientot']
    igh = ''.join(f'<a href="{SITE["instagram"]}" target="_blank" rel="noopener" aria-label="Voir sur Instagram" data-rv>{img(n, "Publication Instagram de Maison Môa", "(max-width: 560px) 50vw, (max-width: 900px) 33vw, 16vw")}</a>' for n in ig)
    lieu = [('lieu-charpente-3', 'La charpente de Maison Môa, sous les toits', 'big'), ('post-bien-etre', 'Un nouveau lieu dédié à votre bien-être', ''),
            ('lieu-charpente-1', 'L’espace sous la charpente en bois', ''), ('post-sur-mesure', 'Une approche sur mesure', ''),
            ('lieu-charpente-2', 'Lumière naturelle sous les fenêtres de toit', 'big'), ('corps-des-alpes-flacons', 'Les huiles Corps des Alpes', ''), ('logo-ombres', 'Maison Môa, institut de beauté', '')]
    hs = ''.join(f'<div class="hs-item {c}">{frame(n, a, "", par=False, sizes="(max-width: 900px) 78vw, 40vw", lazy=False)}</div>' for n, a, c in lieu)
    body = header('') + hero('serum', 'Institut de beauté · Riaz, Gruyère', 'Prendre soin de vous, <em>avec précision.</em>',
        'Soins du visage, épilations, beauté du regard, des mains et des pieds, soins du corps. Un institut intimiste à deux pas de Bulle, où chaque détail a sa raison d’être.',
        cta_buttons(), cls='svc-hero home-hero', meta=open_pill(), fallback='corps-des-alpes-pipette') + f'''
<section class="sec bg-paper intro"><div class="leaf-bg" aria-hidden="true"></div>
 <div class="wrap">
  <svg class="mono-draw" viewBox="0 0 245 385" aria-hidden="true" data-draw><use href="#mono"/></svg>
  <span class="eyebrow c">L’esprit Maison Môa</span>
  <h2 class="h-l" data-split>Un lieu <em>pensé avec intention,</em> où chaque détail a sa raison d’être.</h2>
  <p class="lead" data-rv>Maison Môa est un institut de beauté indépendant installé à Riaz, proche de Bulle. Un espace à taille humaine, accueillant, soigné et intimiste, pour que vous vous sentiez pleinement à votre place, avec une attention particulière portée à la qualité des soins, à vos envies et à votre confort.</p>
  <div class="pillars" data-rv-group>
   <div data-rv><b><span data-count="17">17</span> ans</b><span>de métier-passion</span></div>
   <div data-rv><b>CFC</b><span>Esthéticienne diplômée</span></div>
   <div data-rv><b><span data-count="{TOTAL_SOINS}">{TOTAL_SOINS}</span> soins</b><span>à la carte, du visage au corps</span></div>
  </div>
 </div>
</section>
<section class="sec" id="soins">
 <div class="wrap">
  <div class="svc-head">
   <div><span class="eyebrow">La carte des soins</span><h2 class="h-l" data-split style="margin-top:22px">Six univers, <em>un même soin du détail.</em></h2></div>
   <p data-rv>Des rituels visage aux épilations à la cire végane, chaque prestation est pensée pour prendre soin de vous avec justesse, dans une atmosphère douce et enveloppante.</p>
  </div>
  <div class="svc-list">{rows}</div>
  <div class="ctas mt-l" data-rv><a class="lnk" href="tarifs">Voir tous les tarifs {I["arrow"]}</a><a class="lnk" href="bons-cadeaux" style="margin-left:24px">Offrir un bon cadeau {I["arrow"]}</a></div>
 </div>
 <div class="hover-img" aria-hidden="true"></div>
</section>
<section class="sec bg-paper">
 <div class="wrap ritual">
  <div class="stick">{frame("visage-penombre", "Modelage du visage à la lueur d'une bougie", "", par=True)}<div class="badge"><span>Durée<b>{sig["dur"]}</b></span><span>Prix<b>{chf(sig["price"])}</b></span></div></div>
  <div>
   <span class="eyebrow">Le rituel signature</span>
   <h2 class="h-l" data-split style="margin:22px 0 26px">Le Rituel <em>Ultra Cocooning</em></h2>
   <p class="lead" data-rv>{E(sig["lead"][0])}</p>
   {steps_html(sig["steps"])}
   <p class="quote" data-rv>{E(sig["outro"])}</p>
   <div class="ctas" data-rv><button class="btn solid mag" type="button" data-book data-soin="Le Rituel Ultra Cocooning">Réserver ce rituel</button><a class="lnk" href="soins-du-visage">Tous les soins du visage {I["arrow"]}</a></div>
  </div>
 </div>
</section>
<section class="sec">
 <div class="wrap split">
  <div class="duo">{frame("charlene-soin", "Charlène, esthéticienne CFC, pendant un soin", "tall")}{frame("post-sur-mesure", "Une approche sur mesure", "tall")}</div>
  <div class="copy">
   <span class="eyebrow">L’intention de Charlène</span>
   <h2 class="h-l" data-split>La précision du geste, <em>le goût du détail.</em></h2>
   <p class="quote" data-rv>« Maison Môa est un espace que j’ai pensé autour d’une idée simple : prendre soin de vous avec précision. »</p>
   <p data-rv>Titulaire d’un CFC d’esthéticienne, j’ai commencé mon parcours dans ce métier-passion il y a maintenant 17 ans. Au fil de ces années, mes expériences, notamment dans l’hôtellerie et au sein d’un palace, m’ont permis d’affiner ma pratique et de développer ce qui me tient particulièrement à cœur : la précision du geste, le goût du détail et l’attention portée à chaque étape d’un soin.</p>
   <span class="sign" data-rv>Charlène</span>
   <div class="ctas mt-m" data-rv><a class="btn mag" href="la-maison">Découvrir la Maison {I["arrow"]}</a></div>
  </div>
 </div>
</section>
<section class="sec bg-linen">
 <div class="wrap mosaic">
  <div class="a">{frame("corps-des-alpes-pipette", "Huile de massage Corps des Alpes à la pipette, dans la lumière", "tall")}</div>
  <div class="b">{frame("corps-des-alpes-huiles", "Huiles de massage Corps des Alpes : laurier, argan, santal rouge, arnica, verveine", "wide")}</div>
  <div class="c">{frame("corps-des-alpes-lumiere", "Flacons d'huiles Corps des Alpes", "sq")}</div>
  <div class="copy">
   <span class="eyebrow">Le choix ♡</span>
   <h2 class="h-m" data-split style="margin:22px 0 24px">Corps des Alpes, <em>des soins suisses faits main</em> dans le canton de Fribourg.</h2>
   <p data-rv>Pour les soins, j’ai choisi Corps des Alpes : une gamme de produits naturels, nobles et efficaces, fabriqués et étiquetés à la main dans le canton de Fribourg. Un choix qui s’inscrit dans l’envie de privilégier les savoir-faire et les produits de proximité.</p>
   <div class="chips" data-rv><span class="chip">Huile d’arnica</span><span class="chip">Huile d’argan</span><span class="chip">Verveine</span><span class="chip">Santal rouge</span><span class="chip">Huile de laurier</span><span class="chip">Cire végane sans colophane</span></div>
   <a class="lnk" href="{SITE["corps_des_alpes"]}" target="_blank" rel="noopener" data-rv>Découvrir Corps des Alpes {I["ne"]}</a>
  </div>
 </div>
</section>
<section class="sec hscroll" id="lieu">
 <div class="hs-track">
  <div class="hs-intro"><span class="eyebrow">Premières touches</span><h2 class="h-m" data-split>Sous la charpente, <em>un cocon prend forme.</em></h2><p class="muted" data-rv>Une matière, une texture, une ambiance… À l’étage, sous une belle charpente de bois, chaque détail commence à trouver sa place. Et ce n’est que le début.</p><p class="muted" data-rv>Rendez-vous le {SITE["opening_txt"]} pour découvrir le lieu.</p></div>
  {hs}
 </div>
</section>
<section class="sec bg-paper gift">
 <div class="wrap gift-grid">
  <div class="scene" data-scene="cadeau" data-layout="center" data-cy="0.52" data-rh="0.82" data-lazy><div class="fallback" style="background-image:url(assets/img/bon-cadeau-coffret.webp)"></div></div>
  <div>
   <span class="eyebrow">Les bons cadeaux ♡</span>
   <h2 class="h-l" data-split style="margin:22px 0 26px">Offrir un moment <em>tout particulier.</em></h2>
   <p data-rv class="muted">Les bons cadeaux seront bientôt disponibles en ligne. En attendant, contactez-moi par e-mail ou par téléphone pour préparer votre attention sur mesure, puis venez la retirer directement à l’institut.</p>
   <p data-rv class="muted">Une jolie façon de faire plaisir, tout simplement.</p>
   <div class="ctas mt-m" data-rv><a class="btn solid mag" href="bons-cadeaux">{I["gift"]} Préparer un bon cadeau</a><a class="lnk" href="mailto:{SITE["email"]}?subject=Bon%20cadeau%20Maison%20M%C3%B4a">Par e-mail {I["arrow"]}</a></div>
  </div>
 </div>
</section>
<section class="sec tight">
 <div class="wrap">
  <div class="ig-head"><div><span class="eyebrow">Suivre l’aventure</span><h2 class="h-m" data-split style="margin-top:18px">Sur Instagram, <em>{SITE["ig_handle"]}</em></h2></div><a class="btn mag" href="{SITE["instagram"]}" target="_blank" rel="noopener">{I["ig"]} Suivre Maison Môa</a></div>
  <div class="ig-grid" data-rv-group>{igh}</div>
 </div>
</section>
{infos_section()}
<section class="sec">
 <div class="wrap narrow">
  <span class="eyebrow">Questions fréquentes</span>
  <h2 class="h-l" data-split style="margin:22px 0 44px">Bon <em>à savoir</em></h2>
  {faq_block(FAQ[:6])}
 </div>
</section>
{cta_band()}
''' + footer() + scripts(True)
    ld = [ld_business(), ld_faq(FAQ[:6])]
    return head('index', 'Maison Môa · Institut de beauté à Riaz, près de Bulle',
                'Maison Môa, institut de beauté à Riaz près de Bulle : soins du visage, épilations à la cire végane, teintures cils et sourcils, manucure, beauté des pieds et soins du corps. Ouverture le 2 novembre 2026.',
                scene=True, ld=ld) + body

# ---------------------------------------------------------------- pages de soins
def soin_article(it, i, svc):
    lead = it.get('lead') or []
    steps = it.get('steps') or []
    if len(steps) == 1 and not lead:
        lead, steps = [steps[0]['d']], []
    meta = f'<span>{I["clock"]} {it["dur"]}</span><span class="price">{chf(it["price"], it["prefix"])}</span>'
    if it.get('skin'):
        meta += f'<span>{I["leaf"]} {E(it["skin"])}</span>'
    if it.get('pick'):
        meta += f'<span>{E(it["pick"])}</span>'
    var = ''
    if it.get('variants'):
        var = '<ul class="opts">' + ''.join(f'<li><span>{E(v[0])}</span><b>{chf(v[1])}</b></li>' for v in it['variants']) + '</ul>'
    body = ''.join(f'<p>{E(p)}</p>' for p in lead)
    if it.get('choices'):
        body += '<p class="eyebrow" style="margin:22px 0 0">Trois gommages au choix</p>' + steps_html([dict(t=t, d=d) for t, d in it['choices']], prog=False)
    if steps:
        body += '<p class="eyebrow" style="margin:26px 0 0">Votre rituel en quelques étapes</p>' + steps_html(steps)
    body += ''.join(f'<p>{E(p)}</p>' for p in it.get('after', []))
    if it.get('note'):
        body += f'<p class="note"><b>À savoir :</b> {E(it["note"])}</p>'
    if it.get('tip'):
        body += f'<p class="note"><b>Petite astuce :</b> {E(it["tip"])}</p>'
    if it.get('outro'):
        body += f'<p class="outro">{E(it["outro"])}</p>'
    wa = wa_link(f'Bonjour Charlène, j’aimerais réserver le soin « {it["name"]} » chez Maison Môa.')
    return f'''<article class="soin{" compact" if it.get("addon") else ""}" id="{it["id"]}">
 <div class="top" data-rv>
  <span class="n">{svc["n"]}.{i:02d}{" · Le petit +" if it.get("addon") else ""}{" · Signature" if it.get("signature") else ""}</span>
  <h3>{E(it["name"])}</h3>
  <div class="meta">{meta}</div>{var}
  <div class="ctas"><button class="btn solid sm mag" type="button" data-book data-soin="{A(it["name"])}">Réserver ce soin</button><a class="btn sm" href="{wa}" target="_blank" rel="noopener">{I["wa"]} Une question ?</a></div>
 </div>
 <div class="body" data-rv>{body}</div>
</article>'''

def price_rows(rows):
    return '<ul class="price-list">' + ''.join(f'<li><span class="nm">{E(n)}</span><span class="dots"></span><span class="du">{dur(d)}</span><span class="pr">{chf(p)}</span></li>' for n, p, d in rows) + '</ul>'

def others(slug):
    idx = [s['slug'] for s in SERVICES].index(slug)
    picks = [SERVICES[(idx + k) % len(SERVICES)] for k in (1, 2, 3)]
    return ''.join(f'<a class="other" href="{s["slug"]}" data-rv>{frame(s["hover"], s["name"], "", par=False, sizes="(max-width: 900px) 50vw, 33vw")}<span class="lbl"><b>{E(s["name"])}</b><span>dès {chf(s["from"])}</span></span></a>' for s in picks)

def page_service(svc):
    slug = svc['slug']
    crumbs = f'<nav class="crumbs" aria-label="Fil d’Ariane"><a href="./">Accueil</a><span aria-hidden="true">/</span><a href="./#soins">Soins</a><span aria-hidden="true">/</span><span>{E(svc["name"])}</span></nav>'
    lo, hi = svc['durs']
    facts = f'<dl class="facts" data-intro><div><dt>Soins</dt><dd>{svc["count"]}</dd></div><div><dt>Durée</dt><dd>{dur(lo)} – {dur(hi)}</dd></div><div><dt>Dès</dt><dd>{chf(svc["from"])}</dd></div></dl>'
    h = hero(svc['scene'], svc['eyebrow'] + ' · Riaz, près de Bulle', svc['h1'], E(svc['intro']), cta_buttons(), cls='svc-hero', crumbs=crumbs, facts=facts, fallback=svc['img'])
    if slug == 'epilations':
        toc_items = [('ep-visage', 'Visage'), ('ep-corps', 'Corps'), ('ep-forfaits', 'Forfaits'), ('ep-rituel', 'Le rituel')]
        content = f'''
<section class="sec" id="carte">
 <div class="wrap">
  <div class="svc-head"><div><span class="eyebrow">La carte</span><h2 class="h-l" data-split style="margin-top:22px">Visage, corps <em>& forfaits</em></h2></div><p data-rv>Chaque épilation commence par une lotion professionnelle à l’eau de bleuet et se termine par une touche finale apaisante. Les forfaits réunissent jambes, maillot et aisselles en un seul rendez-vous.</p></div>
  <div class="menu-pair">
   <div class="menu-card marble" id="ep-visage" data-rv><h3>Visage</h3><p class="sub">Cire végane sans bandes</p>{price_rows(EP_FACE)}</div>
   <div class="menu-card marble" id="ep-forfaits" data-rv><h3>Forfaits</h3><p class="sub">Jambes, bikini & aisselles</p>{price_rows(EP_FORFAITS)}<ul class="price-list"><li><span class="nm">{E(EP_FORFAIT_PLUS[0])}</span><span class="dots"></span><span class="pr">+ {chf(EP_FORFAIT_PLUS[1])}</span></li></ul></div>
  </div>
  <div class="menu-card marble mt-m" id="ep-corps" data-rv><h3>Corps</h3><p class="sub">Aisselles & maillot : cire végane sans bandes · bras, jambes, dos & torse : cire roll-on</p><div class="menu-pair">{price_rows(EP_BODY[:7])}{price_rows(EP_BODY[7:])}</div></div>
  <div class="ctas mt-m" data-rv><button class="btn solid mag" type="button" data-book data-soin="Épilation">Réserver une épilation</button><a class="btn" href="{wa_link('Bonjour Charlène, j’aimerais réserver une épilation chez Maison Môa.')}" target="_blank" rel="noopener">{I["wa"]} Une question ?</a></div>
 </div>
</section>
<section class="sec bg-paper" id="ep-rituel">
 <div class="wrap grid-2">
  <div><span class="eyebrow">Visage, aisselles & maillot</span><h3 class="h-m" data-split style="margin:20px 0 6px">Une cire <em>végane, sans bandes</em></h3><p class="muted" data-rv>Hypoallergénique, sans colophane, formulée à basse température : idéale pour les zones délicates.</p>{steps_html(EP_RITUAL_FINE["steps"])}<p class="outro" data-rv>{E(EP_RITUAL_FINE["outro"])}</p></div>
  <div><span class="eyebrow">Bras, jambes, dos & torse</span><h3 class="h-m" data-split style="margin:20px 0 6px">Une cire <em>roll-on</em> tout en douceur</h3><p class="muted" data-rv>Hypoallergénique, sans colophane ni parfum, formulée à basse température.</p>{steps_html(EP_RITUAL_ROLL["steps"])}<p class="outro" data-rv>{E(EP_RITUAL_ROLL["outro"])}</p></div>
 </div>
</section>'''
    else:
        items = svc['items']
        toc_items = [(it['id'], it['name'].replace('Le Rituel ', '').replace('Le Soin ', '')) for it in items]
        arts = ''.join(soin_article(it, i + 1, svc) for i, it in enumerate(items))
        plus = ''
        if svc.get('plus'):
            plus = f'<div class="mt-l"><span class="eyebrow">Les petits +</span><h2 class="h-m" data-split style="margin:20px 0 30px">À ajouter <em>à votre soin du visage</em></h2><div class="soins">' + ''.join(soin_article(it, len(items) + i + 1, svc) for i, it in enumerate(svc['plus'])) + '</div></div>'
            toc_items.append(('contour-des-yeux', 'Les petits +'))
        content = f'''
<section class="sec" id="carte">
 <div class="wrap">
  <div class="svc-head"><div><span class="eyebrow">La carte</span><h2 class="h-l" data-split style="margin-top:22px">{svc["h1"]}<br>à Riaz</h2></div><p data-rv>Chaque soin est détaillé étape par étape, avec sa durée et son prix. Réservez en ligne en quelques clics, ou écrivez-moi pour être conseillée.</p></div>
  <div class="soins">{arts}</div>
  {plus}
 </div>
</section>'''
    toc = '<nav class="toc" aria-label="Sommaire des soins"><div class="wrap">' + ''.join(f'<a href="#{a}">{E(n)}</a>' for a, n in toc_items) + '<button class="btn solid sm" type="button" data-book>Réserver</button></div></nav>'
    imgs = svc['imgs']
    band = f'''<section class="sec tight"><div class="wrap photo-band">{frame(imgs[0], svc["name"])}{frame(imgs[1], svc["name"])}{frame(imgs[2], svc["name"])}</div></section>'''
    extra = ''
    if slug == 'soins-du-visage':
        ing = [('Camomille & bleuet', 'Des laits démaquillants doux pour préparer la peau.'), ('Karité bio & coco', 'Des gommages au sucre qui nourrissent en exfoliant.'),
               ('Figue de barbarie & jasmin', 'Pour régénérer et hydrater, aux senteurs florales.'), ('Café vert & bouleau', 'Une huile de modelage raffermissante.'),
               ('Thé vert & jojoba', 'Un masque apaisant pour les peaux qui ont besoin de calme.'), ('Aloe vera & immortelle', 'La crème de la touche finale, pour tous les rituels.'),
               ('Calendula', 'Une huile neutre et apaisante après la microdermabrasion.'), ('Jade frais', 'Des accessoires pour décongestionner le contour des yeux.')]
        extra = f'''<section class="sec bg-paper"><div class="wrap"><div class="svc-head"><div><span class="eyebrow">Au cœur des rituels</span><h2 class="h-l" data-split style="margin-top:22px">Des produits <em>choisis avec soin</em></h2></div><p data-rv>Naturels et sensoriels, les produits de Maison Môa sont sélectionnés pour leur efficacité et leur douceur, dont les huiles Corps des Alpes, fabriquées à la main dans le canton de Fribourg.</p></div><div class="ing" data-rv-group>{"".join(f"<div data-rv><b>{E(a)}</b><span>{E(b)}</span></div>" for a, b in ing)}</div></div></section>'''
    body = header(slug) + h + toc + content + band + extra + f'''
<section class="sec bg-paper">
 <div class="wrap"><div class="svc-head"><div><span class="eyebrow">Continuer la découverte</span><h2 class="h-m" data-split style="margin-top:20px">D’autres <em>rituels Môa</em></h2></div><p data-rv><a class="lnk" href="tarifs">Tous les tarifs {I["arrow"]}</a></p></div><div class="others">{others(slug)}</div></div>
</section>
{infos_section('', 'Venir <em>à l’institut</em>')}
{cta_band()}
''' + footer() + scripts(True)
    ld = [ld_crumbs([('Accueil', ''), (svc['name'], slug)]),
          {'@context': 'https://schema.org', '@type': 'Service', 'name': svc['name'], 'serviceType': svc['name'], 'description': svc['desc'],
           'provider': {'@id': BASE + '#institut'}, 'areaServed': ['Riaz', 'Bulle', 'La Gruyère'], 'url': BASE + slug,
           'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'CHF', 'lowPrice': svc['from'], 'offerCount': svc['count']}}]
    return head(slug, svc['title'], svc['desc'], scene=True, ld=ld) + body

# ---------------------------------------------------------------- la maison
def page_maison():
    crumbs = '<nav class="crumbs" aria-label="Fil d’Ariane"><a href="./">Accueil</a><span aria-hidden="true">/</span><span>La Maison</span></nav>'
    vals = [('La précision du geste', 'Des protocoles maîtrisés, réalisés avec attention, à chaque étape du soin.'),
            ('Le goût du détail', 'Un lieu soigneusement pensé, où chaque détail a sa raison d’être.'),
            ('Des produits de proximité', 'Corps des Alpes, fabriqués et étiquetés à la main dans le canton de Fribourg.'),
            ('Une approche sur mesure', 'Chaque prestation s’adapte à votre peau, à vos envies et à votre rythme.')]
    body = header('la-maison') + hero('maison', 'La Maison · Riaz', 'Un lieu soigneusement <em>pensé.</em>',
        'Maison Môa, c’est l’histoire d’une esthéticienne passionnée et d’une envie simple : vous accueillir dans un lieu à taille humaine, où l’on prend vraiment le temps de prendre soin de vous.',
        cta_buttons(), cls='svc-hero', crumbs=crumbs, fallback='logo-ombres') + f'''
<section class="sec bg-paper">
 <div class="wrap split">
  <div class="duo">{frame("charlene-soin", "Charlène pendant un soin", "tall")}{frame("corps-des-alpes-pipette", "Huile Corps des Alpes", "tall")}</div>
  <div class="copy">
   <span class="eyebrow">L’intention de Charlène</span>
   <h2 class="h-l" data-split>Prendre soin de vous, <em>avec précision.</em></h2>
   <p data-rv>Maison Môa, à Riaz, est un espace que j’ai pensé autour d’une idée simple : prendre soin de vous avec précision.</p>
   <p data-rv>Titulaire d’un CFC d’esthéticienne, j’ai commencé mon parcours dans ce métier-passion il y a maintenant 17 ans. Au fil de ces années, mes différentes expériences, notamment dans l’hôtellerie et au sein d’un palace, m’ont permis d’affiner ma pratique et de développer ce qui me tient particulièrement à cœur aujourd’hui : la précision du geste, le goût du détail et cette attention portée à chaque étape d’un soin.</p>
   <p data-rv>C’est cette vision que j’ai souhaité donner à Maison Môa : un lieu soigneusement pensé, où chaque détail a sa raison d’être, des soins maîtrisés aux produits soigneusement sélectionnés, dans une atmosphère douce et enveloppante.</p>
   <span class="sign" data-rv>Charlène</span>
  </div>
 </div>
</section>
<section class="sec">
 <div class="wrap">
  <div class="svc-head"><div><span class="eyebrow">Notre approche</span><h2 class="h-l" data-split style="margin-top:22px">Ce qui fait <em>Maison Môa</em></h2></div><p data-rv>Un institut à taille humaine, pour que vous vous sentiez pleinement à votre place, avec une attention particulière portée à la qualité des soins, à vos envies et à votre confort.</p></div>
  <div class="ing" data-rv-group>{"".join(f"<div data-rv><b>{E(a)}</b><span>{E(b)}</span></div>" for a, b in vals)}</div>
  <div class="pillars" data-rv-group>
   <div data-rv><b><span data-count="17">17</span> ans</b><span>de métier-passion</span></div>
   <div data-rv><b>CFC</b><span>Esthéticienne diplômée</span></div>
   <div data-rv><b>Palace</b><span>& hôtellerie haut de gamme</span></div>
  </div>
 </div>
</section>
<section class="sec bg-linen">
 <div class="wrap mosaic">
  <div class="a">{frame("corps-des-alpes-flacons", "Flacons Corps des Alpes", "tall")}</div>
  <div class="b">{frame("corps-des-alpes-huiles", "Huiles de massage Corps des Alpes", "wide")}</div>
  <div class="c">{frame("corps-des-alpes-flacons-2", "Huiles Corps des Alpes", "sq")}</div>
  <div class="copy">
   <span class="eyebrow">Le choix ♡</span>
   <h2 class="h-m" data-split style="margin:22px 0 24px">Corps des Alpes, <em>des produits suisses nobles,</em> naturels et efficaces.</h2>
   <p data-rv>Pour les soins, j’ai choisi Corps des Alpes, une gamme de produits naturels fabriqués et étiquetés à la main dans le canton de Fribourg. Leurs huiles de massage pour le visage et le corps font partie des soins de Maison Môa : une approche simple et authentique, qui correspond à l’esprit de la Maison.</p>
   <a class="lnk" href="{SITE["corps_des_alpes"]}" target="_blank" rel="noopener" data-rv>corps-des-alpes.ch {I["ne"]}</a>
  </div>
 </div>
</section>
<section class="sec">
 <div class="wrap split rev">
  <div class="duo">{frame("lieu-charpente-1", "L’espace sous la charpente", "tall")}{frame("lieu-charpente-2", "Fenêtres de toit et charpente en bois", "tall")}</div>
  <div class="copy">
   <span class="eyebrow">Le lieu</span>
   <h2 class="h-l" data-split>À l’étage, <em>sous la charpente.</em></h2>
   <p data-rv>L’institut se trouve au 1er étage, avec un accès par l’entrée des locaux de Fridogs, Ruelle des Berges 3A à Riaz. Une belle charpente de bois, la lumière des fenêtres de toit, des matières douces : un cocon intimiste, à deux pas de Bulle.</p>
   <ul class="checks" data-rv><li>Parking du côté de l’école primaire de Riaz</li><li>Accessible en transports publics depuis Bulle</li><li>Créneaux possibles sur la pause de midi</li></ul>
   <a class="btn mag" href="contact">Plan & accès {I["arrow"]}</a>
  </div>
 </div>
</section>
<section class="sec tight bg-paper"><div class="wrap"><div class="ig-grid" data-rv-group>{"".join(f'<a href="{SITE["instagram"]}" target="_blank" rel="noopener" aria-label="Voir sur Instagram" data-rv>{img(n, "Publication Instagram de Maison Môa", "(max-width: 900px) 33vw, 16vw")}</a>' for n in ["logo-banniere", "post-ouverture", "post-prestations", "post-bien-etre", "post-sur-mesure", "lieu-charpente-3"])}</div></div></section>
{cta_band("Au plaisir de vous <em>accueillir bientôt.</em>", "Les réservations en ligne sont ouvertes : choisissez votre soin et votre créneau, les premiers rendez-vous sont disponibles dès le " + SITE["opening_txt"] + ".")}
''' + footer() + scripts(True)
    return head('la-maison', 'La Maison · Charlène, esthéticienne CFC · Maison Môa Riaz',
                'Découvrez Maison Môa et Charlène, esthéticienne CFC depuis 17 ans, passée par l’hôtellerie et un palace. Un institut de beauté intimiste à Riaz, près de Bulle, avec les produits Corps des Alpes.',
                scene=True, ld=[ld_crumbs([('Accueil', ''), ('La Maison', 'la-maison')])]) + body

# ---------------------------------------------------------------- tarifs
def page_tarifs():
    secs, nav = '', ''
    for s in SERVICES:
        nav += f'<a href="#t-{s["slug"]}">{E(s["name"])}</a>'
        if s['slug'] == 'epilations':
            lists = f'<p class="eyebrow">Visage</p>{price_rows(EP_FACE)}<p class="eyebrow mt-m">Corps</p>{price_rows(EP_BODY)}<p class="eyebrow mt-m">Forfaits</p>{price_rows(EP_FORFAITS)}<ul class="price-list"><li><span class="nm">{E(EP_FORFAIT_PLUS[0])}</span><span class="dots"></span><span class="pr">+ {chf(EP_FORFAIT_PLUS[1])}</span></li></ul>'
        else:
            rows = ''
            for it in s['items'] + s.get('plus', []):
                sub = ''
                if it.get('variants'):
                    sub = '<small>' + ' · '.join(f'{E(v[0].split(" (")[0])} {chf(v[1])}' for v in it['variants']) + '</small>'
                rows += f'<li><span class="nm"><a href="{s["slug"]}#{it["id"]}">{E(it["name"])}</a>{sub}</span><span class="dots"></span><span class="du">{it["dur"]}</span><span class="pr">{chf(it["price"], it["prefix"])}</span></li>'
            lists = f'<ul class="price-list">{rows}</ul>'
        secs += f'''<div class="tarif-sec" id="t-{s["slug"]}"><div class="side" data-rv><span class="eyebrow">{s["n"]}</span><h2 class="h-m">{s["h1"]}</h2><p>{E(s["teaser"])}</p><a class="lnk" href="{s["slug"]}">Le détail des soins {I["arrow"]}</a></div><div class="menu-card travertine" data-rv>{lists}</div></div>'''
    body = header('tarifs') + f'''
<section class="sec" style="padding-top:calc(var(--hdr) + 90px)">
 <div class="wrap">
  <nav class="crumbs" aria-label="Fil d’Ariane"><a href="./">Accueil</a><span aria-hidden="true">/</span><span>Tarifs</span></nav>
  <span class="eyebrow">La carte des soins</span>
  <h1 class="h-xl" data-split style="margin:24px 0 26px">Tarifs <em>& prestations</em></h1>
  <p class="lead" data-intro style="max-width:40em">{TOTAL_SOINS} soins à la carte, du visage au corps. Tous les prix sont en francs suisses ; le paiement se fait par carte bancaire ou en espèces.</p>
  <div class="tarif-nav" data-intro>{nav}<a href="bons-cadeaux">Bons cadeaux</a></div>
  <div class="mt-l">{secs}</div>
  <div class="ctas mt-m" data-rv><button class="btn solid mag" type="button" data-book>Réserver un soin</button><a class="btn" href="{SITE["salonkee"]}" target="_blank" rel="noopener">Voir les disponibilités {I["ne"]}</a></div>
 </div>
</section>
{cta_band()}
''' + footer() + scripts(False)
    return head('tarifs', 'Tarifs · Maison Môa, institut de beauté à Riaz',
                'Tous les tarifs de Maison Môa à Riaz, près de Bulle : rituels visage dès CHF 85, épilations dès CHF 20, teintures dès CHF 30, manucure dès CHF 50, beauté des pieds dès CHF 60, soins du corps dès CHF 70.',
                ld=[ld_crumbs([('Accueil', ''), ('Tarifs', 'tarifs')])]) + body

# ---------------------------------------------------------------- formulaires
def soin_options():
    o = '<option value="">Choisir un soin…</option>'
    for s in SERVICES:
        o += f'<optgroup label="{A(s["name"])}">'
        if s['slug'] == 'epilations':
            names = [n for n, _, _ in EP_FACE + EP_BODY + EP_FORFAITS]
            o += ''.join(f'<option>Épilation · {E(n)}</option>' for n in names)
        else:
            o += ''.join(f'<option>{E(it["name"])}</option>' for it in s['items'] + s.get('plus', []))
        o += '</optgroup>'
    return o + '<option>Je ne sais pas encore, j’aimerais être conseillée</option>'

def page_contact():
    crumbs = '<nav class="crumbs" aria-label="Fil d’Ariane"><a href="./">Accueil</a><span aria-hidden="true">/</span><span>Contact</span></nav>'
    body = header('contact') + f'''
<section class="sec" style="padding-top:calc(var(--hdr) + 90px)">
 <div class="wrap grid-2" style="align-items:start">
  <div>
   {crumbs}
   <span class="eyebrow">Contact & réservation</span>
   <h1 class="h-xl" data-split style="margin:24px 0 26px">Au plaisir de <em>vous rencontrer.</em></h1>
   <p class="lead" data-intro>Réservez en ligne, appelez, écrivez sur WhatsApp ou envoyez une demande : je vous réponds dès que possible.</p>
   <div class="ctas mt-m" data-intro><a class="btn solid mag" href="{SITE["salonkee"]}" target="_blank" rel="noopener">{I["cal"]} Réserver en ligne</a><a class="btn mag" href="{wa_link()}" target="_blank" rel="noopener">{I["wa"]} WhatsApp</a></div>
   <ul class="hours mt-l" data-intro>
    <li><span>Téléphone</span><a href="tel:{SITE["tel"]}">{SITE["phone"]}</a></li>
    <li><span>E-mail</span><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></li>
    <li><span>Adresse</span><a href="{SITE["maps"]}" target="_blank" rel="noopener">{E(SITE["street"])}, {SITE["zip"]} {SITE["city"]}</a></li>
    <li><span>Instagram</span><a href="{SITE["instagram"]}" target="_blank" rel="noopener">{SITE["ig_handle"]}</a></li>
    <li><span>Facebook</span><a href="{SITE["facebook"]}" target="_blank" rel="noopener">Maison Môa</a></li>
   </ul>
  </div>
  <div class="panel" id="demande" data-intro>
   <span class="eyebrow">Demande de rendez-vous</span>
   <h2 class="h-m" style="margin:18px 0 28px">Votre <em>demande</em></h2>
   <form class="form" data-form="rdv" novalidate>
    <div class="field"><label for="f-nom">Prénom & nom</label><input id="f-nom" name="nom" autocomplete="name" required placeholder="Votre nom"></div>
    <div class="field"><label for="f-tel">Téléphone</label><input id="f-tel" name="tel" type="tel" autocomplete="tel" required placeholder="079 000 00 00"></div>
    <div class="field full"><label for="f-mail">E-mail <span class="muted">(facultatif)</span></label><input id="f-mail" name="email" type="email" autocomplete="email" placeholder="vous@exemple.ch"></div>
    <div class="field full"><label for="f-soin">Soin souhaité</label><select id="f-soin" name="soin">{soin_options()}</select></div>
    <div class="field"><label for="f-date">Date souhaitée</label><input id="f-date" name="date" type="date" min="2026-11-02"></div>
    <div class="field"><span class="lbl">Moment préféré</span><div class="pills"><label><input type="radio" name="moment" value="Matin"><span>Matin</span></label><label><input type="radio" name="moment" value="Midi"><span>Midi</span></label><label><input type="radio" name="moment" value="Après-midi"><span>Après-midi</span></label><label><input type="radio" name="moment" value="Fin de journée"><span>Fin de journée</span></label></div></div>
    <div class="field full"><label for="f-msg">Message</label><textarea id="f-msg" name="message" placeholder="Une question, une envie particulière, votre type de peau…"></textarea></div>
    <label class="consent full"><input type="checkbox" name="ok" required> <span>J’accepte que mes informations soient utilisées pour répondre à ma demande (<a href="politique-de-confidentialite" style="text-decoration:underline">confidentialité</a>).</span></label>
    <p class="form-msg" role="alert" aria-live="polite"></p>
    <div class="actions full"><button class="btn solid" type="submit" value="wa">{I["wa"]} Envoyer par WhatsApp</button><button class="btn" type="submit" value="mail">{I["mail"]} Envoyer par e-mail</button></div>
    <p class="form-note full">Le message s’ouvre dans WhatsApp ou votre messagerie, prêt à être envoyé. Rien n’est enregistré sur ce site.</p>
   </form>
  </div>
 </div>
</section>
{infos_section()}
<section class="sec">
 <div class="wrap narrow">
  <span class="eyebrow">Questions fréquentes</span>
  <h2 class="h-l" data-split style="margin:22px 0 44px">Tout ce qu’il faut <em>savoir</em></h2>
  {faq_block(FAQ)}
 </div>
</section>
''' + footer() + scripts(False)
    return head('contact', 'Contact & réservation · Maison Môa, institut de beauté à Riaz',
                f'Contactez Maison Môa à Riaz, près de Bulle : {SITE["phone"]}, WhatsApp ou {SITE["email"]}. Réservation en ligne, horaires, accès, parking et questions fréquentes.',
                ld=[ld_business(), ld_faq(FAQ), ld_crumbs([('Accueil', ''), ('Contact', 'contact')])]) + body

def page_cadeaux():
    crumbs = '<nav class="crumbs" aria-label="Fil d’Ariane"><a href="./">Accueil</a><span aria-hidden="true">/</span><span>Bons cadeaux</span></nav>'
    ideas = [VISAGE[4], VISAGE[1], MAINS[3], CORPS[0], CORPS[1], PIEDS[1]]
    idea_html = ''.join(f'<li><span class="nm">{E(i["name"])}<small>{i["dur"]}</small></span><span class="dots"></span><span class="pr">{chf(i["price"])}</span></li>' for i in ideas)
    steps = [dict(t='Choisissez', d='Un montant libre, ou un soin précis à offrir.'), dict(t='Contactez-moi', d='Par e-mail, téléphone ou WhatsApp, avec le prénom de la personne et un petit mot si vous le souhaitez.'),
             dict(t='Retirez-le à l’institut', d='Votre bon cadeau est préparé avec soin, et vous venez le chercher directement sur place.')]
    body = header('bons-cadeaux') + hero('cadeau', 'Bons cadeaux', 'Offrir un moment <em>tout particulier.</em>',
        'Un rituel visage, une manucure, un massage… ou un montant libre. Les bons cadeaux seront bientôt disponibles en ligne ; en attendant, je prépare votre attention sur mesure.',
        f'<a class="btn solid mag" href="#commande">{I["gift"]} Préparer un bon cadeau</a><a class="btn mag" href="tel:{SITE["tel"]}">{I["phone"]} {SITE["phone"]}</a>', cls='svc-hero', crumbs=crumbs, fallback='bon-cadeau-coffret') + f'''
<section class="sec bg-paper">
 <div class="wrap split">
  <div>
   <span class="eyebrow">Comment ça marche</span>
   <h2 class="h-l" data-split style="margin:22px 0 10px">Trois étapes, <em>tout simplement.</em></h2>
   {steps_html(steps)}
  </div>
  <div class="duo">{frame("bon-cadeau-coffret", "Coffret cadeau en papier kraft", "tall")}{frame("fleurs-enveloppe", "Fleurs séchées dans une enveloppe", "tall")}</div>
 </div>
</section>
<section class="sec" id="commande">
 <div class="wrap grid-2" style="align-items:start">
  <div>
   <span class="eyebrow">Idées de rituels à offrir</span>
   <h2 class="h-l" data-split style="margin:22px 0 30px">Quelques <em>coups de cœur</em></h2>
   <div class="menu-card" data-rv><ul class="price-list">{idea_html}</ul><p class="muted mt-s" style="font-size:14px">Ou un montant libre, à utiliser sur l’ensemble de la carte.</p></div>
  </div>
  <div class="panel" data-rv>
   <span class="eyebrow">Votre bon cadeau</span>
   <h2 class="h-m" style="margin:18px 0 28px">Préparer <em>votre attention</em></h2>
   <form class="form" data-form="cadeau" novalidate>
    <div class="field full"><span class="lbl">Montant ou soin</span><div class="pills"><label><input type="radio" name="montant" value="CHF 50.–"><span>CHF 50.–</span></label><label><input type="radio" name="montant" value="CHF 80.–"><span>CHF 80.–</span></label><label><input type="radio" name="montant" value="CHF 100.–" checked><span>CHF 100.–</span></label><label><input type="radio" name="montant" value="CHF 150.–"><span>CHF 150.–</span></label><label><input type="radio" name="montant" value="Un soin précis"><span>Un soin précis</span></label></div></div>
    <div class="field full"><label for="g-soin">Soin à offrir <span class="muted">(facultatif)</span></label><select id="g-soin" name="soin">{soin_options()}</select></div>
    <div class="field"><label for="g-de">De la part de</label><input id="g-de" name="de" autocomplete="name" required placeholder="Votre prénom"></div>
    <div class="field"><label for="g-pour">Pour</label><input id="g-pour" name="pour" placeholder="Son prénom"></div>
    <div class="field"><label for="g-tel">Votre téléphone</label><input id="g-tel" name="tel" type="tel" autocomplete="tel" required placeholder="079 000 00 00"></div>
    <div class="field"><label for="g-date">Retrait souhaité</label><input id="g-date" name="date" type="date" min="2026-11-02"></div>
    <div class="field full"><label for="g-msg">Un petit mot à glisser</label><textarea id="g-msg" name="message" placeholder="Joyeux anniversaire…"></textarea></div>
    <label class="consent full"><input type="checkbox" name="ok" required> <span>J’accepte que mes informations soient utilisées pour préparer ce bon cadeau.</span></label>
    <p class="form-msg" role="alert" aria-live="polite"></p>
    <div class="actions full"><button class="btn solid" type="submit" value="mail">{I["mail"]} Envoyer par e-mail</button><button class="btn" type="submit" value="wa">{I["wa"]} WhatsApp</button></div>
    <p class="form-note full">Paiement et retrait directement à l’institut. Rien n’est enregistré sur ce site.</p>
   </form>
  </div>
 </div>
</section>
{cta_band("Une jolie façon de <em>faire plaisir.</em>", "Pour toute question sur les bons cadeaux, appelez-moi ou écrivez-moi : je vous aide à choisir le rituel idéal.", "texture-marbre-2")}
''' + footer() + scripts(True)
    return head('bons-cadeaux', 'Bons cadeaux · Maison Môa, institut de beauté à Riaz',
                'Offrez un bon cadeau Maison Môa à Riaz, près de Bulle : rituel visage, manucure, massage ou montant libre, préparé sur mesure et à retirer à l’institut.',
                scene=True, ld=[ld_crumbs([('Accueil', ''), ('Bons cadeaux', 'bons-cadeaux')])]) + body

def page_privacy():
    body = header('') + f'''
<section class="sec legal" style="padding-top:calc(var(--hdr) + 90px)">
 <div class="wrap narrow">
  <span class="eyebrow">Informations légales</span>
  <h1 class="h-l" data-split style="margin:24px 0 30px">Politique de <em>confidentialité</em></h1>
  <p>Ce site est édité pour Maison Môa – Institut de beauté, {E(SITE["street"])}, {SITE["zip"]} {SITE["city"]}, Suisse. Contact : <a href="mailto:{SITE["email"]}">{SITE["email"]}</a>, {SITE["phone"]}.</p>
  <h2>Données collectées</h2>
  <p>Ce site ne collecte aucune donnée personnelle de manière automatique : pas de compte, pas de cookies publicitaires, pas d’outil de mesure d’audience. Les polices de caractères sont hébergées sur le site lui-même.</p>
  <h2>Formulaires</h2>
  <p>Les formulaires de demande de rendez-vous et de bon cadeau ne transmettent rien à un serveur : ils préparent un message dans votre application WhatsApp ou votre messagerie e-mail. Vous restez libre de l’envoyer ou non. Les informations reçues servent uniquement à répondre à votre demande et ne sont jamais transmises à des tiers.</p>
  <h2>Réservation en ligne</h2>
  <p>La réservation en ligne est assurée par Salonkee. En réservant, vous êtes soumis à la politique de confidentialité de ce prestataire.</p>
  <h2>Liens externes</h2>
  <p>Ce site contient des liens vers Instagram, Facebook, WhatsApp, Google Maps et Salonkee. Ces services disposent de leurs propres règles en matière de protection des données.</p>
  <h2>Vos droits</h2>
  <p>Conformément à la loi fédérale sur la protection des données (LPD), vous pouvez demander l’accès, la rectification ou la suppression de vos données en écrivant à <a href="mailto:{SITE["email"]}">{SITE["email"]}</a>.</p>
  <p class="muted mt-m">Carte : © les contributeurs d’OpenStreetMap.</p>
 </div>
</section>
''' + footer() + scripts(False)
    return head('politique-de-confidentialite', 'Politique de confidentialité · Maison Môa', 'Politique de confidentialité du site de Maison Môa, institut de beauté à Riaz.') + body

def page_404():
    body = header('') + f'''
<section class="notfound"><div class="wrap">
 <svg viewBox="0 0 245 385" style="width:56px;height:88px;margin:0 auto 30px;color:var(--olive)" fill="currentColor" aria-hidden="true"><use href="#mono"/></svg>
 <span class="eyebrow c">Page introuvable</span>
 <h1 class="h-l" style="margin:22px auto 22px;max-width:14ch">Cette page s’est <em>éclipsée.</em></h1>
 <p class="lead" style="margin:0 auto 34px;max-width:30em">Le lien est peut-être ancien. Revenez à l’accueil ou découvrez la carte des soins.</p>
 <div class="ctas" style="justify-content:center"><a class="btn solid" href="./">Accueil</a><a class="btn" href="tarifs">Les soins & tarifs</a></div>
</div></section>
''' + footer() + scripts(False)
    return head('404', 'Page introuvable · Maison Môa', 'Cette page n’existe pas.').replace('<link rel="canonical"', '<base href="/maisonmoa/"><link rel="canonical"') + body

# ---------------------------------------------------------------- écriture
def write(name, html_):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
        f.write(html_)

def main():
    pages = {'index.html': page_index(), 'la-maison.html': page_maison(), 'tarifs.html': page_tarifs(), 'contact.html': page_contact(),
             'bons-cadeaux.html': page_cadeaux(), 'politique-de-confidentialite.html': page_privacy(), '404.html': page_404()}
    for s in SERVICES:
        pages[s['slug'] + '.html'] = page_service(s)
    for n, h in pages.items():
        write(n, h)
    urls = [''] + [s['slug'] for s in SERVICES] + ['la-maison', 'tarifs', 'bons-cadeaux', 'contact']
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{BASE}{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')
    print('ok', len(pages), 'pages')

if __name__ == '__main__':
    main()
