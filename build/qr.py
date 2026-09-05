#!/usr/bin/env python3
"""D101 — الباركود الموحّد لصفحة الروابط.
الاستخدام:  python3 build/qr.py [URL]
الافتراضي: https://keifaldiafa.com/links  (رابط الإنتاج المستقبلي؛ للنموذج مرّر رابط النموذج).
يُخرج في prototype-home/qr/: links-qr.svg (طباعة، متجه) · links-qr-1024.png · links-qr-card-1080.png (بطاقة بشعار واسم ورقم للنشر)."""
import sys, os, qrcode
from qrcode.image.svg import SvgPathImage
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(ROOT, 'qr'); os.makedirs(OUT, exist_ok=True)
URL = sys.argv[1] if len(sys.argv) > 1 else 'https://keifaldiafa.com/links'
GOLD = (197, 160, 89); INK = (13, 13, 13); CREAM = (245, 245, 245)

def qr(url, **kw):
    q = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=kw.get('box', 20), border=kw.get('border', 2)); q.add_data(url); q.make(fit=True); return q

# 1) SVG متجه للطباعة (أسود على أبيض — أعلى قابلية قراءة للماسحات)
img = qr(URL, box=10).make_image(image_factory=SvgPathImage); img.save(os.path.join(OUT, 'links-qr.svg'))

# 2) PNG 1024 بشعار في المنتصف (تصحيح أخطاء H يسمح بتغطية ~30%)
pil = qr(URL).make_image(fill_color='black', back_color='white').convert('RGBA').resize((1024, 1024), Image.NEAREST)
emb = Image.open(os.path.join(ROOT, 'img', 'logo-emblem.webp')).convert('RGBA'); emb.thumbnail((200, 200))
badge = Image.new('RGBA', (240, 240), (255, 255, 255, 255)); ImageDraw.Draw(badge).rounded_rectangle((0, 0, 239, 239), radius=40, fill=(255, 255, 255, 255), outline=GOLD, width=6)
badge.alpha_composite(emb, ((240 - emb.width) // 2, (240 - emb.height) // 2)); pil.alpha_composite(badge, (392, 392)); pil.save(os.path.join(OUT, 'links-qr-1024.png'))

# 3) بطاقة نشر 1080×1350 (داكنة/ذهبية بهوية الموقع)
W, H = 1080, 1350; card = Image.new('RGBA', (W, H), INK + (255,)); d = ImageDraw.Draw(card)
d.rounded_rectangle((60, 60, W - 60, H - 60), radius=48, outline=GOLD, width=3)
def font(p, s):
    try: return ImageFont.truetype(p, s)
    except Exception: return ImageFont.load_default()
AMIRI = next((p for p in ['/usr/share/fonts/opentype/fonts-hosny-amiri/Amiri-Bold.ttf', '/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf'] if os.path.exists(p)), '')
LATIN = next((p for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'] if os.path.exists(p)), '')
f_head = font(AMIRI, 60); f_lat = font(LATIN, 30)
emb2 = Image.open(os.path.join(ROOT, 'img', 'logo-emblem.webp')).convert('RGBA'); emb2.thumbnail((150, 180)); card.alpha_composite(emb2, ((W - emb2.width) // 2, 120))
qimg = qr(URL, box=16, border=1).make_image(fill_color=INK, back_color='white').convert('RGBA').resize((660, 660), Image.NEAREST)
frame = Image.new('RGBA', (700, 700), (255, 255, 255, 255)); ImageDraw.Draw(frame).rounded_rectangle((0, 0, 699, 699), radius=36, fill=(255, 255, 255, 255)); frame.alpha_composite(qimg, (20, 20))
b2 = badge.resize((170, 170), Image.LANCZOS); frame.alpha_composite(b2, (265, 265)); card.alpha_composite(frame, ((W - 700) // 2, 340))
d.text((W // 2, 1095), 'KEIF AL-DIAFA', font=f_lat, fill=GOLD, anchor='mm')
d.text((W // 2, 1155), 'امسح الباركود واختر قناة التواصل', font=f_head, fill=CREAM, anchor='mm', direction='rtl', language='ar')
d.text((W // 2, 1232), '0508252134  ·  keifaldiafa.com/links', font=f_lat, fill=GOLD, anchor='mm')
card.convert('RGB').save(os.path.join(OUT, 'links-qr-card-1080.png'), optimize=True)
print('URL:', URL); print('->', sorted(os.listdir(OUT)))
