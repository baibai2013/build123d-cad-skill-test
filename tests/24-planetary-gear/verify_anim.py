"""headless 验证动画:拍两帧比较是否在动 + 截图。用法: python verify_anim.py <url>"""
import sys, time, hashlib
from playwright.sync_api import sync_playwright
url = sys.argv[1]
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 900, "height": 700})
    errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(url, wait_until="networkidle", timeout=30000)
    time.sleep(4)
    f1 = pg.screenshot(path="/tmp/frame1.png")
    time.sleep(2.5)
    f2 = pg.screenshot(path="/tmp/frame2.png")
    b.close()
    h1, h2 = hashlib.md5(f1).hexdigest(), hashlib.md5(f2).hexdigest()
    print("frame1 == frame2 (静止)?", h1 == h2)
    print("两帧字节:", len(f1), len(f2))
    if errs: print("pageerror:", errs[:5])
