# تدقيق Playwright للصفحات الست على 390/1440 + lightbox + فلاتر + نموذج. يحتاج خادم على 8787. تشغيل: cd /home/user/webapp && python3 prototype-home/build/audit_playwright.py
import asyncio, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # جذر allpro — اللقطات تُكتب هنا مهما كان cwd
os.makedirs(os.path.join(ROOT, '01-keif-aldiafa/reports/shots/v6'), exist_ok=True)
from playwright.async_api import async_playwright
BASE='http://localhost:8787/'
PAGES = ['index.html','services.html#zamzam','offerings.html#equipment','portfolio.html?type=government','about.html','contact.html?service=hosts','links.html',
         # v6.3 (D62): عيّنة الصفحات المحلية
         'locations.html','city-jeddah.html','city-riyadh.html','sababin-qahwa-jeddah.html#packages','qahwajiin-jeddah.html','qahwajiin-makkah.html','diyafa-munasabat-dammam.html','mubashirin-qahwa-jeddah.html','social.html','legal.html',
         # v6.8 (D95–D97): كل الصفحات المحلية بمخطّط واحد — عيّنة إضافية
         'city-abha.html','sababin-qahwa-yanbu.html','diyafa-munasabat-taif.html']
async def main():
    res={}
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for vw,name in [(390,'m'),(1440,'d')]:
            for pg in PAGES:
                ctx=await b.new_context(viewport={'width':vw,'height':844 if vw==390 else 900},device_scale_factor=1)
                page=await ctx.new_page(); errs=[]
                page.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
                page.on('pageerror',lambda e: errs.append(str(e)))
                page.on('requestfailed',lambda r: errs.append('REQFAIL '+r.url))
                await page.goto(BASE+pg,wait_until='networkidle'); await page.wait_for_timeout(800)
                info=await page.evaluate("""()=>{
                  const d=document.documentElement; const fab=document.getElementById('fab');
                  const h=location.hash.slice(1); const t=h?document.getElementById(h):null;
                  return {hscroll:d.scrollWidth>d.clientWidth, sw:d.scrollWidth, cw:d.clientWidth,
                    fabHidden: fab?fab.classList.contains('hide'):null, scrollY:window.scrollY,
                    hit: t?t.classList.contains('hit'):null, title:document.title,
                    imgsBroken:[...document.images].filter(i=>i.complete&&i.naturalWidth===0&&!i.hidden&&i.loading!=='lazy'&&i.id!=='lbImg').length,
                    pcount:(document.getElementById('pcount')||{}).textContent||null,
                    svcSel:(document.querySelector('select[name=service]')||{}).value||null}}""")
                await page.evaluate("window.scrollTo(0,600)"); await page.wait_for_timeout(500)
                info['fabAfterScroll']=await page.evaluate("document.getElementById('fab')?.classList.contains('hide')")
                await page.evaluate("window.scrollTo(0,0)"); await page.wait_for_timeout(300)
                fn=os.path.join(ROOT, f"01-keif-aldiafa/reports/shots/v6/{name}-{pg.split('.html')[0]}.png")
                await page.screenshot(path=fn,full_page=False)
                # v6.1: لقطة كاملة الطول أيضًا للمراجعة البصرية — نُظهر عناصر .rv أولًا حتى لا تخرج شفافة
                await page.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'))"); await page.wait_for_timeout(300)
                await page.screenshot(path=fn.replace('.png','-full.png'),full_page=True)
                info['errors']=errs; res[f'{name} {pg}']=info
                print(name,pg,json.dumps(info,ensure_ascii=False))
                await ctx.close()
        # lightbox + filter + form
        ctx=await b.new_context(viewport={'width':1440,'height':900}); page=await ctx.new_page()
        await page.goto(BASE+'services.html',wait_until='networkidle')
        await page.click('#hosts figure img'); await page.wait_for_timeout(500)
        print('LB', await page.evaluate("({open:document.getElementById('lb').classList.contains('open')||document.getElementById('lb').getAttribute('aria-hidden'), src:document.getElementById('lbImg').src, cap:document.getElementById('lbCap').textContent})"))
        await page.keyboard.press('Escape')
        await page.goto(BASE+'portfolio.html?type=weddings',wait_until='networkidle'); await page.wait_for_timeout(500)
        print('PF alias', await page.evaluate("({url:location.search, cnt:document.getElementById('pcount')?.textContent, visible:[...document.querySelectorAll('.pgrid figure')].filter(f=>!f.hidden&&getComputedStyle(f).display!='none').length, gov:getComputedStyle(document.getElementById('govnote')||document.body).display})"))
        await page.goto(BASE+'contact.html?service=zamzam',wait_until='networkidle')
        await page.fill('input[name=name]','تجربة'); await page.fill('input[name=phone]','0500000000'); await page.fill('textarea[name=message]','تفاصيل تجريبية')   # v6.1: الرسالة إلزامية في التحقق
        # v6.1: نعترض window.open لقراءة رابط wa.me الأصلي (إعادة توجيه wa.me→api.whatsapp تُفسد الترميز في headless)
        await page.evaluate("window.open=(u)=>{window.__waUrl=u}")
        await page.click('form button[type=submit]'); await page.wait_for_timeout(500)
        import urllib.parse as U
        wa=await page.evaluate("window.__waUrl||''"); print('FORM', wa.startswith('https://wa.me/966508252134?text='), U.unquote(wa).replace('\n',' | ')[:160], await page.evaluate("window.dataLayer"))
        await b.close()
asyncio.run(main())
