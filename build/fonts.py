#!/usr/bin/env python3
"""
v6.1 — خطوط مستضافة محليًا بدل Google Fonts (تشخيص Lighthouse: إعادة التخطيط بعد وصول
الخطوط كانت أكبر مسبّب للـTBT/LCP على الصفحات الفرعية).

المصدر: ملفات woff2 الرسمية من fonts.gstatic.com (نفس ما يقدّمه Google Fonts) →
تقليص (subset) بـfontTools إلى المحارف التي يستعملها الموقع فعليًا:
  - العربية الأساسية U+0621–0652 + أرقام عربية/هندية + علامات ترقيم عربية
  - ASCII الأساسي (أرقام/لاتيني داخل العناوين مثل VIP)
  - علامات الطباعة المستعملة: – — « » × ✕ ✦ …
مع الإبقاء على كل ميزات OpenType (--layout-features='*') حتى تبقى الوصلات/التشكيل سليمة.

المخرجات (prototype-home/fonts/):
  amiri-700.woff2      Amiri Bold      (العناوين)        ≈ 43 KB  (كان 100 KB عربي + 20 KB لاتيني)
  noto-naskh.woff2     Noto Naskh Arabic متغيّر 400–700 (النص)  ≈ 22 KB  (كان 94 KB + 20 KB)
  marcellus.woff2      Marcellus       (اللاتيني الزخرفي) ≈ 14 KB  (كما هو)

التشغيل:  cd prototype-home/build && python3 fonts.py [--force]
يحتاج: pip install fonttools brotli
"""
import os, sys, urllib.request, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'fonts'); CACHE = os.path.join('/tmp', 'fonts-src')

# روابط gstatic كما وردت في css2 (2026-09-04). لو تغيّرت النسخة يُحدَّث الرابط فقط.
SRC = {
    'amiri-700':  'https://fonts.gstatic.com/s/amiri/v30/J7acnpd8CGxBHp2VkaY6zp5yGw.woff2',
    'noto-naskh': 'https://fonts.gstatic.com/s/notonaskharabic/v44/RrQKbpV-9Dd1b1OAGA6M9PkyDuVBeN2DHV20Lg.woff2',
    'marcellus':  'https://fonts.gstatic.com/s/marcellus/v13/wEO_EBrOk8hQLDvIAF81VvoK.woff2',
}
UNICODES = ','.join([
    'U+0020-007E', 'U+00A0', 'U+00AB', 'U+00BB', 'U+00D7',          # ASCII + NBSP + « » ×
    'U+060C', 'U+061B', 'U+061F', 'U+0621-0652', 'U+0660-066F',     # عربي أساسي + تشكيل + أرقام هندية
    'U+0670', 'U+06CC', 'U+06D4',
    'U+200C-200F', 'U+2010-2011', 'U+2013-2014', 'U+2018-2019', 'U+201C-201D', 'U+2026',
    'U+2715', 'U+2726',                                             # ✕ ✦
])

def fetch(name):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, name + '.src.woff2')
    if not os.path.exists(p):
        urllib.request.urlretrieve(SRC[name], p)
    return p

def subset(name, force=False):
    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, name + '.woff2')
    if os.path.exists(dst) and not force: return dst
    src = fetch(name)
    subprocess.run([sys.executable, '-m', 'fontTools.subset', src, '--flavor=woff2', f'--unicodes={UNICODES}',
                    '--layout-features=*', '--no-hinting', f'--output-file={dst}'], check=True)
    return dst

if __name__ == '__main__':
    force = '--force' in sys.argv
    for n in SRC:
        p = subset(n, force); print(f'{n:12s} {os.path.getsize(p)//1024:4d} KB  → {os.path.relpath(p, ROOT)}')
