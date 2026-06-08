"""抓 cad-viewer 加载某 URL 时的失败请求(>=400)+ 关键请求,headless。
用法: python verify_net.py <url>"""
import sys, time
from playwright.sync_api import sync_playwright

url = sys.argv[1]
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    page = browser.new_page(viewport={"width": 900, "height": 700})
    reqs = []
    def on_resp(r):
        u = r.url
        if "/__cad/" in u or ".glb" in u or "/files/" in u or r.status >= 400:
            reqs.append(f"{r.status}  {u[:160]}")
    page.on("response", on_resp)
    page.goto(url, wait_until="networkidle", timeout=30000)
    time.sleep(3)
    browser.close()
    print("=== 关键/失败请求 ===")
    for r in reqs[:40]:
        print(" ", r)
