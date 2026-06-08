import sys, time
from playwright.sync_api import sync_playwright
url=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=b.new_page(viewport={"width":900,"height":700})
    logs=[]
    pg.on("console", lambda m: logs.append(m.text))
    pg.on("pageerror", lambda e: logs.append("PAGEERROR "+str(e)))
    pg.goto(url, wait_until="networkidle", timeout=30000); time.sleep(5); b.close()
    for l in logs:
        if "TEX" in l or "PAGEERROR" in l: print(l[:320])
