#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — يولّد services.html / offerings.html / portfolio.html / about.html / contact.html
من الغلاف المشترك لـ index.html (رأس + CSS + هيدر + درج + فوتر + واتساب طافٍ + معرض + سكربت) — بلا تكرار يدوي.
تشغيل:  python3 build/build.py   (من مجلد prototype-home أو أي مكان)
"""
import re, os, json, html, urllib.parse as U
from data import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
MAN = json.load(open(os.path.join(ROOT, 'build', 'images-manifest.json'), encoding='utf-8'))
SIZES = MAN['sizes']
HEROES = MAN.get('heroes', {})   # من images.py hero_variants(): name → {'m':[[w,h,path]..], 'd':[[w,h,path]..]}
def sz(name):
    w, h = SIZES.get(name) or _probe(name); return f'width="{w}" height="{h}"'
def _probe(name):
    from PIL import Image
    return Image.open(os.path.join(ROOT, 'img', 'photos', name + '.webp')).size

def cut(s, a, b):
    i = s.index(a); j = s.index(b, i) + len(b); return s[i:j]
CSS = cut(IDX, '<style>', '</style>')
FONTS = cut(IDX, '<link rel="preload" as="font"', 'amiri-700.woff2" crossorigin>')   # v6.1: خطوط محلية (preload ×2)؛ الـ@font-face داخل CSS
HEADER = cut(IDX, '<header>', '</header>')
FOOTER = cut(IDX, '<footer>', '</footer>')
FAB = cut(IDX, '<a class="fab"', '</a>')
LB = cut(IDX, '<!-- المعرض -->', '<div class="lb-thumbs" id="lbThumbs"></div>\n</div>')
SCRIPT = cut(IDX, '<script>', '</script>')
# الصفحات الفرعية لا تحتوي .hero → كتلة الـfab الموروثة كانت تُبقيه مخفيًا؛ نُعطّلها (PAGE_JS يتولى الـfab)
SCRIPT = SCRIPT.replace("const fab=$('#fab'), contact=$('#contact'), hero=$('.hero');\n  if(fab){", "const fab=$('#fab'), contact=$('#contact'), hero=$('.hero');\n  if(fab && hero){")
assert "if(fab && hero){" in SCRIPT, 'fab patch failed'
WA_SVG = re.search(r'<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17\.5[^<]*</svg>', IDX).group(0)
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>'
HINT = '<span class="hint rv">اسحب لليسار<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5m7-7-7 7 7 7"/></svg></span>'
STAMP = 'v6.8 · 2026-09-05'

def wa(text, cls='btn btn-wa', label='تواصل عبر واتساب', ev='wa'):
    return f'<a class="{cls}" href="https://wa.me/{WA_NUM}?text={U.quote(text)}" target="_blank" rel="noopener" data-ev="{ev}">{WA_SVG}{label}</a>'
def esc(s): return html.escape(s, quote=True)

PAGES = [('index.html','الرئيسية'),('services.html','الخدمات'),('offerings.html','التقديمات'),('portfolio.html','أعمالنا'),('locations.html','المدن'),('about.html','من نحن'),('contact.html','تواصل')]

def header(cur, section=None):
    # القائمة الجانبية أُزيلت (طلب المالك 2026-09-04): صف صفحات ثابت في الهيدر، الصفحة الحالية aria-current="page"
    # v6.3 (D60): الصفحات الفرعية (مدينة/خدمة×مدينة) تُبرز قسمها «المدن» بـ aria-current="true"
    def cur_attr(p):
        if p == cur: return ' aria-current="page"'
        if section and p == section: return ' aria-current="true"'
        return ''
    links = '\n      '.join(f'<a class="nav-link" href="{p}"{cur_attr(p)}>{t}</a>' for p, t in PAGES)
    h = re.sub(r'(<a class="nav-link"[^>]*>[^<]*</a>\s*)+', links + '\n    ', HEADER, count=1)
    return h

PAGE_CSS = '''
/* ===== v6 — الصفحات الداخلية ===== */
.phero{position:relative;min-height:46svh;display:flex;align-items:flex-end;overflow:hidden;background:var(--rich);padding:0}
.phero picture{display:contents}
.phero img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 30%}
.phero::before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(13,13,13,.5),rgba(13,13,13,.8) 50%,var(--rich) 100%)}   /* v6.1: تعتيم أقوى — الصور الفاتحة (بوفيه/معرض) كانت تُضعف قراءة العنوان */
.phero h1,.phero p,.phero .label,.phero .crumb{text-shadow:0 1px 2px rgba(0,0,0,.6),0 2px 14px rgba(0,0,0,.5)}
.phero .wrap{position:relative;z-index:1;padding-block:28px 26px;text-align:center}
.phero .label{display:inline-flex;align-items:center;gap:12px;font-size:.74rem;letter-spacing:.3em;color:var(--gold);margin-bottom:8px}
.phero .label::before,.phero .label::after{content:"✦";font-size:.7rem;letter-spacing:0}
.phero h1{font-size:clamp(1.7rem,6vw,2.7rem);color:var(--cream);text-wrap:balance;line-height:1.35}
.phero h1 em{font-style:normal;background:var(--grad-gold);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;text-shadow:none;filter:drop-shadow(0 2px 6px rgba(0,0,0,.75))}   /* v6.1: text-shadow يطمس النص المتدرّج → drop-shadow */
.phero p{margin:10px auto 0;max-width:56ch;color:var(--cream-2);font-size:.98rem}
.phero .cta{display:flex;gap:10px;justify-content:center;margin-top:18px;flex-wrap:wrap}
.crumb{display:flex;justify-content:center;gap:8px;font-size:.78rem;color:var(--cream-3);margin-bottom:8px}
.crumb a{color:var(--gold-hi)}
@media (min-width:900px){.phero{min-height:400px}.phero .wrap{padding-block:48px 44px}}
/* شريط الروابط اللاصق */
.chips{position:sticky;top:var(--top);z-index:60;background:rgba(13,13,13,.9);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}
.chips .wrap{display:flex;gap:8px;overflow-x:auto;padding-block:10px;scrollbar-width:none;scroll-snap-type:x proximity}
.chips .wrap::-webkit-scrollbar{display:none}
.chips a{flex:none;scroll-snap-align:start;border:1px solid rgba(197,160,89,.28);border-radius:999px;padding:6px 14px;font-size:.84rem;font-weight:500;color:var(--cream-2);white-space:nowrap;transition:.25s}
.chips a:hover{color:var(--gold-hi);border-color:var(--line-hi)}
.chips a.on{background:var(--grad-gold);color:var(--black);border-color:transparent;font-weight:700}
.chips a b{font-family:var(--f-latin);font-weight:400;font-size:.7rem;margin-inline-start:6px;opacity:.7;direction:ltr}
@media (min-width:900px){.chips .wrap{justify-content:center;flex-wrap:wrap;overflow:visible}}
/* إبراز الهدف عند الوصول برابط # */
.hit{animation:hit 2.2s ease-out}
@keyframes hit{0%,40%{box-shadow:0 0 0 2px var(--gold),0 0 40px rgba(197,160,89,.35)}100%{box-shadow:none}}
/* بطاقة الخدمة */
.grp{padding-block:40px;content-visibility:auto;contain-intrinsic-size:auto var(--cis-m,900px)}
.grp+.grp{border-top:1px solid var(--line)}
.card{border:1px solid var(--line-2);border-radius:20px;background:rgba(36,36,36,.55);padding:16px;margin-top:16px;scroll-margin-top:calc(var(--top) + 64px)}
.card .latin{display:block;margin-bottom:4px}
.card h3{font-size:clamp(1.25rem,4.4vw,1.7rem);color:var(--gold-hi);line-height:1.4}
.card .short{color:var(--cream-3);font-size:.9rem;margin-top:2px}
.card .desc{margin-top:10px;color:var(--cream-2);font-size:.95rem}
.feats{display:grid;grid-template-columns:1fr 1fr;gap:8px 14px;margin-top:12px;font-size:.88rem;color:var(--cream)}
.feats li{list-style:none;display:flex;gap:8px;align-items:flex-start;line-height:1.5}
.feats li::before{content:"✦";color:var(--gold);font-size:.7rem;margin-top:.35em}
.gal{display:grid;grid-template-columns:repeat(4,1fr);grid-auto-rows:minmax(0,1fr);gap:6px;margin-top:14px}
.gal figure{position:relative;border-radius:12px;overflow:hidden;aspect-ratio:1;cursor:zoom-in;background:var(--black);border:1px solid var(--line)}
.gal figure:first-child{grid-column:span 2;grid-row:span 2}
.gal img{width:100%;height:100%;object-fit:cover;transition:transform .8s cubic-bezier(.22,1,.36,1)}
.gal figure:hover img{transform:scale(1.05)}
.gal figure.more::after{content:attr(data-more);position:absolute;inset:0;display:grid;place-items:center;background:rgba(13,13,13,.55);color:var(--gold-hi);font-family:var(--f-head);font-weight:700;font-size:1.1rem}
.gal .zoom{position:absolute;bottom:8px;inset-inline-end:8px;width:28px;height:28px;border-radius:50%;background:rgba(13,13,13,.6);border:1px solid var(--line-2);display:grid;place-items:center;color:var(--gold-hi);font-size:.8rem;pointer-events:none}
.outfits{margin-top:16px;padding-top:14px;border-top:1px solid var(--line)}
.outfits h4{font-size:1rem;color:var(--gold);font-family:var(--f-head);display:flex;align-items:center;gap:10px}
.outfits h4::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,rgba(197,160,89,.45),transparent)}
.ogrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px;margin-top:10px}
.ogrid figure{position:relative;border-radius:12px;overflow:hidden;aspect-ratio:3/4;cursor:zoom-in;background:var(--black);border:1px solid var(--line)}
.ogrid img{width:100%;height:100%;object-fit:cover;object-position:top}
.ogrid figcaption{position:absolute;inset-inline:0;bottom:0;padding:26px 8px 8px;background:linear-gradient(180deg,transparent,rgba(13,13,13,.95));font-family:var(--f-head);font-weight:700;color:var(--gold-hi);font-size:.92rem;text-align:center}
.card .acts{display:flex;gap:10px;margin-top:16px;flex-wrap:wrap}
.card .acts .btn{flex:1 1 180px}
@media (min-width:900px){
  .grp{padding-block:56px}
  .card{display:grid;grid-template-columns:1fr 1.05fr;gap:28px;padding:26px;margin-top:22px}
  .card .txt{order:1}.card .media{order:2}
  .card .gal{margin-top:0}
  .card .outfits,.card .acts{grid-column:1/-1}
  .card .acts .btn{flex:0 0 auto;min-width:220px}
  .feats{font-size:.92rem}
}
/* شبكة التقديمات */
.items{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.item{position:relative;border-radius:14px;overflow:hidden;background:var(--black);border:1px solid var(--line);cursor:zoom-in;transition:border-color .3s,transform .3s}
.item:hover{border-color:var(--line-hi);transform:translateY(-3px)}
.item img{width:100%;height:auto;aspect-ratio:1;object-fit:cover}   /* v6.1: height:auto ضروري — سمة height="640" كانت تغلب aspect-ratio فتطول البطاقات */
.item img[data-pos]{object-position:var(--pos)}
#hot .item img{object-position:50% 78%}
.item figcaption{padding:9px 10px 11px}
.item b{display:block;font-family:var(--f-head);font-size:.95rem;color:var(--gold-hi);line-height:1.35}
.item small{display:block;color:var(--cream-3);font-size:.78rem;line-height:1.45;margin-top:2px}
.cat{padding-block:40px;scroll-margin-top:calc(var(--top) + 56px);content-visibility:auto;contain-intrinsic-size:auto var(--cis-m,900px)}
@media (min-width:900px){.grp,.cat{contain-intrinsic-size:auto var(--cis-d,900px)}}
.cat+.cat{border-top:1px solid var(--line)}
.cat .sec-head{margin-bottom:16px}
.cat .cta-row{display:flex;justify-content:center;margin-top:18px}
@media (min-width:900px){.items{grid-template-columns:repeat(4,1fr);gap:16px}.item b{font-size:1.05rem}.item small{font-size:.84rem}.cat{padding-block:56px}}
/* معرض الأعمال */
.filters{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin-bottom:18px}
.filters button{border:1px solid rgba(197,160,89,.3);border-radius:999px;padding:7px 16px;font-size:.88rem;font-weight:500;color:var(--cream-2);transition:.25s}
.filters button[aria-pressed="true"]{background:var(--grad-gold);color:var(--black);border-color:transparent;font-weight:700;box-shadow:var(--glow-gold)}
.pgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.pgrid .shot{width:auto;max-width:none}
.pgrid .shot[hidden]{display:none}
.pnote{text-align:center;color:var(--cream-3);font-size:.84rem;margin-top:16px;line-height:1.7}
.pcount{text-align:center;color:var(--gold-hi);font-size:.82rem;margin-bottom:12px;font-family:var(--f-latin);letter-spacing:.1em}
@media (min-width:900px){.pgrid{grid-template-columns:repeat(4,1fr);gap:16px}}
/* من نحن */
.story{display:grid;gap:18px}
.story img{border-radius:18px;border:1px solid var(--line-2);width:100%;aspect-ratio:4/3;object-fit:cover}
.story p{color:var(--cream-2);font-size:1rem}
.story p+p{margin-top:10px}
.nums{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:22px}
.nums div{text-align:center;border:1px solid var(--line-2);border-radius:16px;padding:16px 8px;background:rgba(36,36,36,.5)}
.nums b{display:block;font-family:var(--f-latin);font-size:1.6rem;color:var(--gold-hi);direction:ltr}
.nums b.ar{font-family:var(--f-head)}
.nums small{color:var(--cream-3);font-size:.8rem}
.vals{display:grid;grid-template-columns:1fr;gap:10px}
.val{border:1px solid var(--line-2);border-radius:16px;padding:18px;background:rgba(36,36,36,.55)}
.val b{display:block;font-family:var(--f-head);font-size:1.1rem;color:var(--gold-hi);margin-bottom:6px}
.val b::before{content:"✦ ";color:var(--gold);font-size:.8rem}
.val p{color:var(--cream-2);font-size:.92rem}
@media (min-width:900px){.story{grid-template-columns:1.1fr 1fr;align-items:center;gap:40px}.vals{grid-template-columns:repeat(4,1fr);gap:16px}.nums{gap:16px}}
/* تواصل */
.cgrid{display:grid;gap:18px}
.form{border:1px solid var(--line-2);border-radius:20px;padding:18px;background:rgba(36,36,36,.55);display:grid;gap:12px}
.form label{display:grid;gap:5px;font-size:.86rem;color:var(--cream-2)}
.form input,.form select,.form textarea{font:inherit;font-size:1rem;color:var(--cream);background:rgba(13,13,13,.6);border:1px solid var(--line-2);border-radius:12px;padding:11px 12px;width:100%;transition:border-color .25s}
.form input:focus,.form select:focus,.form textarea:focus{outline:none;border-color:var(--gold)}
.form select{appearance:none;background-image:linear-gradient(45deg,transparent 50%,var(--gold) 50%),linear-gradient(135deg,var(--gold) 50%,transparent 50%);background-position:calc(0% + 18px) 55%,calc(0% + 13px) 55%;background-size:5px 5px;background-repeat:no-repeat;padding-inline-start:34px}
.form textarea{min-height:110px;resize:vertical}
.form .row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.form .note{font-size:.8rem;color:var(--cream-3)}
.ways{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.way{display:flex;flex-direction:column;align-items:center;gap:6px;text-align:center;border:1px solid var(--line-2);border-radius:16px;padding:16px 10px;background:rgba(36,36,36,.5);transition:.3s}
.way:hover{border-color:var(--line-hi);transform:translateY(-3px)}
.way svg{width:26px;height:26px;color:var(--gold-hi)}
.way b{font-family:var(--f-head);font-size:.98rem;color:var(--cream)}
.way small{color:var(--cream-3);font-size:.78rem;direction:ltr;unicode-bidi:isolate}
@media (min-width:900px){.cgrid{grid-template-columns:1.1fr .9fr;align-items:start;gap:32px}.ways{grid-template-columns:repeat(2,1fr)}}
'''

PAGE_JS = '''
<script>
(function(){
  const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
  // إبراز الهدف عند الوصول برابط #
  function hit(){ const id=decodeURIComponent(location.hash.slice(1)); if(!id) return; const el=document.getElementById(id); if(!el) return; el.classList.remove('hit'); requestAnimationFrame(()=>el.classList.add('hit')); }
  addEventListener('hashchange',hit); addEventListener('load',()=>setTimeout(hit,150));
  // شريط الروابط اللاصق: تفعيل حسب الموضع
  const chips=$$('.chips a'); if(chips.length){
    const map=new Map(chips.map(a=>[a.getAttribute('href').slice(1),a]));
    const io=new IntersectionObserver(es=>{ es.forEach(e=>{ if(e.isIntersecting){ chips.forEach(c=>c.classList.remove('on')); const c=map.get(e.target.id); if(c){c.classList.add('on'); c.scrollIntoView({block:'nearest',inline:'center',behavior:'smooth'});} } }); },{rootMargin:'-40% 0px -55% 0px'});
    map.forEach((a,id)=>{ const t=document.getElementById(id); if(t) io.observe(t); });
  }
  // واتساب الطافي: مخفي أثناء هيرو الصفحة وقسم التواصل
  const fab=$('#fab'), ph=$('.phero'), ct=$('#contact');
  if(fab){ const vis={h:true,c:false}; const ap=()=>fab.classList.toggle('hide',vis.h||vis.c);
    if(ph) new IntersectionObserver(es=>es.forEach(e=>{vis.h=e.isIntersecting;ap();}),{threshold:.2}).observe(ph);
    if(ct) new IntersectionObserver(es=>es.forEach(e=>{vis.c=e.isIntersecting;ap();}),{threshold:.2}).observe(ct); ap(); }
  window.__proto={hit};
})();
</script>'''

def shell(cur, title, desc, sections, body, extra_css='', extra_js='', hero_img=None, section=None):
    pre = hero_preload(hero_img) if hero_img else ''
    css = CSS.replace('</style>', PAGE_CSS + extra_css + '</style>')
    return f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)} — كيف الضيافة (نموذج v6)</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#0D0D0D">
{pre}
<meta property="og:title" content="{esc(title)} — كيف الضيافة">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="img/og.jpg">
<link rel="icon" href="img/logo-emblem.webp">
{FONTS}
{css}
</head>
<body>

<div class="proto">نموذج تجريبي للمراجعة — ليس الموقع الفعلي · {STAMP}</div>
{header(cur, section)}

<main id="top">
{body}
</main>

{FOOTER}

{FAB.replace('<a class="fab" id="fab"', '<a class="fab" id="fab" data-ev="wa_fab"')}

{LB}

{SCRIPT}
{PAGE_JS}
{extra_js}
</body>
</html>'''

def _hero_sets(img):
    """يعيد (m_srcset, m_fallback, d_srcset, m_w, m_h, d_w, d_h) من manifest['heroes']؛ None إن لم تُولَّد نسخ."""
    h = HEROES.get(img)
    if not h: return None
    m, d = h['m'], h['d']
    ms = ', '.join(f'{pth} {w}w' for w, _, pth in m); ds = ', '.join(f'{pth} {w}w' for w, _, pth in d)
    mf = next((pth for w, _, pth in m if w >= 750), m[-1][2])   # الافتراضي للجوال ≈ DPR2
    return ms, mf, ds, m[0][0], m[0][1], d[-1][0], d[-1][1]

def hero_preload(img):
    """preload مشروط بـ media (كما v5.3 للرئيسية): نسخة الجوال بـ imagesrcset، ونسخة الديسكتوب ≥900px."""
    hs = _hero_sets(img)
    if not hs:
        return f'<link rel="preload" as="image" href="img/photos/{img}.webp" fetchpriority="high">'
    ms, mf, ds, *_ = hs
    df = HEROES[img]['d'][-1][2]
    return (f'<link rel="preload" as="image" href="{mf}" imagesrcset="{ms}" imagesizes="100vw" media="(max-width:899px)" fetchpriority="high">\n'
            f'<link rel="preload" as="image" href="{df}" imagesrcset="{ds}" imagesizes="100vw" media="(min-width:900px)" fetchpriority="high">')

def hero_img(img, alt):
    """<picture>: مصدر ديسكتوب 3:1 (≥900px) + جوال 1:1 بثلاث كثافات. الأبعاد الصريحة تمنع CLS؛ CSS يغطي الصندوق (object-fit:cover)."""
    hs = _hero_sets(img)
    if not hs:
        return f'<img class="bg" src="img/photos/{img}.webp" alt="{esc(alt)}" {sz(img)} fetchpriority="high" decoding="async">'
    ms, mf, ds, mw, mh, dw, dh = hs
    return (f'<picture><source media="(min-width:900px)" srcset="{ds}" sizes="100vw" width="{dw}" height="{dh}">'
            f'<img class="bg" src="{mf}" srcset="{ms}" sizes="100vw" alt="{esc(alt)}" width="{mw}" height="{mh}" fetchpriority="high" decoding="async"></picture>')

def cis(n_items, kind='cat'):
    """v6.1 — تقدير ارتفاع القسم لـcontain-intrinsic-size (content-visibility:auto): يحفظ دقّة شريط التمرير والمراسي قبل تخطيط القسم.
    بطاقات .item: ≈(عرض العمود + 62px تعليق) لكل صف؛ جوال عمودان بعرض ≈170 → 232/صف، ديسكتوب 4 أعمدة ≈250 → 312/صف. بطاقات .card: ≈600/450 لكل بطاقة."""
    import math
    if kind == 'cat':
        m = 160 + math.ceil(n_items/2)*242; d = 180 + math.ceil(n_items/4)*328
    else:
        m = 130 + n_items*600; d = 150 + n_items*450
    return f'style="--cis-m:{m}px;--cis-d:{d}px"'

def phero(label, h1, p, img, alt, ctas='', crumb='', crumbs=None, after=''):
    """v6.3: crumbs=[(نص, رابط|None)..] لمسار متعدّد؛ img=None → هيرو بلا صورة (social/legal)؛ after = HTML بعد الفقرة (شارات)."""
    if crumbs: cr = '<span>›</span>'.join(f'<a href="{h}">{t}</a>' if h else f'<span>{t}</span>' for t, h in crumbs)
    else: cr = f'<span>{crumb or label}</span>'
    return f'''<section class="phero{'' if img else ' noimg'}" aria-label="{esc(label)}">
  {hero_img(img, alt) if img else ''}
  <div class="wrap">
    <div class="crumb"><a href="index.html">الرئيسية</a><span>›</span>{cr}</div>
    <span class="label">{label}</span>
    <h1>{h1}</h1>
    <p>{p}</p>
    {after}
    {f'<div class="cta">{ctas}</div>' if ctas else ''}
  </div>
</section>'''

def fig(name, alt, cap, sub='', g='', tag='', extra='', cls='', more=''):
    m = f' class="{cls}{" more" if more else ""}" data-more="{more}"' if more else (f' class="{cls}"' if cls else '')
    return (f'<figure{m} data-g="{g}"{extra}><img src="img/photos/{name}.webp" alt="{esc(alt)}" {sz(name)} loading="lazy" decoding="async" data-cap="{esc(cap)}" data-sub="{esc(sub)}">'
            f'{f"<span class=\"tag\">{tag}</span>" if tag else ""}<span class="zoom" aria-hidden="true">⤢</span></figure>')

def contact_block(h2, p, wa_text):
    return f'''<section class="on-black grain glow contact" id="contact">
  <div class="wrap">
    <span class="label rv">تواصل</span>
    <h2 class="rv">{h2}</h2>
    <p class="rv">{p}</p>
    <div class="actions rv">
      {wa(wa_text, 'btn btn-wa', 'تواصل عبر واتساب', 'wa_contact')}
      <a class="btn btn-glass" href="contact.html">نموذج طلب عرض</a>
    </div>
    <p class="tel rv">واتساب واتصال: <a href="tel:+966508252134">{WA_DISPLAY}</a></p>
    <p class="assure rv">عروض أسعار وعقود وفواتير رسمية للجهات والشركات</p>
  </div>
</section>'''

def faq_block(items, h2):
    d = ''.join(f'<details class="rv"{" open" if i==0 else ""}><summary>{q}</summary><p>{a}</p></details>' for i,(q,a) in enumerate(items))
    return f'''<section class="on-deep" id="faq"><div class="wrap"><div class="sec-head"><span class="label rv">أسئلة شائعة</span><h2 class="rv">{h2}</h2></div><div class="faqs">{d}</div></div></section>'''

# ======================= services.html =======================
def build_services():
    chips = ''.join(f'<a href="#{i}">{SERVICES[i]["title"].split(" — ")[0].split(" و")[0] if len(SERVICES[i]["title"])>22 else SERVICES[i]["title"]}</a>' for g in SERVICE_GROUPS for i in g['ids'])
    body = phero('الخدمات', 'كل ما تحتاجه مناسبتك — <em>من طاقم واحد</em>', 'خمس عشرة خدمة في أربع مجموعات: طاقم رجالي ونسائي، تراث وفنون، أركان وتجهيز. اختر ما يناسب طابع مناسبتك واطلب عرضًا خلال دقائق.', 's-hosts', 'قهوجيين كيف الضيافة في قاعة استقبال',
        wa('السلام عليكم، أرغب بعرض سعر لطاقم ضيافة لمناسبة:\nالمدينة: \nالتاريخ: \nعدد الضيوف: ', 'btn btn-gold', 'اطلب عرضًا الآن', 'wa_hero') + '<a class="btn btn-glass" href="#g-male">استعرض الخدمات</a>')
    body += f'<nav class="chips" aria-label="الخدمات"><div class="wrap">{chips}</div></nav>'
    for gi, g in enumerate(SERVICE_GROUPS):
        cards = ''
        for sid in g['ids']:
            s = SERVICES[sid]
            gal = ''
            for k, (name, cap) in enumerate(zip(s['gallery'], s['gallery_caps'])):
                hidden = k >= 5
                gal += fig(name, f'{s["title"]} — {cap}', s['title'], cap, f'svc-{sid}', extra=' hidden' if hidden else '', more=(f'+{len(s["gallery"])-5}' if k == 4 and len(s['gallery']) > 5 else ''))
            outfits = ''
            if s.get('outfits'):
                oo = ''.join(fig(im, f'زي {n} — {d}', n, d, f'svc-{sid}') .replace('<span class="zoom" aria-hidden="true">⤢</span>', f'<figcaption>{n}</figcaption>') for n, d, ims in s['outfits'] for im in ims[:2])
                outfits = f'<div class="outfits"><h4>الأزياء المتاحة — اختر ما يناسب طابع مناسبتك</h4><div class="ogrid">{oo}</div></div>'
            feats = ''.join(f'<li>{f}</li>' for f in s['features'])
            wa_txt = f'السلام عليكم، أرغب بالاستفسار عن خدمة «{s["title"]}» لمناسبة:\nالمدينة: \nالتاريخ: \nعدد الضيوف: '
            cards += f'''<article class="card rv" id="{sid}" aria-labelledby="h-{sid}">
  <div class="txt"><span class="latin">{s['latin']}</span><h3 id="h-{sid}">{s['title']}</h3><p class="short">{s['short']}</p><p class="desc">{s['desc']}</p><ul class="feats">{feats}</ul></div>
  <div class="media"><div class="gal">{gal}</div></div>
  {outfits}
  <div class="acts">{wa(wa_txt, 'btn btn-gold', 'اطلب هذه الخدمة', f'wa_svc_{sid}')}<a class="btn btn-glass" href="contact.html?service={sid}">نموذج طلب عرض</a></div>
</article>'''
        body += f'''<section class="grp {'on-rich' if gi%2==0 else 'on-deep'}" id="g-{g['key']}" {cis(len(g['ids']), 'grp')}><div class="wrap"><div class="sec-head"><span class="label rv">{g['hint']}</span><h2 class="rv">{g['label']}</h2></div>{cards}</div></section>'''
    body += faq_block(FAQ_SERVICES, 'قبل أن تختار الخدمة')
    body += contact_block('لم تجد ما تبحث عنه؟ <em>أخبرنا بمناسبتك</em>', 'نقترح عليك الطاقم والزي والتقديمات المناسبة — بلا التزام.', 'السلام عليكم، أرغب باستشارة حول الخدمة المناسبة لمناسبة:\nالمدينة: \nالتاريخ: \nعدد الضيوف: ')
    secs = [(f'g-{g["key"]}', g['label'], g['hint']) for g in SERVICE_GROUPS] + [('faq','أسئلة شائعة',''),('contact','تواصل','')]
    js = '''<script>document.querySelectorAll('.gal figure.more').forEach(f=>f.addEventListener('click',()=>{},{once:true}));</script>'''
    return shell('services.html', 'الخدمات', 'خدمات كيف الضيافة: قهوجيين وصبابين، سقّاء زمزم، سفرجية، سوّاس، طاقم نسائي، خطاط ورسّام، فرقة شعبية، خيمة تراثية، كاونترات، ركن تصوير، بوفيه وطاولة متنقلة.', secs, body, hero_img='s-hosts')

# ======================= offerings.html =======================
def build_offerings():
    pd = json.load(open(os.path.join(ROOT,'build','prod-data.json'), encoding='utf-8'))
    cats = pd['offerings']
    chips = ''.join(f'<a href="#{c["id"]}">{c["label"]}<b>{len(c["items"])}</b></a>' for c in cats) + f'<a href="#equipment">المعدات<b>{len([k for k in SIZES if k.startswith("of-equipment-")])}</b></a><a href="#distributions">التوزيعات<b>5</b></a>'
    body = phero('التقديمات والمعدات', 'ما الذي يصل إلى <em>ضيوفك؟</em>', 'قهوة سعودية وشاي، مشروبات باردة، تمور محشية، حلويات ومعجنات، سناكات وسندوتشات وفواكه ومكسرات — ودلال وفناجين تليق بها. اختر ما تريد ونرتّبه لك.', 'pf-eq-3', 'بوفيه تقديمات كيف الضيافة: معجنات وكانابيه على حوامل ذهبية',
        wa('السلام عليكم، أرغب بعرض سعر لتقديمات ضيافة لمناسبة:\nالمدينة: \nالتاريخ: \nعدد الضيوف: \nالأصناف المطلوبة: ', 'btn btn-gold', 'اطلب قائمة تقديمات', 'wa_hero') + '<a class="btn btn-glass" href="#hot">استعرض الأصناف</a>', crumb='التقديمات')
    body += f'<nav class="chips" aria-label="فئات التقديمات"><div class="wrap">{chips}</div></nav>'
    def grid(cid, items):
        return '<div class="items">' + ''.join(f'<figure class="item rv" data-g="of-{cid}"><img src="img/photos/{n}.webp" alt="{esc(nm)} — {esc(d)}" {sz(n)} loading="lazy" decoding="async" data-cap="{esc(nm)}" data-sub="{esc(d)}"><figcaption><b>{nm}</b><small>{d}</small></figcaption></figure>' for n, nm, d in items) + '</div>'
    for ci, c in enumerate(cats):
        items = []
        for i, it in enumerate(c['items'], 1):
            nm = it['name']; d = it['desc']
            if c['id'] == 'nuts': nm = NUTS_FIX[i-1]; d = 'منتجات شركة شريكة — تشكيلة فاخرة للضيافة'
            if c['id'] == 'sandwiches': nm = SANDWICH_FIX[i-1]
            nm = NAME_FIX.get(nm, nm)
            items.append((f"of-{c['id']}-{i}", nm, d))
        extra = '<p class="rv" style="text-align:center;color:var(--cream-3);font-size:.82rem;margin-top:-6px;margin-bottom:12px">المكسرات والغرانولا من منتجات شركة شريكة معتمدة، وتُقدَّم بتغليفها الأصلي أو في صحون التقديم.</p>' if c['id']=='nuts' else ''
        body += f'''<section class="cat {'on-rich' if ci%2==0 else 'on-deep'}" id="{c['id']}" {cis(len(items))}><div class="wrap"><div class="sec-head"><span class="label rv">{len(items)} أصناف</span><h2 class="rv">{c['label']}</h2><p class="rv">{c['desc']}</p></div>{extra}{grid(c['id'], items)}
<div class="cta-row rv">{wa(f"السلام عليكم، أرغب بإضافة «{c['label']}» لتقديمات مناسبة:\nالمدينة: \nالتاريخ: \nعدد الضيوف: ", 'btn btn-glass btn-sm', f'اطلب {c["label"]}', f'wa_off_{c["id"]}')}</div></div></section>'''
    # المعدات
    eq = [(k, equipment_caption(MAN['map'][k]), 'ضمن الحزمة أو بحسب الطلب') for k in sorted((k for k in SIZES if k.startswith('of-equipment-')), key=lambda x:int(x.split('-')[-1]))]
    body += f'''<section class="cat on-rich" id="equipment" {cis(len(eq))}><div class="wrap"><div class="sec-head"><span class="label rv">{len(eq)} قطعة</span><h2 class="rv">معدات التقديم</h2><p class="rv">دلال ذهبية وفضية، فناجين وكاسات، استاندات وصواني — كلها من مخزوننا وتصل مع الطاقم.</p></div>{grid('equipment', eq)}
<div class="cta-row rv">{wa('السلام عليكم، أرغب بالاستفسار عن معدات التقديم (دلال، فناجين، استاندات) لمناسبة:\nالمدينة: \nالتاريخ: ', 'btn btn-glass btn-sm', 'اسأل عن المعدات', 'wa_off_equipment')}</div></div></section>'''
    di = [(f'of-distributions-{i}', DIST_CAPS[i-1], 'تغليف فاخر · إمكانية طباعة الشعار') for i in range(1,6)]
    body += f'''<section class="cat on-deep" id="distributions" {cis(len(di))}><div class="wrap"><div class="sec-head"><span class="label rv">هدايا الضيوف</span><h2 class="rv">التوزيعات</h2><p class="rv">صواني توزيعات VIP — تمر وحلا وقهوة — بتغليف فاخر يمكن طباعة شعار الجهة عليه.</p></div>{grid('distributions', di)}
<div class="cta-row rv">{wa('السلام عليكم، أرغب بعرض سعر لتوزيعات VIP لمناسبة:\nالمدينة: \nالتاريخ: \nالعدد: ', 'btn btn-glass btn-sm', 'اطلب توزيعات', 'wa_off_distributions')}</div></div></section>'''
    body += faq_block(FAQ_OFFERINGS, 'عن التقديمات والمعدات')
    body += contact_block('أرسل قائمتك <em>ونعود إليك بعرض</em>', 'اختر الأصناف، وأخبرنا بالمدينة والتاريخ وعدد الضيوف.', 'السلام عليكم، أرغب بعرض سعر لتقديمات ضيافة:\nالمدينة: \nالتاريخ: \nعدد الضيوف: \nالأصناف: ')
    secs = [(c['id'], c['label'], '') for c in cats] + [('equipment','معدات التقديم',''),('distributions','التوزيعات',''),('contact','تواصل','')]
    return shell('offerings.html', 'التقديمات والمعدات', 'تقديمات كيف الضيافة: مشروبات حارة وباردة، تمور فاخرة، حلويات، معجنات، سناكات، سندوتشات، فواكه، مكسرات، معدات تقديم وتوزيعات VIP.', secs, body, hero_img='pf-eq-3')

# ======================= portfolio.html =======================
def build_portfolio():
    shots = []
    def add(prefix, caps, typ, tag, n):
        for i, (c, s) in enumerate(caps[:n], 1):
            shots.append((f'{prefix}-{i}', c, s, typ, tag))
    add('pf-co', PF_CO_CAPS, 'corporate', 'شركة', len(PF_CO_CAPS))
    add('pf-gov', PF_GOV_CAPS, 'government', 'فعالية رسمية', 4)
    add('pf-wed', PF_WED_CAPS, 'private', 'مناسبة خاصة', len(PF_WED_CAPS))
    add('pf-eq', PF_EQ_CAPS, 'equipment', 'تجهيزات', len(PF_EQ_CAPS))
    # ترتيب متنوّع: تداخل الأنواع
    order = []; buckets = {}
    for s in shots: buckets.setdefault(s[3], []).append(s)
    keys = ['corporate','government','private','equipment']
    while any(buckets.values()):
        for k in keys:
            if buckets.get(k): order.append(buckets[k].pop(0))
    figs = ''.join(f'<figure class="shot rv" data-g="pf" data-type="{t}" data-go="portfolio.html?type={t}" data-go-txt="المزيد من هذا النوع"><img src="img/photos/{n}.webp" alt="{esc(c)} — {esc(s)}" {sz(n)} loading="lazy" decoding="async" data-cap="{esc(c)}" data-sub="{esc(s)}"><span class="tag">{tag}</span><figcaption><b>{c}</b><span>{s}</span></figcaption></figure>' for n, c, s, t, tag in order)
    body = phero('أعمالنا', 'صور من مناسبات <em>نفّذناها</em>', f'{len(order)} صورة من فعاليات الشركات والاستقبالات الرسمية والزواجات وتجهيزاتنا. اضغط على أي صورة لتكبيرها.', 'p-gala', 'عشاء رسمي في قاعة فاخرة',
        wa('السلام عليكم، شاهدت أعمالكم وأرغب بعرض سعر لمناسبة:\nالمدينة: \nالتاريخ: \nعدد الضيوف: ', 'btn btn-gold', 'اطلب عرضًا مشابهًا', 'wa_hero'), crumb='أعمالنا')
    body += f'''<section class="on-rich" id="gallery" style="padding-top:28px"><div class="wrap">
  <div class="filters rv" role="group" aria-label="تصفية الأعمال">
    <button type="button" data-f="all" aria-pressed="true">الكل</button>
    <button type="button" data-f="government" aria-pressed="false">جهات حكومية ورسمية</button>
    <button type="button" data-f="corporate" aria-pressed="false">شركات</button>
    <button type="button" data-f="private" aria-pressed="false">مناسبات خاصة وزواجات</button>
    <button type="button" data-f="equipment" aria-pressed="false">تجهيزات ومعدات</button>
  </div>
  <p class="pcount" id="pcount" aria-live="polite"></p>
  <div class="pgrid" id="pgrid">{figs}</div>
  <p class="pnote rv" id="govnote" hidden>تُعرض أعمال الجهات الحكومية بلا أسماء أو شعارات حتى الحصول على موافقتها الكتابية — الصور هنا لفعاليات رسمية بلا هوية جهة.</p>
  <p class="pnote rv">شعارات الشركات في الصور تُعرض بوصفها جزءًا من المناسبة نفسها، وتوسم بـ «شركة».</p>
</div></section>'''
    body += contact_block('تريد مناسبة <em>بهذا المستوى؟</em>', 'أرسل المدينة والتاريخ وعدد الضيوف — ونعود إليك بعرض.', 'السلام عليكم، شاهدت أعمالكم وأرغب بعرض سعر لمناسبة:\nالمدينة: \nالتاريخ: \nعدد الضيوف: ')
    js = '''<script>
(function(){
  const map={events:'corporate',weddings:'private',equipment:'equipment',government:'government',corporate:'corporate',private:'private',all:'all'};
  const btns=[...document.querySelectorAll('.filters button')], figs=[...document.querySelectorAll('#pgrid .shot')], cnt=document.getElementById('pcount'), note=document.getElementById('govnote');
  const names={all:'كل الأعمال',government:'جهات حكومية ورسمية',corporate:'شركات',private:'مناسبات خاصة وزواجات',equipment:'تجهيزات ومعدات'};
  function apply(f,push){ f=map[f]||'all'; let n=0; figs.forEach(x=>{const on=f==='all'||x.dataset.type===f; x.hidden=!on; if(on){n++; x.classList.add('in');}}); btns.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.f===f)));
    cnt.textContent=n+' · '+names[f]; note.hidden=f!=='government';
    if(push){ const u=new URL(location); if(f==='all') u.searchParams.delete('type'); else u.searchParams.set('type',f); history.replaceState(null,'',u); } }
  btns.forEach(b=>b.addEventListener('click',()=>apply(b.dataset.f,true)));
  apply(new URLSearchParams(location.search).get('type')||'all',false);
})();
</script>'''
    secs = [('gallery','المعرض','تصفية: جهات · شركات · خاصة · تجهيزات'),('contact','تواصل','')]
    return shell('portfolio.html', 'أعمالنا', 'معرض أعمال كيف الضيافة: فعاليات الشركات، الاستقبالات الرسمية، الزواجات والمناسبات الخاصة، وتجهيزات الضيافة.', secs, body, extra_js=js, hero_img='p-gala')

# ======================= about.html =======================
def build_about():
    vals = ''.join(f'<div class="val rv"><b>{t}</b><p>{d}</p></div>' for t, d in ABOUT['values'])
    body = phero('تعرّف علينا', 'من نحن في <em>كيف الضيافة</em>', ABOUT['intro'], 'ab-hall', 'قهوجيين كيف الضيافة في قاعة استقبال', crumb='من نحن')
    body += f'''<section class="on-deep glow" id="story"><div class="wrap">
  <div class="sec-head"><span class="label rv">قصتنا</span><h2 class="rv">منذ 2016 — ضيافة تُحترم فيها المقامات</h2></div>
  <div class="story"><div class="rv"><p>{ABOUT['story'][0]}</p><p>{ABOUT['story'][1]}</p>
    <div class="nums"><div><b>+500</b><small>مناسبة نُفّذت</small></div><div><b class="ar">منذ 2016</b><small>خبرة متواصلة</small></div><div><b>15</b><small>خدمة متكاملة</small></div></div></div>
    <figure class="rv" data-g="about"><img src="img/photos/ab-team.webp" alt="صبابين كيف الضيافة في مجلس قاعة" {sz('ab-team')} loading="lazy" decoding="async" data-cap="طاقم كيف الضيافة" data-sub="مجلس قاعة — جدة" style="cursor:zoom-in"></figure></div>
</div></section>
<section class="on-rich" id="values"><div class="wrap"><div class="sec-head"><span class="label rv">قيمنا</span><h2 class="rv">أربعة مبادئ لا نتنازل عنها</h2></div><div class="vals">{vals}</div></div></section>
<section class="on-deep" id="trust"><div class="wrap"><div class="sec-head"><span class="label rv">التوثيق</span><h2 class="rv">مؤسسة مسجّلة وموثّقة</h2><p class="rv">مؤسسة كيف الضيافة للأفراح والمناسبات — الرقم الوطني الموحّد <span style="font-family:var(--f-latin);direction:ltr;unicode-bidi:embed;color:var(--gold-hi)">7033069720</span>. نعمل بعروض أسعار وعقود وفواتير رسمية، ونلتزم بمتطلبات المشتريات والبروتوكول لكل جهة.</p></div>
  <div class="badges rv" style="display:flex;gap:26px;justify-content:center;align-items:center;flex-wrap:wrap"><img src="img/commerce-crop.svg" alt="وزارة التجارة" width="771" height="294" style="height:44px;width:auto" loading="lazy"><img src="img/zatca-crop.svg" alt="هيئة الزكاة والضريبة والجمارك" width="833" height="581" style="height:44px;width:auto" loading="lazy"><img src="img/sbc-crop.svg" alt="المركز السعودي للأعمال" width="748" height="206" style="height:44px;width:auto" loading="lazy"></div>
  <p class="rv" style="text-align:center;margin-top:18px;color:var(--cream-3);font-size:.86rem">تقييم عملائنا على خرائط Google: <a href="{SOCIAL['maps']}" target="_blank" rel="noopener" style="color:var(--gold-hi)">4.5 ★ من 49 تقييمًا</a></p>
</div></section>'''
    body += contact_block('نسعد <em>بخدمتكم</em>', 'استشارة مجانية حول الطاقم والزي والتقديمات المناسبة لمناسبتك.', 'السلام عليكم، أرغب بالاستفسار عن خدمات كيف الضيافة لمناسبة:\nالمدينة: \nالتاريخ: \nعدد الضيوف: ')
    secs = [('story','قصتنا',''),('values','قيمنا',''),('trust','التوثيق',''),('contact','تواصل','')]
    return shell('about.html', 'من نحن', 'كيف الضيافة — مؤسسة سعودية للضيافة الفاخرة منذ 2016: قهوجيين وصبابين وصبابات، تقديمات ومعدات، لأكثر من 500 مناسبة.', secs, body, hero_img='ab-hall')

# ======================= contact.html =======================
def build_contact():
    opts = ''.join(f'<optgroup label="{g["label"]}">' + ''.join(f'<option value="{i}">{SERVICES[i]["title"]}</option>' for i in g['ids']) + '</optgroup>' for g in SERVICE_GROUPS)
    cities = ['جدة','مكة المكرمة','المدينة المنورة','الرياض','الطائف','الدمام','أبها','ينبع']
    copts = ''.join(f'<option>{c}</option>' for c in cities) + '<option>مدينة أخرى</option>'
    ic = {'wa':WA_SVG,'tel':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>',
          'mail':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
          'ig':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
          'tt':'<svg viewBox="0 0 24 24" fill="currentColor"><path d="M16.5 3c.3 2.3 1.7 3.7 4 4v3.2c-1.5 0-2.9-.5-4-1.3V15a5.5 5.5 0 1 1-5.5-5.5c.3 0 .7 0 1 .1v3.3a2.3 2.3 0 1 0 1.3 2.1V3h3.2z"/></svg>',
          'x':'<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.5 3h3l-7 8 8 10h-6.3l-4.9-6.4L4.7 21h-3l7.5-8.6L1.5 3h6.4l4.4 5.9L17.5 3zm-1 16.2h1.7L7.6 4.7H5.8l10.7 14.5z"/></svg>',
          'snap':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 3c3 0 5 2.2 5 5v3c1 .3 2 .2 2.5-.2-.3 1-1.5 1.6-2.5 2 .8 1.7 2.3 2.8 4 3.2-.5.8-1.8 1-2.8 1.2-.2.6-.3 1.3-.6 1.5-.9-.2-1.8-.2-2.6.3-1 .6-1.8 1-3 1s-2-.4-3-1c-.8-.5-1.7-.5-2.6-.3-.3-.2-.4-.9-.6-1.5-1-.2-2.3-.4-2.8-1.2 1.7-.4 3.2-1.5 4-3.2-1-.4-2.2-1-2.5-2 .5.4 1.5.5 2.5.2V8c0-2.8 2-5 5-5z"/></svg>',
          'map':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>'}
    ways = f'''<div class="ways rv">
  <a class="way" href="https://wa.me/{WA_NUM}?text={U.quote('السلام عليكم، أرغب بالاستفسار عن خدمات كيف الضيافة لمناسبة')}" target="_blank" rel="noopener" data-ev="wa_way">{ic['wa']}<b>واتساب</b><small>{WA_DISPLAY}</small></a>
  <a class="way" href="tel:+966508252134" data-ev="tel_way">{ic['tel']}<b>اتصل بنا</b><small>{WA_DISPLAY}</small></a>
  <a class="way" href="mailto:{EMAIL}" data-ev="mail">{ic['mail']}<b>البريد</b><small>{EMAIL}</small></a>
  <a class="way" href="{SOCIAL['maps']}" target="_blank" rel="noopener" data-ev="maps">{ic['map']}<b>خرائط Google</b><small>4.5 ★ · 49 تقييمًا</small></a>
  <a class="way" href="{SOCIAL['instagram']}" target="_blank" rel="noopener" data-ev="ig">{ic['ig']}<b>إنستغرام</b><small>@keifaldiafa</small></a>
  <a class="way" href="{SOCIAL['tiktok']}" target="_blank" rel="noopener" data-ev="tt">{ic['tt']}<b>تيك توك</b><small>@keifaldiafa</small></a>
  <a class="way" href="{SOCIAL['x']}" target="_blank" rel="noopener" data-ev="x">{ic['x']}<b>X</b><small>@keifaldiafa</small></a>
  <a class="way" href="{SOCIAL['snapchat']}" target="_blank" rel="noopener" data-ev="snap">{ic['snap']}<b>سناب شات</b><small>keifaldiafa</small></a>
</div>'''
    body = phero('تواصل معنا', 'احجز قهوجيين وطاقم ضيافة <em>لمناسبتك</em>', 'نسعد بخدمتكم — املأ النموذج وستُفتح رسالة واتساب مُعدّة بكل التفاصيل، أو تواصل مباشرة بالطريقة التي تفضّلها. استشارة مجانية بلا التزام.', 'p-reception', 'استقبال VIP بقهوة وتمور', crumb='تواصل')
    body += f'''<section class="on-deep glow" id="form"><div class="wrap"><div class="cgrid">
  <form class="form rv" id="leadForm" novalidate>
    <div class="row"><label>الاسم <span aria-hidden="true" style="color:var(--gold)">*</span><input name="name" required autocomplete="name" placeholder="اسمك أو اسم الجهة"></label>
    <label>الجوال <span aria-hidden="true" style="color:var(--gold)">*</span><input name="phone" type="tel" required autocomplete="tel" inputmode="tel" placeholder="05xxxxxxxx" dir="ltr"></label></div>
    <div class="row"><label>البريد الإلكتروني<input name="email" type="email" autocomplete="email" placeholder="اختياري" dir="ltr"></label>
    <label>تاريخ المناسبة<input name="date" type="date"></label></div>
    <div class="row"><label>المدينة<select name="city">{copts}</select></label>
    <label>عدد الضيوف التقريبي<input name="guests" type="number" min="1" inputmode="numeric" placeholder="مثال: 200" dir="ltr"></label></div>
    <label>الخدمة المطلوبة<select name="service" id="svcSel"><option value="">اختر الخدمة</option>{opts}<optgroup label="أخرى"><option value="offerings">تقديمات ومعدات</option><option value="package">باقة متكاملة (طاقم + تقديمات + تجهيز)</option></optgroup></select></label>
    <label>تفاصيل المناسبة <span aria-hidden="true" style="color:var(--gold)">*</span><textarea name="message" required placeholder="نوع المناسبة، المكان، الوقت، أي طلبات خاصة"></textarea></label>
    <p class="note" id="formErr" role="alert" hidden style="color:#f0b3b3"></p>
    <button class="btn btn-gold btn-block" type="submit" data-ev="lead_submit">{WA_SVG}أرسل عبر واتساب</button>
    <p class="note">لا يُخزَّن أي شيء هنا — تُفتح رسالة واتساب بالتفاصيل ليتابعها فريقنا معك مباشرة.</p>
  </form>
  <div>
    <div class="sec-head" style="text-align:start;margin-bottom:14px"><span class="label rv">أو مباشرة</span><h2 class="rv" style="font-size:1.5rem">طرق التواصل</h2></div>
    {ways}
  </div>
</div></div></section>
<section class="cities on-black" id="cities" aria-label="المدن التي نخدمها"><div class="wrap rv"><span class="lbl">نصل إليكم في:</span>{''.join(f'<a{" class=\"main\"" if c["slug"]=="jeddah" else ""} href="{city_page(c["slug"])}">{c["ar"]}</a>' for c in CITIES)}<a href="locations.html">كل المدن ›</a><span class="lbl" style="margin-inline-start:6px">وجميع مناطق المملكة</span></div></section>'''
    js = f'''<script>
(function(){{
  const f=document.getElementById('leadForm'), err=document.getElementById('formErr'), sel=document.getElementById('svcSel');
  const pre=new URLSearchParams(location.search).get('service'); if(pre&&sel.querySelector('option[value="'+pre+'"]')) sel.value=pre;
  const svcName=v=>{{const o=sel.querySelector('option[value="'+v+'"]'); return o?o.textContent:''}};
  f.addEventListener('submit',e=>{{ e.preventDefault(); const d=Object.fromEntries(new FormData(f)); err.hidden=true;
    if(!d.name.trim()||!d.phone.trim()||!d.message.trim()){{ err.textContent='يرجى إدخال الاسم والجوال وتفاصيل المناسبة.'; err.hidden=false; f.querySelector(':invalid')?.focus(); return; }}
    const lines=['مرحباً، أنا '+d.name.trim(),'📱 '+d.phone.trim()]; if(d.email) lines.push('📧 '+d.email); if(d.service) lines.push('🎯 الخدمة: '+svcName(d.service)); if(d.date) lines.push('📅 التاريخ: '+d.date); if(d.city) lines.push('📍 المدينة: '+d.city); if(d.guests) lines.push('👥 عدد الضيوف: '+d.guests); lines.push('💬 '+d.message.trim());
    (window.dataLayer=window.dataLayer||[]).push({{event:'lead_wa',service:d.service||'',city:d.city}});
    window.open('https://wa.me/{WA_NUM}?text='+encodeURIComponent(lines.join('\\n')),'_blank','noopener'); }});
}})();
</script>'''
    secs = [('form','نموذج طلب عرض',''),('cities','المدن','')]
    return shell('contact.html', 'تواصل معنا', 'تواصل مع كيف الضيافة: واتساب 0508252134، نموذج طلب عرض يُرسل عبر واتساب، البريد، وحسابات التواصل. نصل إلى جميع مناطق المملكة.', secs, body, extra_js=js, hero_img='p-reception')


# ======================= v6.3 — الصفحات المحلية (D55–D62) =======================
LOCAL_CSS = '''
/* ===== v6.3 — المدن / خدمة×مدينة / social / legal ===== */
.phero.noimg{min-height:auto;background:radial-gradient(ellipse at 50% 0%,rgba(197,160,89,.14),transparent 60%),var(--rich)}
.phero.noimg::before{background:none}
.badges-l{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-top:14px}
.badges-l span{border:1px solid rgba(197,160,89,.35);border-radius:999px;padding:5px 13px;font-size:.8rem;color:var(--gold-hi);background:rgba(13,13,13,.45)}
.lsec{padding-block:40px}
.lsec+.lsec{border-top:1px solid var(--line)}
.split{display:grid;gap:16px;align-items:center}
.split h2{font-size:clamp(1.3rem,4.4vw,1.8rem);color:var(--gold-hi);line-height:1.4}
.split p{margin-top:10px;color:var(--cream-2);font-size:.97rem}
.split .kick{display:block;font-size:.74rem;letter-spacing:.3em;color:var(--gold);margin-bottom:6px}
.split figure{position:relative;border-radius:18px;overflow:hidden;aspect-ratio:4/3;cursor:zoom-in;background:var(--black);border:1px solid var(--line-2)}
.split figure img{width:100%;height:100%;object-fit:cover}
.split .btn{margin-top:14px}
.split .zoom{position:absolute;bottom:8px;inset-inline-end:8px;width:28px;height:28px;border-radius:50%;background:rgba(13,13,13,.6);border:1px solid var(--line-2);display:grid;place-items:center;color:var(--gold-hi);font-size:.9rem}
.pk{display:grid;gap:12px}
.pk article{border:1px solid var(--line-2);border-radius:18px;padding:18px;background:rgba(36,36,36,.55)}
.pk h3{font-size:1.1rem;color:var(--gold-hi)}
.pk p{color:var(--cream-2);font-size:.92rem;margin-top:6px}
.pk .feats{grid-template-columns:1fr}
.eq{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.eq figure{text-align:center;border:1px solid var(--line);border-radius:14px;padding:10px 6px;background:radial-gradient(circle at 50% 35%,rgba(197,160,89,.12),transparent 70%)}
.eq img{width:100%;max-width:120px;height:auto;aspect-ratio:1;margin-inline:auto;display:block}
.eq figcaption{font-size:.78rem;color:var(--cream-2);margin-top:4px}
.why{display:grid;grid-template-columns:1fr;gap:10px}
.why li{list-style:none;display:flex;gap:10px;align-items:flex-start;border:1px solid var(--line);border-radius:14px;padding:12px 14px;background:rgba(36,36,36,.45);color:var(--cream);font-size:.92rem;line-height:1.6}
.why li::before{content:"✦";color:var(--gold);font-size:.75rem;margin-top:.4em}
.lgal{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
.lgal figure{position:relative;border-radius:12px;overflow:hidden;aspect-ratio:1;cursor:zoom-in;background:var(--black);border:1px solid var(--line)}
.lgal img{width:100%;height:100%;object-fit:cover;transition:transform .8s cubic-bezier(.22,1,.36,1)}
.lgal figure:hover img{transform:scale(1.05)}
.lgal .zoom{position:absolute;bottom:8px;inset-inline-end:8px;width:28px;height:28px;border-radius:50%;background:rgba(13,13,13,.6);border:1px solid var(--line-2);display:grid;place-items:center;color:var(--gold-hi);font-size:.9rem}
.dist{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
.dist span,.lnk a{border:1px solid rgba(197,160,89,.3);border-radius:999px;padding:6px 14px;font-size:.86rem;color:var(--cream-2)}
.lnk{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
.lnk a{color:var(--gold-hi);transition:.25s}
.lnk a:hover{background:rgba(197,160,89,.1);border-color:var(--line-hi)}
.band{text-align:center;padding-block:44px}
.band h2{font-size:clamp(1.4rem,5vw,2rem);color:var(--cream)}
.band p{color:var(--cream-2);margin:10px auto 18px;max-width:56ch}
.cgrid-l{display:grid;gap:12px}
.cgrid-l a{display:block;border:1px solid var(--line-2);border-radius:18px;padding:18px;background:rgba(36,36,36,.55);transition:.3s}
.cgrid-l a:hover{border-color:var(--line-hi);transform:translateY(-3px)}
.cgrid-l b{display:block;font-family:var(--f-head);font-size:1.15rem;color:var(--gold-hi)}
.cgrid-l small{display:block;color:var(--cream-3);font-size:.8rem;margin-top:2px}
.cgrid-l p{color:var(--cream-2);font-size:.9rem;margin-top:8px}
.cgrid-l .more{display:inline-block;margin-top:10px;color:var(--gold);font-size:.86rem}
.qr{display:grid;gap:16px;justify-items:center;text-align:center;border:1px solid var(--line-2);border-radius:20px;padding:22px;background:rgba(36,36,36,.55)}
.qr img{width:220px;height:220px;border-radius:14px;background:#fff;padding:8px}
.qr p{color:var(--cream-2);font-size:.92rem;max-width:48ch}
.qr .num{direction:ltr;unicode-bidi:isolate;font-family:var(--f-latin);color:var(--gold-hi);letter-spacing:.06em}
.prose{max-width:70ch;margin-inline:auto}
.prose h2{font-size:1.25rem;color:var(--gold-hi);margin-top:28px}
.prose p,.prose li{color:var(--cream-2);font-size:.95rem;line-height:1.9;margin-top:8px}
.prose ul{padding-inline-start:20px}
.prose .foot{margin-top:28px;color:var(--cream-3);font-size:.86rem;border-top:1px solid var(--line);padding-top:14px}
@media (min-width:900px){
  .lsec{padding-block:56px}
  .split{grid-template-columns:1fr 1fr;gap:36px}
  .split.rev figure{order:-1}
  .pk{grid-template-columns:repeat(3,1fr);gap:16px}
  .eq{grid-template-columns:repeat(6,1fr);gap:12px}
  .why{grid-template-columns:repeat(3,1fr);gap:14px}
  .lgal{grid-template-columns:repeat(6,1fr);gap:10px}
  .cgrid-l{grid-template-columns:repeat(4,1fr);gap:16px}
  .qr{grid-template-columns:auto 1fr;text-align:start;justify-items:start;align-items:center;gap:28px}
}
'''
LOC_CRUMB = ('المدن', 'locations.html')

def lfig(name, alt, cap, sub, g):
    return f'<figure class="rv" data-g="{g}"><img src="img/photos/{name}.webp" alt="{esc(alt)}" {sz(name)} loading="lazy" decoding="async" data-cap="{esc(cap)}" data-sub="{esc(sub)}"><span class="zoom" aria-hidden="true">⤢</span></figure>'

def sec_head(label, h2, p='', hint=False):
    return f'<div class="sec-head"><span class="label rv">{label}</span><h2 class="rv">{h2}</h2>{f"<p class=\"rv\">{p}</p>" if p else ""}{HINT if hint else ""}</div>'

def eq_strip():
    figs = ''.join(f'<figure class="rv"><img src="img/cutouts/{f}.webp" alt="{esc(n)}" width="480" height="480" loading="lazy" decoding="async"><figcaption>{n}</figcaption></figure>' for f, n in CUTOUT_ITEMS)
    return f'<section class="lsec on-black grain" id="equipment"><div class="wrap">{sec_head("عدّة الضيافة", "دلالنا وفناجيننا تصل معنا", "الدلال والفناجين وأطقم التقديم ضمن الخدمة — لا تحتاج تجهيز شيء.")}<div class="eq">{figs}</div></div></section>'

def links_block(h2, links, id_='links'):
    a = ''.join(f'<a href="{l["href"]}">{l["label"]}</a>' for l in links)
    return f'<section class="lsec on-rich" id="{id_}"><div class="wrap">{sec_head("روابط", h2)}<div class="lnk rv">{a}</div></div></section>'

def dist_block(h2, districts):
    return f'<section class="lsec on-deep" id="districts"><div class="wrap">{sec_head("التغطية", h2)}<div class="dist rv">{"".join(f"<span>{d}</span>" for d in districts)}</div></div></section>'

# v6.8 (D96): التخطيط المحلي القديم (local_page/build_city — phero + بطاقات + معرض) حُذف؛ صفحات المدن والصفحة النيّة تمرّ الآن عبر master_page (لغة تصميم واحدة لكل الصفحات المحلية).
CITY_ROLE_IMG = {'sababin-qahwa': ('sv-hosts-1', 'صبابين بالزي التراثي', 'قاعة استقبال'), 'qahwajiin': ('sv-hosts-4', 'قهوجيين بزي رسمي', 'فعالية'), 'diyafa-munasabat': ('sv-buffet-2', 'بوفيه ضيافة', 'تجهيز')}

def city_content(city):
    """D96: سجلّ صفحة المدينة بمخطّط master_page نفسه — kind='city'. الأدوار = أول فقرة محلية لكل خدمة من الثلاث (محتوى فريد لكل مدينة) مع زر إلى صفحتها."""
    c = CITY[city]; ar = c['ar']; ci = [x['slug'] for x in CITIES].index(city)
    hero = CITY_HERO[ci % len(CITY_HERO)]
    imgs = [CITY_ROLE_IMG[s['slug']] for s in LOCAL_SERVICES]
    for k in range(4):   # يكمل الشريط إلى 8 لقطات من مجمّعات الخدمات الثلاث بالتناوب حسب المدينة
        for s in LOCAL_SERVICES:
            for t in pick(s['slug'], ci + k, 2):
                if t[0] != hero and t[0] not in [x[0] for x in imgs] and len(imgs) < 8: imgs.append(t)
    sections = []
    for s in LOCAL_SERVICES:
        h2, txt = local_content(s['slug'], city)['sections'][0][:2]
        sections.append((h2, txt, s['kicker'], page_of(s['slug'], city), f'{s["ar"]} {ar} ›'))
    wa_t = f'السلام عليكم، أرغب بالاستفسار عن خدمات الضيافة لمناسبة في {ar}:\nالتاريخ: \nالمكان: \nعدد الضيوف: '
    return {'kind': 'city', 'slug': city_page(city)[:-5], 'service': {'ar': 'الضيافة', 'slug': 'city', 'kicker': 'في ' + ar}, 'city': c,
            'h1': (f'ضيافة فاخرة في {ar}', 'بطاقم سعودي وعدّة كاملة'), 'title': f'ضيافة فاخرة في {ar} — قهوجيين وصبابين ومناسبات', 'desc': c['lead'], 'intro': c['lead'],
            'sections': sections, 'packages': None, 'why': c['highlights'] + WHY_US(ar)[:3],
            'faqs': c['faqs'] + [('هل تشمل الخدمة المعدات والتقديمات؟', 'نعم — الدلال والفناجين والتمر والتقديمات ضمن الخدمة أو بحسب طلبك.')],
            'imgs': imgs, 'hero': hero, 'others': [], 'districts': c['districts'],
            'other_cities': [{'label': o['ar'], 'href': city_page(o['slug'])} for o in CITIES if o['slug'] != city], 'wa': wa_t}

def build_city(city):
    return master_page(city_content(city))

def build_locations():
    wa_t = 'السلام عليكم، أرغب بالاستفسار عن خدمات الضيافة لمناسبة:\nالمدينة: \nالتاريخ: \nعدد الضيوف: '
    body = phero('المدن', 'نصل إليكم في <em>ثماني مدن</em> وما حولها', 'قاعدتنا جدة، ونخدم مكة والمدينة والرياض والطائف والدمام وأبها وينبع بطاقم وعدّة كاملة — مع ترتيب الانتقال والإقامة عند الحاجة.', 'p-hall', 'قاعة استقبال — كيف الضيافة', wa(wa_t, 'btn btn-gold', 'تواصل عبر واتساب', 'wa_hero'), crumb='المدن')
    cards = ''.join(f'<a class="rv" href="{city_page(c["slug"])}"><b>{c["ar"]}</b><small>{c["region"]}</small><p>{c["intro"]}</p><span class="more">خدماتنا في {c["ar"]} ›</span></a>' for c in CITIES)
    body += f'<section class="lsec on-deep glow" id="cities"><div class="wrap">{sec_head("التغطية", "اختر مدينتك")}<div class="cgrid-l">{cards}</div></div></section>'
    body += links_block('صفحات الخدمات بحسب المدينة', [{'label': f'{s["ar"]} {c["ar"]}', 'href': page_of(s['slug'], c['slug'])} for s in LOCAL_SERVICES for c in CITIES] + [{'label': 'مباشرين قهوة جدة', 'href': 'mubashirin-qahwa-jeddah.html'}], 'all')
    body += contact_block('مدينتك غير موجودة؟ <em>تواصل معنا</em>', 'نصل إلى جميع مناطق المملكة بحسب التوفّر وترتيب الانتقال.', wa_t)
    return shell('locations.html', 'المدن التي نخدمها', 'كيف الضيافة تخدم جدة ومكة والمدينة والرياض والطائف والدمام وأبها وينبع — قهوجيين وصبابين وضيافة مناسبات في كل مدينة.', [], body, extra_css=LOCAL_CSS, hero_img='p-hall')

def build_social():
    from data import SOCIAL
    body = phero('تابعنا', 'تابعنا وشاهد <em>ضيافتنا</em> — قبل أن تحجزها', 'كل مناسبة نخدمها نصوّرها: القاعات، الكاونترات، الطاقم بزيّه، والتوزيعات. تابعنا على المنصّة التي تفضّلها أو امسح الباركود.', None, '', crumb='حساباتنا')
    body += f'''<section class="lsec on-deep glow" id="qr"><div class="wrap"><div class="qr rv"><img src="img/brand/qr-keif-aldiafa.png" alt="باركود واتساب كيف الضيافة" width="984" height="984" loading="lazy" decoding="async"><div><h2 style="color:var(--gold-hi);font-size:1.3rem">امسح الباركود</h2><p>وجّه كاميرا هاتفك إلى الرمز لفتح محادثة واتساب معنا مباشرة — أو احفظ الرقم: <a class="num" href="tel:+966508252134">{WA_DISPLAY}</a></p>{wa('السلام عليكم، أرغب بالاستفسار عن خدمات كيف الضيافة', 'btn btn-wa btn-sm', 'افتح واتساب', 'wa_qr')}</div></div></div></section>'''
    nets = ''.join(f'<a class="rv" href="{SOCIAL[k]}" target="_blank" rel="noopener" data-ev="{k}"><b>{n}</b><small dir="ltr" style="unicode-bidi:isolate">{h}</small><p>{d}</p></a>' for k, n, h, d in SOCIAL_NETS)
    body += f'<section class="lsec on-rich" id="nets"><div class="wrap">{sec_head("منصّاتنا", "خمس منصّات — محتوى مختلف في كل واحدة")}<div class="cgrid-l">{nets}</div></div></section>'
    body += contact_block('أعجبك ما رأيت؟ <em>احجزه</em>', 'أرسل المدينة والتاريخ وعدد الضيوف على واتساب.', 'السلام عليكم، شاهدت حساباتكم وأرغب بالاستفسار لمناسبة:\nالمدينة: \nالتاريخ: \nعدد الضيوف: ')
    return shell('social.html', 'تابعنا وشاهد ضيافتنا', 'حسابات كيف الضيافة على إنستغرام وتيك توك وسناب شات وإكس وفيسبوك — صور وفيديوهات من مناسبات نفّذناها، وباركود للتواصل عبر واتساب.', [], body, extra_css=LOCAL_CSS)

def build_legal():
    body = phero('الحقوق', 'الحقوق القانونية <em>والملكية الفكرية</em>', 'معلومات الحقوق القانونية والملكية الفكرية لصور ومحتوى موقع كيف الضيافة.', None, '', crumb='الحقوق القانونية')
    secs = ''
    for h2, ps in LEGAL_SECTIONS:
        secs += f'<h2>{h2}</h2>' + ''.join(f'<p>{p}</p>' for p in ps)
    body += f'<section class="lsec on-deep" id="legal"><div class="wrap"><div class="prose rv">{secs}<p class="foot">مؤسسة كيف الضيافة للأفراح والمناسبات — الرقم الوطني الموحّد <span dir="ltr">7033069720</span> · آخر تحديث 2026.</p></div></div></section>'
    return shell('legal.html', 'الحقوق القانونية والملكية الفكرية', 'معلومات الحقوق القانونية والملكية الفكرية لصور ومحتوى موقع كيف الضيافة — مؤسسة سعودية لخدمات الضيافة الفاخرة.', [], body, extra_css=LOCAL_CSS)

# ======================= v6.4 — الصفحة النموذجية (خدمة×مدينة) D63–D70 =======================
# صفحة واحدة بمستوى الرئيسية (وأفضل): «من كل شيء شوية — بس مخصّصة للمدينة». تُعمَّم بعد اعتماد المالك عبر MASTER_PAGES.
def _home_section(id_):
    """يقصّ قسمًا كاملًا من index.html (مصدر حقيقة واحد للشعارات والزي — D64)."""
    a = IDX.index(f'id="{id_}"'); a = IDX.rfind('<section', 0, a); b = IDX.index('</section>', a) + len('</section>')
    return IDX[a:b]

MASTER_CSS = '''
/* ===== v6.4 — الصفحة النموذجية (خدمة×مدينة) ===== */
.hero.hero-l{min-height:0;height:auto;max-height:none;padding:40px 0 36px}
.hero.hero-l::before{background:linear-gradient(180deg,rgba(13,13,13,.62) 0%,rgba(13,13,13,.55) 45%,rgba(13,13,13,.9) 85%,var(--rich) 100%)}
.hero.hero-l .bg img{object-position:center 35%}
.hero.hero-l .crumb{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;font-size:.78rem;color:var(--cream-3);margin-bottom:16px;text-shadow:0 1px 2px rgba(0,0,0,.6)}
.hero.hero-l .crumb a{color:var(--gold-hi)}
.hero.hero-l .crumb span:last-child{color:var(--cream)}
.hero.hero-l .hcard{max-width:560px}
.hero.hero-l h1{font-size:clamp(1.45rem,5vw,2.15rem);line-height:1.45}
.hero.hero-l h1 em{font-style:normal;background:var(--grad-gold);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.hero.hero-l .badges-l{margin-top:14px}
.hero.hero-l .badges-l span{background:rgba(13,13,13,.55)}
.hero.hero-l .cta .btn-glass{white-space:nowrap}
@media (min-width:900px){.hero.hero-l{padding:56px 0 48px}.hero.hero-l .hcard{max-width:660px}.hero.hero-l h1{font-size:2.4rem}}
/* أعمالنا: وسم المدينة بالذهبي على يسار الصورة */
.shot .tag.city{inset-inline-start:auto;inset-inline-end:10px;background:var(--grad-gold);color:var(--black);border-color:transparent;font-weight:700}
/* لمن نخدم: وصف قصير يظهر على الجوال أيضًا */
.who-l .who small{display:block;font-size:.7rem;margin-top:2px}
@media (min-width:900px){.who-l .who small{font-size:.86rem}}
/* الخدمات: بطاقات المدينة (محلية) مميّزة */
.svc.local{border-color:var(--line-hi);box-shadow:0 0 34px rgba(197,160,89,.1)}
.svc.local b::after{content:" ✦";color:var(--gold);font-size:.75em}
/* الترتيبات: زر أسفل كل بطاقة */
.pk article .btn{margin-top:14px;width:100%}
/* ===== v6.5 — إعادة الهيكلة (D71–D78) ===== */
/* شركاء النجاح — نسخة مضغوطة بلا فراغ (D73): 6 شعارات بالجوال، 12 بالحاسوب، بلا .rv (تظهر فورًا) */
.partners.compact{padding-block:28px}
.partners.compact .sec-head{margin-bottom:14px}
.partners.compact .sec-head h2{font-size:clamp(1.15rem,3.8vw,1.6rem)}
.partners.compact .logos{grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.partners.compact .logo{height:72px;padding:10px}
.partners.compact .logo img{inset:10px;width:calc(100% - 20px);height:calc(100% - 20px)}
.partners.compact .logos.collapsed .logo:nth-child(n+7){display:none}
.partners.compact .logos:not(.collapsed) .logo{animation:up .5s both}
.partners.compact .works-foot{margin-top:14px}
.partners.compact .works-foot .btn{border:1px solid rgba(197,160,89,.5);color:var(--ink);background:#fff}
@media (min-width:900px){.partners.compact{padding-block:40px}.partners.compact .logos{grid-template-columns:repeat(6,1fr);gap:12px}.partners.compact .logo{height:92px}.partners.compact .logos.collapsed .logo:nth-child(n+7){display:grid}.partners.compact .logos.collapsed .logo:nth-child(n+13){display:none}}
/* الخدمات: صور صغيرة 16:10 دائمًا (D74 — لا width/height على .svc img) */
#services .svc img{height:auto;aspect-ratio:16/10}
/* كيف نعمل: ثلاثة صفوف نص/صورة في قسم واحد (D75) */
.roles .split{margin-top:22px}
.roles .split:first-of-type{margin-top:0}
.roles .split h2{font-size:clamp(1.1rem,3.8vw,1.4rem)}
.roles .split figure{aspect-ratio:16/10}
@media (min-width:900px){.roles .split{margin-top:40px}.roles .split figure{aspect-ratio:4/3}}
/* التقديمات والعدّة: المقصوصات تحت الشريط */
#offerings .eq{margin-top:18px}
/* صف الأيقونات — آخر الصفحة (D76) */
/* .socrow: الأنماط في index.html (D93) */
@media (prefers-reduced-motion:reduce){.socrow .ic::after{animation:none}}
/* الهيرو المتحرك (D84): شرائح تتبدّل فوق صورة الهيرو بتلاشٍ + تقريب بطيء — الصورة الأولى تبقى LCP */
.hero-anim .slides{position:absolute;inset:0;z-index:0;pointer-events:none}
.hero-anim .slides img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 35%;opacity:0;transition:opacity 1.6s ease}
.hero-anim .slides img.on{opacity:1;animation:kbz 9s ease-in-out both}
.hero-anim .bg picture img{transition:opacity 1.6s ease}.hero-anim.away .bg picture img{opacity:0}
@keyframes kbz{from{transform:scale(1)}to{transform:scale(1.08)}}
@media (prefers-reduced-motion:reduce){.hero-anim .slides{display:none}.hero-anim.away .bg picture img{opacity:1}}
/* مسافات الجوال بين الأقسام المتتالية — أخفّ من الرئيسية (48px) */
@media (max-width:899px){#works,#services,#offerings,#faq{padding-block:40px}}
'''

MASTER_HERO = {('qahwajiin', 'jeddah'): 'pf-eq-7'}   # D65: صورة هيرو ثابتة (picture) — دلال ذهبية في قاعة، تُقرأ فوقها البطاقة الزجاجية
HERO_SLIDES = {('qahwajiin', 'jeddah'): ['p-hall', 'sv-hosts-4', 'pf-co-1']}   # D84: خلفية متغيّرة — تتبدّل فوق صورة الهيرو بتلاشٍ بطيء (Ken Burns)، تُحمَّل بعد الأولى
LATIN = {'jeddah': 'Jeddah', 'riyadh': 'Riyadh', 'makkah': 'Makkah', 'madinah': 'Madinah', 'taif': 'Taif', 'dammam': 'Dammam', 'abha': 'Abha', 'yanbu': 'Yanbu'}
LOC_IMG = {'sababin-qahwa': 'sv-hosts-1', 'qahwajiin': 'sv-hosts-4', 'diyafa-munasabat': 'sv-buffet-2'}   # D86: صورة كل بطاقة تطابق اسمها (صبابين بزي تراثي / قهوجيين بزي رسمي / بوفيه ضيافة)
SVC_IMG = {'hostesses': 'sv-hostess-1', 'zamzam': 'sv-zamzam-3', 'safarjia': 'sv-safarjia-1', 'counter': 'sv-counter-1', 'heritage-tent': 'sv-tent-2', 'buffet': 'sv-buffet-3'}   # D86: بطاقات «تكمّل مناسبتك»
COMPLEMENT = ['hostesses', 'zamzam', 'safarjia', 'counter', 'heritage-tent', 'buffet']

SOC_ICON = {   # D76: أيقونات المنصّات (Simple Icons، CC0) — مسارات فقط، تُلوَّن بالذهبي
'instagram': 'M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228.6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773.056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-.0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809.0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-.264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1.17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-.4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1.805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-.9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608.216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056.4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-.419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-.0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077',
'tiktok': 'M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z',
'snapchat': 'M12.206.793c.99 0 4.347.276 5.93 3.821.529 1.193.403 3.219.299 4.847l-.003.06c-.012.18-.022.345-.03.51.075.045.203.09.401.09.3-.016.659-.12 1.033-.301.165-.088.344-.104.464-.104.182 0 .359.029.509.09.45.149.734.479.734.838.015.449-.39.839-1.213 1.168-.089.029-.209.075-.344.119-.45.135-1.139.36-1.333.81-.09.224-.061.524.12.868l.015.015c.06.136 1.526 3.475 4.791 4.014.255.044.435.27.42.509 0 .075-.015.149-.045.225-.24.569-1.273.988-3.146 1.271-.059.091-.12.375-.164.57-.029.179-.074.36-.134.553-.076.271-.27.405-.555.405h-.03c-.135 0-.313-.031-.538-.074-.36-.075-.765-.135-1.273-.135-.3 0-.599.015-.913.074-.6.104-1.123.464-1.723.884-.853.599-1.826 1.288-3.294 1.288-.06 0-.119-.015-.18-.015h-.149c-1.468 0-2.427-.675-3.279-1.288-.599-.42-1.107-.779-1.707-.884-.314-.045-.629-.074-.928-.074-.54 0-.958.089-1.272.149-.211.043-.391.074-.54.074-.374 0-.523-.224-.583-.42-.061-.192-.09-.389-.135-.567-.046-.181-.105-.494-.166-.57-1.918-.222-2.95-.642-3.189-1.226-.031-.063-.052-.15-.055-.225-.015-.243.165-.465.42-.509 3.264-.54 4.73-3.879 4.791-4.02l.016-.029c.18-.345.224-.645.119-.869-.195-.434-.884-.658-1.332-.809-.121-.029-.24-.074-.346-.119-1.107-.435-1.257-.93-1.197-1.273.09-.479.674-.793 1.168-.793.146 0 .27.029.383.074.42.194.789.3 1.104.3.234 0 .384-.06.465-.105l-.046-.569c-.098-1.626-.225-3.651.307-4.837C7.392 1.077 10.739.807 11.727.807l.419-.015h.06z',
'x': 'M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z',
'facebook': 'M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z',
}
SOC_LABEL = {'instagram': 'إنستغرام', 'tiktok': 'تيك توك', 'snapchat': 'سناب شات', 'x': 'إكس', 'facebook': 'فيسبوك'}

def foot(href, label):
    """زر واحد أسفل كل قسم عيّنة → الصفحة العامة التي تحوي كل شيء (Q1/Q2 — D72)."""
    return f'<div class="works-foot rv"><a class="btn btn-glass" href="{href}">{label}</a></div>'

def social_row(wa_text):
    """صف الأيقونات: واتساب + كل حسابات المالك — في آخر الصفحة قبل الفوتر (Q5 — D76)."""
    from data import SOCIAL
    items = ''   # D90: بلا واتساب هنا (له زره الطافي وأزرار الحجز) — 5 منصات في صف واحد بألوان علاماتها
    for k, n, h, d in SOCIAL_NETS:
        items += f'<a class="s-{k}" href="{SOCIAL[k]}" target="_blank" rel="noopener" data-ev="{k}" aria-label="{n} — {esc(h)}"><span class="ic"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="{SOC_ICON[k]}"/></svg></span><small>{n}</small></a>'
    return f'<section class="lsec on-black grain" id="follow"><div class="wrap">{sec_head("تابعنا", "شاهد مناسباتنا <em>لحظة بلحظة</em>", "صور وفيديوهات من قلب المناسبات على حساباتنا.")}<div class="socrow rv">{items}</div></div></section>'

def master_page(rec):
    """الصفحة النموذجية خدمة×مدينة — v6.5: 15 قسمًا مرتّبة بالأهمية (D71–D78)، كل قسم عيّنة + زر للصفحة العامة.
    v6.8 (D96/D97): تخدم أيضًا صفحات المدن (kind='city') والصفحة النيّة (kind='intent') — فروق صغيرة في المسار والعناوين والروابط فقط."""
    s, c, ar = rec['service'], rec['city'], rec['city']['ar']
    kind = rec.get('kind', 'svc'); is_city = kind == 'city'
    slug = rec['slug']; cur = slug + '.html'; g = 'l-' + slug
    ci = [x['slug'] for x in CITIES].index(c['slug'])
    hero = MASTER_HERO.get((s['slug'], c['slug']), rec['hero'])
    imgs = [x for x in rec['imgs'] if x[0] != hero]          # لا نكرّر صورة الهيرو في الشريط
    shots, roles = imgs[:8], imgs[8:] + imgs[:3]
    latin = LATIN.get(c['slug'], c['ar']); h1a, h1b = rec['h1']
    cityp = city_page(c['slug'])
    # 1) الهيرو — الوعد + واتساب + الأرقام (فوق الطيّة)؛ فئات العملاء داخل .pts (D71: أُدمج «لمن نخدم» هنا)
    crumbs = '<span>›</span>'.join([f'<a href="index.html">الرئيسية</a>', f'<a href="locations.html">المدن</a>'] + ([f'<span>{ar}</span>'] if is_city else [f'<a href="{cityp}">{ar}</a>', f'<span>{s["ar"]} {ar}</span>']))
    hp = HERO_POOL.get(s['slug'], [])
    pool = HERO_SLIDES.get((s['slug'], c['slug'])) or [x for x in (hp[ci % 3:] + hp[:ci % 3] + CITY_HERO[ci + 1:] + CITY_HERO[:ci + 1]) if x != hero]   # D95: شرائح تختلف بحسب الخدمة والمدينة
    seen = []; [seen.append(x) for x in pool if x not in seen]
    slides = ''.join(f'<img class="slide" src="img/photos/{n}.webp" alt="" {sz(n)} loading="lazy" decoding="async">' for n in seen[:3])
    body = f"""<section class="hero hero-l hero-anim" aria-label="{esc(s['ar'] + ' في ' + ar)}">
  <div class="bg" aria-hidden="true">{hero_img(hero, '')}<div class="slides">{slides}</div></div>
  <div class="wrap">
    <nav class="crumb" aria-label="مسار التنقل">{crumbs}</nav>
    <div class="hcard">
      <p class="kicker latin">{latin} · Since 2016</p>
      <p class="brandword">كيف الضيافة</p>
      <div class="rule" aria-hidden="true"></div>
      <div class="sub-latin latin"><span class="l1">Keif Al-Diafa</span><span class="l2">{latin}</span></div>
      <h1>{h1a} <em>{h1b}</em></h1>
      <p class="sub">{rec['intro']}</p>
      <div class="pts"><span>جهات وفعاليات رسمية</span><span>شركات ومعارض</span><span>أعراس ومناسبات خاصة</span></div>
      <div class="badges-l"><span>+500 مناسبة منذ 2016</span><span>طاقم سعودي مدرّب</span><span>كل أحياء {ar}</span></div>
    </div>
    <div class="cta">{wa(rec['wa'], 'btn btn-gold', 'احجز عبر واتساب', 'wa_hero')}<a class="btn btn-glass" href="#works">أعمالنا</a></div>
    <div class="proof" aria-label="أرقامنا"><a href="#works" title="شاهد الأعمال"><b>+500</b>مناسبة نُفّذت</a><i></i><span><b class="ar">منذ 2016</b>خبرة متواصلة</span></div>
  </div>
</section>"""
    # 2) أعمالنا — 8 لقطات صغيرة (3:4، لايت بوكس) بوسم المدينة → معرض الأعمال الكامل
    figs = ''.join(f'<figure class="shot" data-g="{g}" data-go="portfolio.html" data-go-txt="معرض الأعمال"><img src="img/photos/{n}.webp" alt="{esc(cap)}" {sz(n)} loading="lazy" decoding="async" data-cap="{esc(cap)}" data-sub="{esc(sub)}"><figcaption><b>{cap}</b><span>{sub}</span></figcaption></figure>' for n, cap, sub in shots)
    body += f'<section class="on-black grain" id="works"><div class="wrap">{sec_head("أعمالنا", f"من أعمالنا في <em>{ar}</em>" if is_city else f"من أعمالنا — <em>{s["ar"]}</em>", "لقطات حقيقية من مناسبات نفّذناها. اضغط على أي صورة لتكبيرها والتنقّل بين الباقي.", hint=True)}<div class="strip rv">{figs}<span class="edge"></span></div>{foot("portfolio.html", "معرض الأعمال الكامل")}</div></section>'
    # 3) شركاء النجاح — نسخة مضغوطة: 6 شعارات بالجوال / 12 بالحاسوب، بلا فراغ (D73) → كل الشركاء في الرئيسية
    logos = re.findall(r'<div class="logo"><img [^>]+></div>', _home_section('partners'))
    body += f'<section class="partners compact" id="partners"><div class="wrap"><div class="sec-head"><span class="label">شركاء النجاح</span><h2>جهات وشركات وثقت بنا — في {ar} وخارجها</h2></div><div class="logos collapsed" id="plogos" aria-label="شركات">{"".join(logos)}</div><div class="works-foot"><button class="btn btn-sm" id="plogosMore" type="button" aria-expanded="false" aria-controls="plogos">كل شركاء النجاح · {len(logos)} جهة</button></div></div></section>'
    # 4) الخدمات — بطاقات صغيرة 16:10 (بلا width/height: إصلاح الصور الطويلة — D74) → كل الخدمات
    def svc(href, img, b, small, local=False):
        return f'<a class="svc rv{" local" if local else ""}" href="{href}"><img src="img/photos/{img}.webp" alt="{esc(b)}" loading="lazy" decoding="async"><div><b>{b}</b><small>{small}</small></div></a>'
    grid = f'<h3 class="svc-grp rv">خدماتنا في {ar}</h3>'
    grid += ''.join(svc(page_of(o['slug'], c['slug']), LOC_IMG[o['slug']], f'{o["ar"]} {ar}', o['short'], True) for o in LOCAL_SERVICES if o['slug'] != s['slug'])
    grid += ''.join(svc(p['slug'] + '.html', 'sv-hosts-3', p['ar'], p['short'], True) for p in INTENT_PAGES if p['city'] == c['slug'] and p['slug'] != slug)
    grid += '<h3 class="svc-grp rv">تكمّل مناسبتك</h3>' + ''.join(svc(f'services.html#{k}', SVC_IMG.get(k, SERVICE_HERO_IMG[k]), SERVICES[k]['title'], SERVICES[k]['short']) for k in COMPLEMENT)
    body += f'<section class="on-deep glow" id="services"><div class="wrap">{sec_head("الخدمات", f"كل ما تحتاجه مناسبتك في {ar} — <em>من طاقم واحد</em>", f"قهوجيون وصبّابون ومباشرون، ومعهم كل ما يكمّل الضيافة: سقّاة زمزم، سفرجية، كاونترات وخيام وبوفيهات — طاقم واحد يصل إلى مناسبتك في {ar} بعدّته كاملة.")}<div class="svcs">{grid}</div>{foot("services.html", "كل الخدمات")}</div></section>'
    # 5) كيف يعمل الطاقم — المحتوى المحلي المكتوب (3 أدوار) في قسم واحد (D75) → واتساب
    def row(i, sec):   # D96: العنصر الرابع/الخامس اختياريان (رابط + نصّه) — صفحات المدن تربط كل دور بصفحة خدمته
        kick = sec[2] if len(sec) > 2 and is_city else s['kicker']
        lnk = f'<a class="btn btn-glass btn-sm" href="{sec[3]}">{sec[4]}</a>' if len(sec) > 4 else ''
        r = roles[i % len(roles)]
        return f'<div class="split{" rev" if i % 2 else ""}"><div class="rv"><span class="kick">{kick}</span><h2>{sec[0]}</h2><p>{sec[1]}</p>{lnk}</div>{lfig(r[0], f"{r[1]} — {ar}", r[1], r[2], g)}</div>'
    rows = ''.join(row(i, sec) for i, sec in enumerate(rec['sections']))
    rh = (f"خدماتنا في <em>{ar}</em> — عن قرب", f"ثلاث خدمات محلية بطاقم واحد — اختر ما يناسب مناسبتك في {ar} أو اجمعها.") if is_city else (f"ماذا يفعل طاقمنا في مناسبتك <em>في {ar}</em>؟", "أدوار واضحة يعرفها أهل الضيافة في السعودية — ونوزّعها على عدد ضيوفك.")
    body += f'<section class="lsec on-rich roles" id="roles"><div class="wrap">{sec_head("خدماتنا" if is_city else "كيف نعمل", *rh)}{rows}<div class="works-foot rv">{wa(rec["wa"], "btn btn-wa", "اسأل عن التفاصيل", "wa_sec")}</div></div></section>'
    # 6) الطاقم والزي — القسم نفسه من الرئيسية (5 صور صغيرة 3:4) → تفاصيل الزي في صفحة الخدمات
    st = _home_section('staff').replace('<h2 class="rv">اختر زيّ طاقمك</h2>', f'<h2 class="rv">اختر زيّ طاقمك في {ar}</h2>')
    body += st.replace('</div>\n</section>', foot('services.html#hosts', 'تفاصيل الزي والطاقم') + '</div>\n</section>')
    # 7) التقديمات والعدّة — 8 مربعات + 6 مقصوصات في قسم واحد (D75: أُدمج eq_strip) → كل التقديمات
    tiles = ''.join(re.findall(r'<figure class="tile".*?</figure>', _home_section('offerings'), flags=re.S)[:8])
    cut_figs = ''.join(f'<figure class="rv"><img src="img/cutouts/{f}.webp" alt="{esc(n)}" width="480" height="480" loading="lazy" decoding="async"><figcaption>{n}</figcaption></figure>' for f, n in CUTOUT_ITEMS)
    body += f'<section class="on-black grain" id="offerings"><div class="wrap">{sec_head("التقديمات والعدّة", f"ما الذي يصل إلى ضيوفك في <em>{ar}</em>؟", "تمور وقهوة وحلويات ومشروبات — والدلال والفناجين وأطقم التقديم تصل مع الطاقم.", hint=True)}<div class="strip rv">{tiles}<span class="edge"></span></div><div class="eq">{cut_figs}</div>{foot("offerings.html", "كل التقديمات والمعدات")}</div></section>'
    # 8) الترتيبات — ثلاث بطاقات، كل واحدة بزر واتساب (بلا أسعار — D68)
    if rec.get('packages'):   # D97: صفحات المدن/النيّة بلا ترتيبات
        pk = ''.join(f'<article class="rv"><h3>{n}</h3><p>{d}</p><ul class="feats">{"".join(f"<li>{f}</li>" for f in fs)}</ul>{wa(f"السلام عليكم، أرغب بالاستفسار عن «{n}» في {ar}:\nالتاريخ: \nالمكان: \nعدد الضيوف: ", "btn btn-gold btn-sm", "اطلب هذا الترتيب", "wa_pk")}</article>' for n, d, fs in rec['packages'])
        body += f'<section class="lsec on-rich glow" id="packages"><div class="wrap">{sec_head("الترتيبات", f"كيف نرتّب {s["ar"]} لمناسبتك في <em>{ar}</em>", "ثلاثة أشكال شائعة — والتشكيل يُحسب على عدد ضيوفك وشكل المكان.")}<div class="pk">{pk}</div></div></section>'
    # 9) لماذا نحن → من نحن
    body += f'<section class="lsec on-deep" id="why"><div class="wrap">{sec_head("لماذا نحن", f"لماذا يختارنا أهل <em>{ar}</em>؟")}<ul class="why">{"".join(f"<li class=\"rv\">{w}</li>" for w in rec["why"])}</ul>{foot("about.html", "تعرّف علينا أكثر")}</div></section>'
    # 10) الأسئلة الشائعة
    body += faq_block(rec['faqs'], f'أسئلة شائعة عن الضيافة في {ar}' if is_city else f'أسئلة شائعة عن {s["ar"]} في {ar}')
    # 11) التغطية → صفحة المدينة
    body += dist_block(f'نصل إلى كل أحياء {ar}', rec['districts'])   # D88: بلا زر «كل خدماتنا في جدة» — هذه هي صفحة جدة الكاملة
    # 12) احجز
    body += contact_block(f'مناسبتك في <em>{ar}</em>' if is_city else f'احجز {s["ar"]} <em>في {ar}</em>', 'أرسل التاريخ والمكان وعدد الضيوف — ونرتّب لك الطاقم والعدّة كاملة.', rec['wa'])
    # 13) روابط
    rel = rec['other_cities'] + [{'label': 'كل المدن', 'href': 'locations.html'}] if rec['other_cities'] else rec['others']   # D97: الصفحة النيّة تربط خدمات مدينتها
    body += links_block('مدن <em>أخرى نخدمها</em>' if is_city else (f'{s["ar"]} في <em>مدن أخرى</em>' if rec['other_cities'] else f'خدمات أخرى في <em>{ar}</em>'), rel, 'rel')   # D89: أُبقي كسطر واحد للمدن فقط (ترابط داخلي للفهرسة)؛ روابط «خدمات جدة الأخرى» حُذفت — موجودة في بطاقات الخدمات أعلاه
    # 14) تابعنا — صف الأيقونات في الأخير (Q5)
    body += social_row(rec['wa'])
    return shell(cur, rec['title'], rec['desc'], [], body, extra_css=LOCAL_CSS + MASTER_CSS, extra_js=MASTER_JS, hero_img=hero, section='locations.html')

MASTER_JS = '''<script>
(function(){
  var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  // D84: خلفية الهيرو المتغيّرة — تبدأ بعد أول رسم، وتتوقف عند الخروج من الشاشة
  var hero=document.querySelector('.hero-anim'), sl=hero?[].slice.call(hero.querySelectorAll('.slides img')):[];
  if(hero&&sl.length&&!reduce){
    var i=-1, vis=true, t;
    function step(){ if(!vis) return; if(i>=0) sl[i].classList.remove('on'); i=(i+1)%sl.length; sl[i].classList.add('on'); hero.classList.add('away'); }
    function loop(){ step(); t=setTimeout(loop,7000); }
    var start=function(){ sl.forEach(function(im){im.loading='eager';}); setTimeout(loop,2600); };
    (window.requestIdleCallback?requestIdleCallback(start,{timeout:2500}):setTimeout(start,1200));
    if('IntersectionObserver' in window) new IntersectionObserver(function(es){es.forEach(function(e){vis=e.isIntersecting; if(vis&&!t){loop();} if(!vis){clearTimeout(t);t=null;}});},{threshold:.05}).observe(hero);
  }
  // D85: شركاء النجاح — ينبثقون للأسفل في الصفحة نفسها
  var pl=document.getElementById('plogos'), pb=document.getElementById('plogosMore');
  if(pl&&pb) pb.addEventListener('click',function(){ var open=!pl.classList.toggle('collapsed'); pb.setAttribute('aria-expanded',String(open)); if(open){pb.textContent='إظهار أقل';} else {pb.textContent=pb.dataset.all; pl.scrollIntoView({block:'nearest',behavior:reduce?'auto':'smooth'});} });
  if(pb) pb.dataset.all=pb.textContent;
})();
</script>'''

# D95 (v6.8): النموذج معمَّم على 24 صفحة خدمة×مدينة (كان qahwajiin-jeddah فقط — D63)؛ D96/D97: وصفحات المدن الثماني والصفحة النيّة كذلك → 33 صفحة محلية بلغة واحدة.

def build_local_all():
    out = {'locations.html': build_locations(), 'social.html': build_social(), 'legal.html': build_legal(), 'mubashirin-qahwa-jeddah.html': master_page(dict(intent_content(), kind='intent'))}   # D97
    for c in CITIES: out[city_page(c['slug'])] = build_city(c['slug'])   # D96
    for s in LOCAL_SERVICES:
        for c in CITIES:
            out[page_of(s['slug'], c['slug'])] = master_page(local_content(s['slug'], c['slug']))   # D95
    return out


if __name__ == '__main__':
    out = {'services.html':build_services(),'offerings.html':build_offerings(),'portfolio.html':build_portfolio(),'about.html':build_about(),'contact.html':build_contact()}
    out.update(build_local_all())   # v6.3: 36 صفحة محلية (D55–D62)
    for k, v in out.items():
        open(os.path.join(ROOT, k), 'w', encoding='utf-8').write(v); print(k, len(v)//1024, 'KB')
