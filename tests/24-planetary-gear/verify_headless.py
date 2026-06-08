"""headless 验证 cad-viewer 渲染(playwright + WebGL),不打扰真 Chrome。
用法: python verify_headless.py <url> <out.png> [wait_s]
抓控制台 error/pageerror + 截图。"""
import sys, time
from playwright.sync_api import sync_playwright

url = sys.argv[1]
out = sys.argv[2]
wait_s = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--use-gl=angle", "--use-angle=swiftshader", "--ignore-gpu-blocklist",
        "--enable-webgl", "--enable-unsafe-swiftshader",
    ])
    page = browser.new_page(viewport={"width": 1000, "height": 760})
    errors = []
    page.on("console", lambda m: errors.append(f"[{m.type}] {m.text}") if m.type in ("error", "warning") else None)
    page.on("pageerror", lambda e: errors.append(f"[pageerror] {e}"))
    page.goto(url, wait_until="networkidle", timeout=30000)
    time.sleep(wait_s)
    page.screenshot(path=out)
    browser.close()
    print("screenshot:", out)
    if errors:
        print("=== console errors/warnings ===")
        for e in errors[:25]:
            print(" ", e[:300])
    else:
        print("(无 console error/warning)")
