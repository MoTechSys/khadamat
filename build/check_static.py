# فحص ثابت: صور مفقودة/مراسي مكسورة/أسعار/رقم واتساب/معرّفات مكرّرة/كلمات الجهات. تشغيل: cd prototype-home && python3 build/check_static.py
# v6.1: أُزيلت الإيجابيات الكاذبة — روابط بـquery (?type=/?service=) تُفحص بعد حذف الاستعلام، وكلمات الجهات داخل alt لشارات التوثيق (commerce/zatca/sbc svg) تُستثنى. الهدف: BAD 0.
import re,os,sys
pages=['index.html','services.html','offerings.html','portfolio.html','about.html','contact.html']
ids={p:set(re.findall(r'id="([^"]+)"',open(p).read())) for p in pages}
bad=0
for p in pages:
    h=open(p).read()
    # images
    for src in set(re.findall(r'(?:src|href)="(img/[^"]+)"',h)):
        if not os.path.exists(src): print(p,'MISSING IMG',src); bad+=1
    # internal links
    for href in set(re.findall(r'href="([^"#:]*)(#[^"]*)?"',h)):
        f,a=href; f=f.split('?')[0]
        if f and not f.startswith('img/'):
            if not os.path.exists(f): print(p,'MISSING FILE',f); bad+=1; continue
        tgt=f or p
        if a and a!='#' and tgt in ids and a[1:] not in ids[tgt]: print(p,'MISSING ANCHOR',f+a); bad+=1
    # entities
    h_txt=re.sub(r'<img [^>]*src="img/(?:commerce|zatca|sbc)-crop\.svg"[^>]*>','',h)   # شارات التوثيق الرسمية (alt وصفي مطلوب للإتاحة)
    for m in re.findall(r'(أمانة|جامعة أم القرى|وزارة|غرفة جدة|منتدى مكة|هيئة|جهة حكومية)',h_txt): 
        if m!='جهة حكومية': print(p,'ENTITY',m); bad+=1
    # prices
    for m in re.findall(r'(ريال|ر\.س|SAR)',h): print(p,'PRICE',m); bad+=1
    # WA number
    for m in set(re.findall(r'wa\.me/(\d+)',h)):
        if m!='966508252134': print(p,'WA',m); bad+=1
    # dup ids
    allids=re.findall(r'id="([^"]+)"',h)
    d=[i for i in set(allids) if allids.count(i)>1]
    if d: print(p,'DUP IDS',d); bad+=1
    # external links
    ext=set(re.findall(r'href="(https?://[^"]+)"',h)); print(p,'external:',sorted(ext))
print('BAD',bad)
