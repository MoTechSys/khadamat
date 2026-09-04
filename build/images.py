#!/usr/bin/env python3
"""
image pipeline — prototype v6
مصدر: keif-aldiafa-web/public/images  →  prototype-home/img/photos/<name>.webp (≤640px, q76)
                                        →  prototype-home/img/full/<name>.webp   (≤1600px, q82)
القرارات:
- استُبعدت كل صورة بحكم GOV/CAUTION في photo-vetting.json (لا جهة حكومية بلا موافقة كتابية).
- البانرات التسويقية (نص على الصورة) لا تدخل المعارض (souqiya-1, safarjia-main-bg, female-7, safarjia-1/2, safarjia-f-1/2).
- الصورة الصغيرة weddings/arab-wedding-hall-men-section (271×300) مستبعدة لضعف الدقة.
"""
import json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(os.path.dirname(ROOT), 'keif-aldiafa-web', 'public', 'images')
THUMB = os.path.join(ROOT, 'img', 'photos'); FULL = os.path.join(ROOT, 'img', 'full')

# name → source (relative to SRC)
M = {}
def add(prefix, items):
    for k, v in items.items(): M[f'{prefix}-{k}'] = v

# ===== الخدمات =====
add('sv-hosts', {'1':'services/male/hosts/dagla/dagla-1.webp','2':'services/male/hosts/dagla/dagla-5.webp','3':'services/male/hosts/dagla/dagla-6.webp','4':'services/male/hosts/dagla/dagla-3.webp'})
add('sv-hizam', {'1':'services/male/hosts/hizam/hizam-1.webp','2':'services/male/hosts/hizam/hizam-2.webp'})
add('sv-dagla', {'1':'services/male/hosts/dagla/dagla-1.webp','2':'services/male/hosts/dagla/dagla-2.webp','3':'services/male/hosts/dagla/dagla-5.webp','4':'services/male/hosts/dagla/dagla-6.webp'})
add('sv-janbiya', {'1':'services/male/hosts/dagla-janbiya/dagla-janbiya-1.webp','2':'services/male/hosts/dagla-janbiya/dagla-janbiya-2.webp'})
add('sv-sideriya', {'1':'services/male/hosts/sideriya/sideriya-1.webp','2':'services/male/hosts/sideriya/sideriya-2.webp','3':'services/male/hosts/sideriya/sideriya-3.webp'})
add('sv-makkawi', {'1':'services/male/hosts/makkawi/makkawi-1.webp','2':'services/male/hosts/makkawi/makkawi-2.webp'})
add('sv-zamzam', {str(i):f'services/male/souqiya/souqiya-{i}.webp' for i in range(2,9)})
add('sv-safarjia', {'1':'services/safarjia/safarji-1.webp','2':'services/safarjia/safarji-2.webp','3':'services/safarjia/safarji-3.webp','4':'services/safarjia/safarji-4.webp','5':'services/male/safarjia/safarjia-3.webp','6':'services/male/safarjia/safarjia-5.webp'})
add('sv-sawas', {'1':'services/sawas/sawas-main.webp','2':'services/sawas/sawas-style-1.webp','3':'services/sawas/sawas-style-2.webp','4':'services/sawas/sawas-style-3.webp','5':'services/sawas/sawas-style-4.webp'})
add('sv-hostess', {'1':'services/female-services/female-2.webp','2':'services/female-services/female-1.webp','3':'services/female-services/female-4.webp','4':'services/female-services/female-6.webp','5':'services/female/hostesses/hostess-2.webp','6':'services/female-services/female-main-bg.webp'})
add('sv-safarjiat', {'1':'services/female-services/female-5.webp','2':'services/female-services/female-3.webp','3':'services/female-services/female-8.webp'})
add('sv-clean', {'1':'services/female/cleaning/cleaning-f-1.webp'})
add('sv-callig', {'1':'services/artistic/artist/artist-2.webp','2':'services/artistic/artist/artist-5.webp','3':'services/artistic/artist/artist-4.webp','4':'services/artistic/artist/artist-3.webp'})
add('sv-artist', {'1':'services/artistic/artist/artist-9.webp','2':'services/artistic/artist/artist-8.webp','3':'services/artistic/artist/artist-6.webp','4':'services/artistic/artist/artist-7.webp'})
add('sv-folk', {'1':'services/artistic/folkband/folkband-1.webp','2':'services/artistic/folkband/folkband-2.webp'})
add('sv-tent', {'1':'services/artistic/heritage-tent/tent-1.webp','2':'services/artistic/heritage-tent/tent-2.webp','3':'services/artistic/heritage-tent/tent-4.webp','4':'keif/khaima-turathiya-jeddah-diyafa-tent-keif-aldiafa.webp'})
add('sv-counter', {'1':'services/artistic/counter/counter-1.webp','2':'keif/qahwa-counter-jeddah-gold-station-keif-aldiafa.webp','3':'services/artistic/counter/counter-2.webp'})
add('sv-booth', {'1':'services/artistic/photo-booth/photo-booth-5.webp','2':'services/artistic/photo-booth/photo-booth-4.webp','3':'services/artistic/photo-booth/photo-booth-6.webp','4':'services/artistic/photo-booth/photo-booth-3.webp'})
add('sv-buffet', {'1':'services/artistic/buffet/buffet-1.webp','2':'services/artistic/buffet/buffet-2.webp','3':'services/artistic/buffet/buffet-3.webp','4':'keif/diyafa-pastry-tiers-jeddah-keif-aldiafa.webp'})
add('sv-table', {'1':'services/artistic/mobile-table/table-2.webp','2':'services/artistic/mobile-table/table-6.webp','3':'services/artistic/mobile-table/table-3.webp','4':'services/artistic/mobile-table/table-1.webp'})

# ===== التقديمات (من prod-data.json) =====
pd = json.load(open(os.path.join(ROOT,'build','prod-data.json'), encoding='utf-8'))
for c in pd['offerings']:
    for i, it in enumerate(c['items'], 1):
        M[f"of-{c['id']}-{i}"] = it['img'].lstrip('/').replace('images/','',1)
# المعدات (29) + التوزيعات (5)
if os.path.isdir(SRC):
    EQ = sorted(f for f in os.listdir(os.path.join(SRC,'equipment')) if f.endswith('.webp') and 'cutout' not in f)
    for i, f in enumerate(EQ, 1): M[f'of-equipment-{i}'] = f'equipment/{f}'
    DI = sorted(f for f in os.listdir(os.path.join(SRC,'distributions')) if f.endswith('.webp'))
    for i, f in enumerate(DI, 1): M[f'of-distributions-{i}'] = f'distributions/{f}'
else:
    # بلا مستودع الإنتاج (حساب جديد): نأخذ الخريطة المحفوظة في images-manifest.json حتى يبقى M كاملًا
    _man = json.load(open(os.path.join(ROOT,'build','images-manifest.json'), encoding='utf-8'))
    for k, v in _man['map'].items():
        if k.startswith(('of-equipment-','of-distributions-')): M[k] = v

# ===== المعرض (portfolio) — شركات (COMPANY) + رسمية بلا جهة (SAFE/FLAG) + زواجات =====
PF_GOV = ['events/formal-reception-indoor-event-saudi-hosts-luxury-catering.webp','events/gala-dinner-vip-reception-royal-protocol-marble-luxury.webp','events/saudi-event-vip-reception-luxury-catering-majlis-traditional-attire.webp','events/ksa-event-qahwa-service-hospitality-staff-arabic-coffee-ceremony.webp']
PF_CO = ['events/jeddah-event-marble-hall-osus-alinsha-vip-reception.webp','events/ksa-event-vip-reception-arabic-coffee-flyadeal-corporate.webp','events/vip-reception-luxury-catering-millennium-hotels-golden-dallah.webp','events/corporate-event-almana-medical-group-arabic-coffee-ceremony.webp','events/saudi-event-vip-reception-bolt-exhibition-qahwa-service.webp','events/royal-protocol-vip-reception-makkah-hotel-towers-majlis.webp','events/exhibition-saudi-event-nayifat-financing-ceremonial-coffee.webp','events/corporate-event-hospitality-staff-formal-reception-saudi-hosts.webp','events/luxury-catering-arabic-coffee-ceremony-gala-dinner-indoor.webp','events/majlis-qahwa-service-saudi-event-camel-decor.webp','events/indoor-event-luxury-catering-ceremonial-coffee-exhibition-reception.webp','events/outdoor-event-nahda-park-arabic-coffee-formal-reception.webp','events/saudi-event-formal-reception-makkah-themed-exhibition.webp','events/official-ceremony-grand-opening-saudi-hosts-red-backdrop.webp','events/conference-catering-saudi-electricity-company-dates-tray-luxury.webp','events/formal-reception-government-event-majad-booth-arabic-coffee.webp','events/conference-catering-hospitality-staff-medical-college-exhibition.webp','events/outdoor-event-tourism-booth-expo-saudi-host-coffee-set.webp','events/ksa-event-corporate-event-takween-al-watan-ceremonial-coffee.webp','events/ksa-event-luxury-catering-mcdc-conference-ceremonial-coffee.webp','events/corporate-event-dallah-hajj-transport-ceremonial-coffee.webp','events/indoor-event-saudi-hosts-bisht-qahwa-service-traditional.webp']
PF_WED = ['weddings/luxury-wedding-hall-male-hosts-dallah-gift-tray.webp','weddings/arab-wedding-male-host-qahwa-station-vip-wedding.webp','weddings/luxury-wedding-men-section-traditional-uniform-wedding-hall.webp','weddings/saudi-wedding-male-host-dallah-dates-qahwa-station.webp','weddings/qahwa-station-male-host-dallah-wedding-hall-ceremony.webp','weddings/saudi-wedding-traditional-uniform-male-hosts-white-thobe.webp','weddings/riyadh-wedding-vip-wedding-hall-male-host.webp','weddings/saudi-wedding-qahwa-station-dallah-white-thobe.webp','weddings/jeddah-wedding-men-section-traditional-uniform-luxury-wedding.webp','weddings/vip-wedding-traditional-uniform-dallah-wedding-hall.webp','weddings/wedding-coffee-male-host-dallah-tray-white-thobe.webp','weddings/saudi-wedding-male-host-arabic-coffee-luxury-wedding.webp']
PF_EQ = ['keif/qahwa-counter-jeddah-gold-station-keif-aldiafa.webp','keif/khaima-turathiya-jeddah-diyafa-tent-keif-aldiafa.webp','keif/diyafa-buffet-jeddah-dates-sweets-keif-aldiafa.webp','keif/nakhla-tamr-sukari-jeddah-display-keif-aldiafa.webp','keif/mabkhara-dallah-gold-jeddah-diyafa-keif-aldiafa.webp','keif/tawzeeat-jeddah-vip-dates-qahwa-tray-keif-aldiafa.webp','keif/qahwajiyeen-jeddah-hall-reception-keif-aldiafa.webp','keif/diyafa-canape-trays-jeddah-keif-aldiafa.webp']
for i,f in enumerate(PF_GOV,1): M[f'pf-gov-{i}']=f
for i,f in enumerate(PF_CO,1): M[f'pf-co-{i}']=f
for i,f in enumerate(PF_WED,1): M[f'pf-wed-{i}']=f
for i,f in enumerate(PF_EQ,1): M[f'pf-eq-{i}']=f
# من نحن
M['ab-team'] = 'keif/sabab-qahwa-jeddah-majlis-hall-keif-aldiafa.webp'
M['ab-hall'] = 'keif/qahwajiyeen-jeddah-hall-reception-keif-aldiafa.webp'

# ===== صور هيرو الصفحات الداخلية (v6.1) =====
# المصدر: img/full/<name>.webp (≤1600px، موجود في المستودع) → img/hero/<name>-m-<w>.webp (مربّع 1:1 للجوال)
#                                                            → img/hero/<name>-d-<w>.webp (شريط 3:1 للديسكتوب ≥900px)
# نقطة التركيز الرأسية 30% (تطابق object-position:center 30% في .phero img.bg). لا تكبير فوق المصدر أبدًا.
HERO = {'s-hosts': 's-hosts', 'pf-eq-3': 'pf-eq-3', 'p-gala': 'p-gala', 'ab-hall': 'ab-hall', 'p-reception': 'p-reception'}
HERO_DIR = os.path.join(ROOT, 'img', 'hero')
HERO_M_W = (480, 750, 1080)      # DPR 1 / 2 / 3 لعرض 390–412px
HERO_D_W = (1200, 1600)          # ديسكتوب 100vw
HERO_FOCUS_Y = 0.30
HERO_Q = 76   # v6.1: كالمصغّرات؛ pf-eq-3-m-750 نزل من 87→~70KB

def _crop(im, ratio, fy=HERO_FOCUS_Y):
    """قصّ إلى نسبة عرض/ارتفاع مع تركيز رأسي fy وتوسيط أفقي."""
    w, h = im.size
    if w / h > ratio:  # أعرض من المطلوب → قصّ الجانبين
        nw = round(h * ratio); x = (w - nw) // 2; return im.crop((x, 0, x + nw, h))
    nh = round(w / ratio); y = round((h - nh) * fy); return im.crop((0, y, w, y + nh))

def hero_variants(force=False):
    os.makedirs(HERO_DIR, exist_ok=True)
    out = {}
    for name in HERO:
        src = os.path.join(FULL, name + '.webp')
        if not os.path.exists(src): raise SystemExit(f'hero source missing: {src}')
        im = Image.open(src).convert('RGB')
        rec = {'m': [], 'd': []}
        for kind, ratio, widths in (('m', 1.0, HERO_M_W), ('d', 3.0, HERO_D_W)):
            c = _crop(im, ratio)
            ws = sorted({min(w, c.width) for w in widths})   # لا تكبير: يُسقَط ما يفوق المصدر ويُستبدل بعرض المصدر
            for w in ws:
                v = c.copy(); v.thumbnail((w, 100000))
                fn = f'{name}-{kind}-{v.width}.webp'; fp = os.path.join(HERO_DIR, fn)
                if force or not os.path.exists(fp): v.save(fp, 'WEBP', quality=HERO_Q, method=6)
                rec[kind].append([v.width, v.height, f'img/hero/{fn}'])
        out[name] = rec
    mp = os.path.join(ROOT, 'build', 'images-manifest.json')
    man = json.load(open(mp, encoding='utf-8')); man['heroes'] = out
    json.dump(man, open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return out

# ===== شعار الهيدر/الدرج/التذييل: نسخة صغيرة (يُعرض 35–40px عرضًا؛ 120px تكفي DPR3) =====
def logo_small(force=False):
    src = os.path.join(ROOT, 'img', 'logo-emblem.png')
    dst = os.path.join(ROOT, 'img', 'logo-emblem-120.webp')
    if force or not os.path.exists(dst):
        im = Image.open(src).convert('RGBA'); im.thumbnail((120, 144)); im.save(dst, 'WEBP', quality=90, method=6)
    return Image.open(dst).size

# حظر صارم: أي ملف بحكم GOV/CAUTION لا يمر
vet = json.load(open(os.path.join(ROOT,'build','photo-vetting.json'), encoding='utf-8'))
BAN = {i['file'] if '/' in i['file'] else 'events/'+i['file'] for i in vet['items'] if i['verdict'] in ('GOV','CAUTION')}

def build(force=False):
    os.makedirs(THUMB, exist_ok=True); os.makedirs(FULL, exist_ok=True)
    sizes = {}
    for name, rel in M.items():
        if rel in BAN: raise SystemExit(f'BANNED image used: {name} -> {rel}')
        src = os.path.join(SRC, rel)
        if not os.path.exists(src): raise SystemExit(f'missing {src}')
        im = Image.open(src).convert('RGB')
        t = os.path.join(THUMB, name+'.webp'); f = os.path.join(FULL, name+'.webp')
        if force or not os.path.exists(t):
            a = im.copy(); a.thumbnail((640, 640)); a.save(t, 'WEBP', quality=76, method=6)
        if force or not os.path.exists(f):
            b = im.copy(); b.thumbnail((1600, 1600)); b.save(f, 'WEBP', quality=82, method=6)
        sizes[name] = Image.open(t).size
    json.dump({'map': M, 'sizes': sizes}, open(os.path.join(ROOT,'build','images-manifest.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
    return sizes

if __name__ == '__main__':
    force = '--force' in sys.argv
    if '--heroes' in sys.argv or not os.path.isdir(SRC):
        # بيئة بلا مستودع الإنتاج: نولّد صور الهيرو والشعار فقط من img/full (موجودة في المستودع)
        if not os.path.isdir(SRC): print('note: production images dir not found → heroes/logo only')
    else:
        s = build(force); print(len(s), 'images ready')
    hv = hero_variants(force)
    for k, v in hv.items(): print('hero', k, 'm:', [x[0] for x in v['m']], 'd:', [x[0] for x in v['d']])
    print('logo small', logo_small(force))
