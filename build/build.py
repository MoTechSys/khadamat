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
def sz(name):
    w, h = SIZES.get(name) or _probe(name); return f'width="{w}" height="{h}"'
def _probe(name):
    from PIL import Image
    return Image.open(os.path.join(ROOT, 'img', 'photos', name + '.webp')).size

def cut(s, a, b):
    i = s.index(a); j = s.index(b, i) + len(b); return s[i:j]
CSS = cut(IDX, '<style>', '</style>')
FONTS = cut(IDX, '<link rel="preconnect" href="https://fonts.googleapis.com">', '</noscript>')
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
STAMP = 'v6 · 2026-09-03'

def wa(text, cls='btn btn-wa', label='تواصل عبر واتساب', ev='wa'):
    return f'<a class="{cls}" href="https://wa.me/{WA_NUM}?text={U.quote(text)}" target="_blank" rel="noopener" data-ev="{ev}">{WA_SVG}{label}</a>'
def esc(s): return html.escape(s, quote=True)

PAGES = [('index.html','الرئيسية'),('services.html','الخدمات'),('offerings.html','التقديمات'),('portfolio.html','أعمالنا'),('about.html','من نحن'),('contact.html','تواصل')]

def header(cur):
    h = HEADER.replace('href="#top" title="الرئيسية"', 'href="index.html" title="الرئيسية"')
    links = ''.join(f'<a class="nav-link" href="{p}"{" aria-current=\"page\"" if p==cur else ""}>{t}</a>' for p, t in PAGES if p != 'index.html')
    h = re.sub(r'(<a class="nav-link"[^>]*>[^<]*</a>\s*)+', links, h, count=1)
    return h

def drawer(cur, sections):
    li = ''.join(f'<li><a href="#{i}"><span>{t}{f"<small>{s}</small>" if s else ""}</span>{ARROW}</a></li>' for i, t, s in sections)
    pg = ''.join(f'<li><a href="{p}"{" aria-current=\"page\"" if p==cur else ""}><span>{t}</span>{ARROW}</a></li>' for p, t in PAGES if p != cur)
    return f'''<div class="scrim" id="scrim" aria-hidden="true"></div>
<aside class="drawer" id="drawer" aria-label="قائمة الصفحة" aria-hidden="true">
  <div class="d-top">
    <span class="brand"><img src="img/logo-emblem.webp" alt="" width="226" height="271"><span class="word"><b>كيف الضيافة</b><small>SINCE 2016</small></span></span>
    <button class="close" id="drawerClose" aria-label="إغلاق القائمة">×</button>
  </div>
  <ul>
    <li class="d-sep">في هذه الصفحة</li>{li}
    <li class="d-sep">الصفحات</li>{pg}
  </ul>
  <div class="d-foot">
    {wa('السلام عليكم، أرغب بالاستفسار عن خدمات كيف الضيافة لمناسبة', 'btn btn-gold btn-block', 'تواصل عبر واتساب', 'wa_drawer')}
    <a class="tel" href="tel:+966508252134">اتصال مباشر <b>{WA_DISPLAY}</b></a>
    <span class="since">Keif Al-Diafa · Luxury Hospitality</span>
  </div>
</aside>'''

PAGE_CSS = '''
/* ===== v6 — الصفحات الداخلية ===== */
.phero{position:relative;min-height:46svh;display:flex;align-items:flex-end;overflow:hidden;background:var(--rich);padding:0}
.phero img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center 30%}
.phero::before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(13,13,13,.35),rgba(13,13,13,.55) 45%,var(--rich) 100%)}
.phero .wrap{position:relative;z-index:1;padding-block:28px 26px;text-align:center}
.phero .label{display:inline-flex;align-items:center;gap:12px;font-size:.74rem;letter-spacing:.3em;color:var(--gold);margin-bottom:8px}
.phero .label::before,.phero .label::after{content:"✦";font-size:.7rem;letter-spacing:0}
.phero h1{font-size:clamp(1.7rem,6vw,2.7rem);color:var(--cream);text-wrap:balance;line-height:1.35}
.phero h1 em{font-style:normal;background:var(--grad-gold);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
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
.grp{padding-block:40px}
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
.item img{width:100%;aspect-ratio:1;object-fit:cover}
.item img[data-pos]{object-position:var(--pos)}
#hot .item img{object-position:50% 78%}
.item figcaption{padding:9px 10px 11px}
.item b{display:block;font-family:var(--f-head);font-size:.95rem;color:var(--gold-hi);line-height:1.35}
.item small{display:block;color:var(--cream-3);font-size:.78rem;line-height:1.45;margin-top:2px}
.cat{padding-block:40px;scroll-margin-top:calc(var(--top) + 56px)}
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

def shell(cur, title, desc, sections, body, extra_css='', extra_js='', hero_img=None):
    pre = f'<link rel="preload" as="image" href="img/photos/{hero_img}.webp" fetchpriority="high">' if hero_img else ''
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
{header(cur)}

{drawer(cur, sections)}

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

def phero(label, h1, p, img, alt, ctas='', crumb=''):
    return f'''<section class="phero" aria-label="{esc(label)}">
  <img class="bg" src="img/photos/{img}.webp" alt="{esc(alt)}" {sz(img)} fetchpriority="high" decoding="async">
  <div class="wrap">
    <div class="crumb"><a href="index.html">الرئيسية</a><span>›</span><span>{crumb or label}</span></div>
    <span class="label">{label}</span>
    <h1>{h1}</h1>
    <p>{p}</p>
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
        body += f'''<section class="grp {'on-rich' if gi%2==0 else 'on-deep'}" id="g-{g['key']}"><div class="wrap"><div class="sec-head"><span class="label rv">{g['hint']}</span><h2 class="rv">{g['label']}</h2></div>{cards}</div></section>'''
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
    body = phero('التقديمات والمعدات', 'ما الذي يصل إلى <em>ضيوفك؟</em>', 'قهوة سعودية وشاي، مشروبات باردة، تمور محشية، حلويات ومعجنات، سناكات وسندوتشات وفواكه ومكسرات — ودلال وفناجين تليق بها. اختر ما تريد ونرتّبه لك.', 'o-dallah', 'دلة ذهبية وتمور على طاولة تقديم',
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
        body += f'''<section class="cat {'on-rich' if ci%2==0 else 'on-deep'}" id="{c['id']}"><div class="wrap"><div class="sec-head"><span class="label rv">{len(items)} أصناف</span><h2 class="rv">{c['label']}</h2><p class="rv">{c['desc']}</p></div>{extra}{grid(c['id'], items)}
<div class="cta-row rv">{wa(f"السلام عليكم، أرغب بإضافة «{c['label']}» لتقديمات مناسبة:\nالمدينة: \nالتاريخ: \nعدد الضيوف: ", 'btn btn-glass btn-sm', f'اطلب {c["label"]}', f'wa_off_{c["id"]}')}</div></div></section>'''
    # المعدات
    eq = [(k, equipment_caption(MAN['map'][k]), 'ضمن الحزمة أو بحسب الطلب') for k in sorted((k for k in SIZES if k.startswith('of-equipment-')), key=lambda x:int(x.split('-')[-1]))]
    body += f'''<section class="cat on-rich" id="equipment"><div class="wrap"><div class="sec-head"><span class="label rv">{len(eq)} قطعة</span><h2 class="rv">معدات التقديم</h2><p class="rv">دلال ذهبية وفضية، فناجين وكاسات، استاندات وصواني — كلها من مخزوننا وتصل مع الطاقم.</p></div>{grid('equipment', eq)}
<div class="cta-row rv">{wa('السلام عليكم، أرغب بالاستفسار عن معدات التقديم (دلال، فناجين، استاندات) لمناسبة:\nالمدينة: \nالتاريخ: ', 'btn btn-glass btn-sm', 'اسأل عن المعدات', 'wa_off_equipment')}</div></div></section>'''
    di = [(f'of-distributions-{i}', DIST_CAPS[i-1], 'تغليف فاخر · إمكانية طباعة الشعار') for i in range(1,6)]
    body += f'''<section class="cat on-deep" id="distributions"><div class="wrap"><div class="sec-head"><span class="label rv">هدايا الضيوف</span><h2 class="rv">التوزيعات</h2><p class="rv">صواني توزيعات VIP — تمر وحلا وقهوة — بتغليف فاخر يمكن طباعة شعار الجهة عليه.</p></div>{grid('distributions', di)}
<div class="cta-row rv">{wa('السلام عليكم، أرغب بعرض سعر لتوزيعات VIP لمناسبة:\nالمدينة: \nالتاريخ: \nالعدد: ', 'btn btn-glass btn-sm', 'اطلب توزيعات', 'wa_off_distributions')}</div></div></section>'''
    body += faq_block(FAQ_OFFERINGS, 'عن التقديمات والمعدات')
    body += contact_block('أرسل قائمتك <em>ونعود إليك بعرض</em>', 'اختر الأصناف، وأخبرنا بالمدينة والتاريخ وعدد الضيوف.', 'السلام عليكم، أرغب بعرض سعر لتقديمات ضيافة:\nالمدينة: \nالتاريخ: \nعدد الضيوف: \nالأصناف: ')
    secs = [(c['id'], c['label'], '') for c in cats] + [('equipment','معدات التقديم',''),('distributions','التوزيعات',''),('contact','تواصل','')]
    return shell('offerings.html', 'التقديمات والمعدات', 'تقديمات كيف الضيافة: مشروبات حارة وباردة، تمور فاخرة، حلويات، معجنات، سناكات، سندوتشات، فواكه، مكسرات، معدات تقديم وتوزيعات VIP.', secs, body, hero_img='o-dallah')

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
<section class="cities on-black" id="cities" aria-label="المدن التي نخدمها"><div class="wrap rv"><span class="lbl">نصل إليكم في:</span>{''.join(f'<a{" class=\"main\"" if c=="جدة" else ""} href="https://wa.me/{WA_NUM}?text={U.quote(f"السلام عليكم، أرغب بالاستفسار عن خدمات كيف الضيافة لمناسبة في {c}")}" target="_blank" rel="noopener" data-ev="wa_city">{c}</a>' for c in cities)}<span class="lbl" style="margin-inline-start:6px">وجميع مناطق المملكة</span></div></section>'''
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

if __name__ == '__main__':
    out = {'services.html':build_services(),'offerings.html':build_offerings(),'portfolio.html':build_portfolio(),'about.html':build_about(),'contact.html':build_contact()}
    for k, v in out.items():
        open(os.path.join(ROOT, k), 'w', encoding='utf-8').write(v); print(k, len(v)//1024, 'KB')
