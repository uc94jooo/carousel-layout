#!/usr/bin/env python3
"""排版小幫手輸出器：把輪播頁 HTML 精確擷取為 1080×1350 PNG。

用法：
  mkt-rag venv 的 python 執行（playwright 裝在那裡）：
  <裝有 playwright 的 python3> export.py <頁面.html ...> [--out 目錄] [--scale 2]

  - 擷取的是 .page 元素本身（不含預覽外框），尺寸恆為 1080×1350（--scale 2 則為 2160×2700）
  - 驅動本機既有的 Chrome（channel=chrome），不需下載瀏覽器
"""
import os, sys
from playwright.sync_api import sync_playwright

args = [a for a in sys.argv[1:]]
scale = 1
outdir = None
if "--scale" in args:
    i = args.index("--scale"); scale = int(args[i+1]); del args[i:i+2]
if "--out" in args:
    i = args.index("--out"); outdir = args[i+1]; del args[i:i+2]
files = args
if not files:
    sys.exit("用法：export.py <頁面.html ...> [--out 目錄] [--scale 2]")

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    page = browser.new_page(viewport={"width": 1200, "height": 1500}, device_scale_factor=scale)
    for f in files:
        url = "file://" + os.path.abspath(f)
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(200)  # 字型/排版安定
        el = page.query_selector(".page")
        if el is None:
            print("略過（找不到 .page）:", f); continue
        d = outdir or os.path.join(os.path.dirname(os.path.abspath(f)), "export")
        os.makedirs(d, exist_ok=True)
        out = os.path.join(d, os.path.splitext(os.path.basename(f))[0] + ".png")
        el.screenshot(path=out)
        print("輸出:", out)
    browser.close()
