# -*- coding: utf-8 -*-
"""مولّد صفحات مراجعة الصور المرقّمة (طلب المالك 2026-09-04):
يقرأ الصفحات المولّدة (index + 5) ويستخرج كل <img> بترتيب ظهورها، ويرقّمها لكل صفحة
(«أعمالنا رقم 12») مع المسمّى الحالي (العنوان + السطر الفرعي أو alt) واسم الملف،
ثم يكتب review/index.html (فهرس) + review/<page>.html لكل صفحة + review/list.md.
v2 (طلب المالك): بلا تكرار (تجزئة بصرية dHash 16×16 عبر كل الصفحات؛ أولوية الصفحات الفرعية ثم الرئيسية)،
صور مصغّرة منخفضة الدقة review/t/*.webp (≤400px q60) لتفتح على الجوال، صورتان في الصف، الرقم تحت الصورة.
الاستخدام: cd prototype-home/build && python3 review.py
لا يمسّ أي ملف من ملفات الموقع. الصور تُعرض من ../img/…
"""
import os, re, html
from html.parser import HTMLParser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'review')
PAGES = [('index', 'الرئيسية'), ('services', 'الخدمات'), ('offerings', 'التقديمات والمعدات'),
         ('portfolio', 'أعمالنا'), ('about', 'من نحن'), ('contact', 'تواصل معنا')]
SEC_AR = {'hero': 'غلاف الصفحة', 'who': 'لمن نعمل', 'works': 'من أعمالنا', 'partners': 'شركاء النجاح', 'staff': 'الطاقم والزي',
          'offerings': 'التقديمات', 'services': 'الخدمات', 'faq': 'الأسئلة الشائعة', 'contact': 'تواصل',
          'g-male': 'الطاقم الرجالي', 'g-female': 'الطاقم النسائي', 'g-heritage': 'تراث وفنون', 'g-setup': 'أركان وتجهيز',
          'hot': 'المشروبات الحارة', 'cold': 'المشروبات الباردة', 'dates': 'التمور', 'sweets': 'الحلويات', 'pastry': 'المعجنات',
          'snacks': 'السناكات', 'sandwiches': 'الساندويتشات', 'fruits': 'الفواكه', 'nuts': 'المكسرات', 'equipment': 'المعدات',
          'distributions': 'التوزيعات', 'gallery': 'معرض الأعمال', 'story': 'قصتنا', 'values': 'قيمنا', 'trust': 'الثقة والاعتمادات', 'cities': 'المدن'}
SKIP_SRC = ('logo-emblem', '-crop.svg')
ORDER = ['services', 'offerings', 'portfolio', 'about', 'contact', 'index']  # أولوية إزالة التكرار
TH_W, TH_Q = 400, 60

class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.items = []; s.sec = 'hero'; s.h = ''; s.hcap = None; s.tagtxt = None; s.tag = ''
        s.fig_tag = None
    def handle_starttag(s, t, attrs):
        a = dict(attrs)
        if t == 'section' and a.get('id'): s.sec = a['id']; s.h = ''
        if t in ('h2', 'h3'): s.hcap = t; s.h = ''
        if t == 'span' and a.get('class') == 'tag': s.tagtxt = ''
        if t == 'img':
            src = a.get('src', '')
            if not src or src.startswith("'") or any(k in src for k in SKIP_SRC) or a.get('id') == 'lbImg': return
            s.items.append({'sec': s.sec, 'h': s.h, 'src': src, 'alt': a.get('alt', ''), 'cap': a.get('data-cap', ''),
                            'sub': a.get('data-sub', ''), 'tag': None})
    def handle_data(s, d):
        if s.hcap: s.h = (s.h + d).strip() if s.h else d.strip()
        if s.tagtxt is not None: s.tagtxt += d
    def handle_endtag(s, t):
        if t in ('h2', 'h3'): s.hcap = None
        if t == 'span' and s.tagtxt is not None:
            if s.items and s.items[-1]['tag'] is None: s.items[-1]['tag'] = s.tagtxt.strip()
            s.tagtxt = None
    def handle_startendtag(s, t, attrs): s.handle_starttag(t, attrs)

def sec_label(it):
    base = SEC_AR.get(it['sec'], it['sec'])
    if it['sec'] in ('g-male', 'g-female', 'g-heritage', 'g-setup') and it['h'] and it['h'] != base: return f"{base} › {it['h']}"
    if it['src'].endswith('-crop.svg'): return 'شارات الاعتماد (سجل تجاري / زكاة / مركز أعمال)'
    return base

def label(it):
    if it['cap']: return it['cap'], it['sub']
    return it['alt'], ''

CSS = """*{box-sizing:border-box}body{margin:0;font-family:'Segoe UI',Tahoma,Arial,sans-serif;background:#f6f1e8;color:#1b1b1b;line-height:1.6}
a{color:#7a5a1e}.top{position:sticky;top:0;background:#0d0d0d;color:#f3e6c8;padding:10px 16px;display:flex;gap:14px;align-items:center;flex-wrap:wrap;z-index:2}
.top a{color:#e5c46a;text-decoration:none;font-weight:700}.top .cur{color:#fff;border-bottom:2px solid #e5c46a}.wrap{max-width:1200px;margin:0 auto;padding:16px}
h1{font-size:1.5rem;margin:8px 0 4px}.hint{background:#fff7e0;border:1px solid #e5c46a;border-radius:10px;padding:10px 14px;margin:10px 0 18px;font-size:.95rem}
h2{margin:28px 0 10px;padding-bottom:6px;border-bottom:2px solid #c9a84c;font-size:1.2rem}h2 small{color:#666;font-weight:400;font-size:.85rem}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}@media (min-width:900px){.grid{grid-template-columns:repeat(3,1fr)}}
.card{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.08);position:relative;display:flex;flex-direction:column}
.card img{width:100%;aspect-ratio:3/4;object-fit:cover;display:block;background:#eee}.card.wide img{aspect-ratio:16/9;object-fit:contain;background:#222}
.num{display:block;background:#0d0d0d;color:#e5c46a;font-weight:900;font-size:1.6rem;text-align:center;padding:4px 0;font-family:Tahoma,sans-serif;letter-spacing:.5px}
.card figcaption{padding:8px 10px 10px;font-size:.9rem}.card b{display:block;font-size:.95rem}.card small{display:block;color:#555}
.card .file{display:block;color:#999;font-size:.72rem;direction:ltr;text-align:right;font-family:monospace;margin-top:4px;word-break:break-all}
.card .t{display:inline-block;background:#f0e6cf;color:#7a5a1e;border-radius:6px;padding:0 6px;font-size:.72rem;margin-top:4px}
.idx{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}.idx a{display:block;background:#fff;border-radius:12px;padding:16px;text-decoration:none;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.idx a b{display:block;font-size:1.15rem;color:#1b1b1b}.idx a span{color:#666}
@media print{.top{position:static}.card{break-inside:avoid}}"""

def nav(cur):
    links = ['<a href="index.html"%s>الفهرس</a>' % (' class="cur"' if cur == 'hub' else '')]
    for k, ar in PAGES: links.append('<a href="%s.html"%s>%s</a>' % (k, ' class="cur"' if cur == k else '', ar))
    return '<div class="top">' + ' · '.join(links) + '</div>'

def page_html(k, ar, items):
    groups = []
    for it in items:
        L = sec_label(it)
        if not groups or groups[-1][0] != L: groups.append((L, []))
        groups[-1][1].append(it)
    out = [f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>مراجعة الصور — {ar}</title><style>{CSS}</style></head><body>{nav(k)}<div class="wrap">',
           f'<h1>{ar} — {len(items)} صورة</h1>',
           f'<div class="hint">للتسجيل الصوتي: قل «<b>{ar}</b> رقم <b>N</b>: [المسمّى الصحيح]». الرقم أسفل كل صورة هو رقمها في هذه الصفحة، وتحته المسمّى الحالي كما في الموقع. الصور بدقة مخفّضة للسرعة؛ كل صورة تظهر مرة واحدة فقط في كل صفحات المراجعة.</div>']
    for L, its in groups:
        out.append(f'<h2>{html.escape(L)} <small>({its[0]["n"]}–{its[-1]["n"]})</small></h2><div class="grid">')
        for it in its:
            cap, sub = label(it)
            wide = ' wide' if it['sec'] in ('partners', 'trust') or 'ab-team' in it['src'] else ''
            tag = f'<span class="t">{html.escape(it["tag"])}</span>' if it.get('tag') else ''
            out.append(f'<figure class="card{wide}"><img src="t/{html.escape(it["t"])}" alt="" loading="lazy" decoding="async"><span class="num">{it["n"]}</span><figcaption><b>{html.escape(cap)}</b>'
                       f'{("<small>" + html.escape(sub) + "</small>") if sub else ""}{tag}<span class="file">{html.escape(os.path.basename(it["src"]))}</span></figcaption></figure>')
        out.append('</div>')
    out.append('</div></body></html>')
    return '\n'.join(out)

def dhash(path, sz=16):
    from PIL import Image
    im = Image.open(path).convert('L').resize((sz + 1, sz), Image.LANCZOS); px = list(im.getdata())
    return ''.join('1' if px[r * (sz + 1) + c] > px[r * (sz + 1) + c + 1] else '0' for r in range(sz) for c in range(sz))

def thumb(src):
    from PIL import Image
    os.makedirs(os.path.join(OUT, 't'), exist_ok=True)
    name = os.path.splitext(os.path.basename(src))[0] + '.webp'
    dst = os.path.join(OUT, 't', name)
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(os.path.join(ROOT, src)):
        im = Image.open(os.path.join(ROOT, src)).convert('RGB')
        if im.width > TH_W: im = im.resize((TH_W, round(im.height * TH_W / im.width)), Image.LANCZOS)
        im.save(dst, 'WEBP', quality=TH_Q, method=6)
    return name

def main():
    os.makedirs(OUT, exist_ok=True)
    parsed = {}
    for k, _ in PAGES:
        p = P(); p.feed(open(os.path.join(ROOT, k + '.html'), encoding='utf-8').read()); parsed[k] = p.items
    # إزالة التكرار: نفس الملف أو نفس الصورة بصرياً (dHash ≤ 8) — أول ظهور بحسب ORDER يبقى
    seen, dups = [], []   # seen: list of (hash, page, n)
    for k in ORDER:
        keep = []
        for it in parsed[k]:
            h = dhash(os.path.join(ROOT, it['src']))
            hit = next((s for s in seen if sum(a != b for a, b in zip(h, s[0])) <= 8), None)
            if hit: dups.append((k, it['src'], hit[1], hit[2])); continue
            keep.append(it); seen.append((h, k, len(keep)))
        parsed[k] = keep
    summary, md = [], ['# قائمة صور الموقع المرقّمة (المسمّى الحالي) — بلا تكرار\n']
    for k, ar in PAGES:
        items = parsed[k]
        for i, it in enumerate(items, 1): it['n'] = i; it['t'] = thumb(it['src'])
        open(os.path.join(OUT, k + '.html'), 'w', encoding='utf-8').write(page_html(k, ar, items))
        summary.append((k, ar, len(items)))
        md.append(f'\n## {ar} ({len(items)})\n')
        last = None
        for it in items:
            L = sec_label(it)
            if L != last: md.append(f'\n### {L}\n'); last = L
            cap, sub = label(it)
            md.append(f'- **{it["n"]}** — {cap}{(" · " + sub) if sub else ""} `{os.path.basename(it["src"])}`')
    total = sum(n for _, _, n in summary)
    hub = [f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>مراجعة صور الموقع — كيف الضيافة</title><style>{CSS}</style></head><body>{nav("hub")}<div class="wrap">',
           f'<h1>مراجعة صور الموقع — {total} صورة في 6 صفحات</h1>',
           f'<div class="hint">طريقة التسجيل: افتح الصفحة، وسجّل صوتياً: «<b>اسم الصفحة</b> — رقم <b>1</b>: كذا، رقم <b>2</b>: كذا…». إن كانت الصورة صحيحة قل «صح». إن كانت لا تُستخدم قل «احذف». أي صورة فيها اسم/شعار جهة حكومية اذكرها.<br>كل صورة تظهر <b>مرة واحدة</b> فقط (استُبعد {len(dups)} تكراراً؛ الصورة المكرّرة في الرئيسية تظهر في صفحتها الأصلية).</div><div class="idx">']
    for k, ar, n in summary: hub.append(f'<a href="{k}.html"><b>{ar}</b><span>{n} صورة</span></a>')
    hub.append('</div></div></body></html>')
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write('\n'.join(hub))
    md.append('\n## التكرارات المستبعدة (%d)\n' % len(dups))
    for k, src, k2, n in dups: md.append(f'- {k}: `{os.path.basename(src)}` = {dict(PAGES)[k2]} رقم {n}')
    open(os.path.join(OUT, 'list.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print('dups removed', len(dups))
    for k, ar, n in summary: print(f'{k:10s} {ar:22s} {n}')
    print('total', total)

if __name__ == '__main__': main()
