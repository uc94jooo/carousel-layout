#!/usr/bin/env python3
"""重新生成 index.html 總覽頁：把每個模板的 CSS 內嵌後以 srcdoc 塞進縮圖，
完全自包含，file:// 直開不會被瀏覽器擋跨檔案載入。模板改動後重跑本腳本。
上方按鈕可篩選：範例頁面／全部物件／小物件／中物件／半頁物件／全頁物件。"""
import io, html, os, re

HERE = os.path.dirname(os.path.abspath(__file__))

# (檔名, 標籤, 篩選分類)——分類：小/中/半/全（物件依尺度範圍可屬多類）
OBJECTS = [
    ("C0-headings.html", "C0 標題 H1／H2／H3【常用｜小區塊｜標題】", "小 題"),
    ("C1-highlight.html", "C1 螢光筆標記【文字級】", "小"),
    ("C2-series-pill.html", "C2 系列標籤【小區塊｜標題】", "小 題"),
    ("C3-subtitle.html", "C3 副標分隔線【小區塊｜標題】", "小 題"),
    ("C4-bubbles.html", "C4 對話框【小區塊～中區塊】", "小 中"),
    ("C5-scenario.html", "C5 情境卡【中區塊】", "中"),
    ("C6-versus.html", "C6 對照卡【中區塊～半頁】", "中 半"),
    ("C6b-uneven.html", "C6b 非等比對照【中區塊～半頁】", "中 半"),
    ("C6c-bignum.html", "C6c 大數字對照【中區塊～半頁】", "中 半"),
    ("C6d-textimg.html", "C6d 非等比圖文區【半頁】", "半"),
    ("C7-num.html", "C7 編號圓圈【小區塊】", "小"),
    ("C8-quote.html", "C8 引言黑線框【中區塊～半頁】", "中 半"),
    ("C9-columns.html", "C9 欄組家族【中區塊】", "中"),
    ("C10-flowstrip.html", "C10 橫向流程條【小區塊】", "小"),
    ("C11-cta.html", "C11 CTA 黃條【小區塊】", "小"),
    ("C13-footer.html", "C13 頁尾簽名【小區塊｜固定】", "小"),
    ("C14-checklist.html", "C14 勾選清單【中區塊～半頁】", "中 半"),
    ("C14a-numlist.html", "C14a 編號圓圈清單【中區塊～半頁】", "中 半"),
    ("C15-bigquote.html", "C15 金句引號【中區塊～半頁】", "中 半"),
    ("C16-author.html", "C16 自介卡【中區塊】", "中"),
    ("C17-iconflow.html", "C17 垂直 icon 流程【半頁～全頁】", "半 全"),
    ("C18-pills.html", "C18 膠囊家族【常用｜小區塊～中區塊】", "小 中"),
    ("C19-fork.html", "C19 岔路家族【常用｜半頁～全頁】", "半 全"),
    ("C20-spectrum.html", "C20 光譜條【備用｜小區塊】", "小"),
    ("C21-dual.html", "C21 同詞雙義卡【備用｜中區塊～半頁】", "中 半"),
    ("C22-note.html", "C22 對話邊註【備用｜小區塊】", "小"),
    ("C23-cycle.html", "C23 循環圖【常用｜中區塊～半頁】", "中 半"),
    ("C24-slot.html", "C24 圖位【小區塊～全頁】", "小 中 半 全"),
    ("C25-bigstat.html", "C25 超大數字【常用｜中區塊～半頁】", "中 半"),
    ("C26-term.html", "C26 中英名詞標【常用｜小區塊｜標題】", "小 題"),
    ("C26b-reveal.html", "C26b 外文揭曉【中區塊｜標題】", "中 題"),
]

# (檔名, 任務標籤, 頁面中使用的物件編號)
TASKS = [
    ("L1-cover.html", "L1 勾住第一眼（封面）", "C1・C2・C3・C24・C13"),
    ("L1b-cover-2line.html", "L1b 勾住第一眼（雙行標題封面）", "C1・C2・C3・C24・C13"),
    ("L2-hook-dialogue.html", "L2 釣出「這就是我」（情境提問）", "C1・C5×2・C13"),
    ("L3-concept.html", "L3 講一個概念", "C1・C24・C13"),
    ("L4-image-lead.html", "L4 讓畫面說話（視覺主導）", "C1・C24・C13"),
    ("L5-scene-full.html", "L5 情境重現（滿版）", "C4・C24 滿版・C13"),
    ("L6-two-cols.html", "L6 平行比較（對照）", "C1・C6・C10・C13"),
    ("L7-fact.html", "L7 立知識錨點（定律重點）", "C1・C8・C9・C13"),
    ("L8-case-stack.html", "L8 原來到處都是（案例堆疊）", "C1・C7・C24・C13"),
    ("L9-flow.html", "L9 拆解因果鏈（流程）", "C1・C7・C17 同族・C13"),
    ("L10-summary-cta.html", "L10 收束＋邀請互動（總結）", "C1・C7・C11・C13"),
    ("L11-outro-profile.html", "L11 拉回讀者＋轉追蹤（自介收尾）", "C1・C16"),
    ("L12-story-annotated.html", "L12 敘事零刪減＋機制攤開", "C1・C9 或 C18・C24・C13"),
    ("L13-scale-contrast.html", "L13 用字級表演放大縮小", "C1・C13"),
]

def read(p):
    return io.open(os.path.join(HERE, p), encoding="utf-8").read()

import glob as _g
css = read("assets/tokens.css") + "\n" + "\n".join(io.open(p, encoding="utf-8").read() for p in sorted([p for p in _g.glob(os.path.join(HERE, "../../themes/*.css")) if not p.endswith("themes.css")])) + "\n" + read("assets/base.css")
css = css.replace('url("../fonts/', 'url("fonts/')  # index 在 templates/ 根層

def inline(page_html):
    page_html = re.sub(r'<link rel="stylesheet" href="assets/tokens\.css">\s*', "", page_html)
    page_html = page_html.replace('<link rel="stylesheet" href="assets/base.css">',
                                  "<style>\n" + css + "\n</style>")
    page_html = page_html.replace("</head>",
        "<style>body{padding:0;background:transparent;display:block;}</style></head>")
    return page_html

def card(f, label, cats, sub=None):
    doc = inline(read(f))
    subline = '<span class="objs">物件：%s</span>' % sub if sub else ""
    return ('<a class="thumb" data-cat="%s" href="%s" target="_blank">'
            '<div class="frame-wrap"><iframe srcdoc="%s"></iframe></div>'
            '<span class="label">%s</span>%s</a>'
            % (cats, f, html.escape(doc, quote=True), label, subline))

obj_cards = "\n".join(card(f, lb, "obj " + cats) for f, lb, cats in OBJECTS)
task_cards = "\n".join(card(f, lb, "task", sub=objs) for f, lb, objs in TASKS)
total = len(OBJECTS) + len(TASKS)

out = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<title>排版小幫手：物件庫與任務實例總覽</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #cfcfcd; font-family: "PingFang TC", sans-serif; padding: 40px; }
  h1 { font-size: 28px; margin-bottom: 8px; }
  h2 { font-size: 20px; margin: 36px 0 16px; color: #1b1b19; }
  p  { color: #55554f; margin-bottom: 20px; }
  .filters { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 12px; }
  .filters button {
    font-size: 15px; font-weight: 700; padding: 10px 22px; border-radius: 999px;
    border: 2px solid #1b1b19; background: #fff; cursor: pointer;
  }
  .filters button.active { background: #1b1b19; color: #fff; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 28px; }
  .thumb { text-decoration: none; color: #1b1b19; }
  .thumb.hide { display: none; }
  .thumb .label { font-size: 15px; font-weight: 700; margin-top: 10px; display: block; }
  .thumb .objs { font-size: 13px; color: #55554f; display: block; margin-top: 2px; }
  .frame-wrap {
    width: 100%; aspect-ratio: 1080 / 1350; overflow: hidden; border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0,0,0,.18); position: relative; background: #eaeae8;
  }
  .frame-wrap iframe {
    width: 1080px; height: 1350px; border: 0; transform-origin: top left;
    position: absolute; top: 0; left: 0; pointer-events: none;
  }
  section.hide { display: none; }
</style>
</head>
<body>
<h1>排版小幫手：物件庫與任務實例總覽</h1>
<p>點縮圖開啟原尺寸模板（1080 × 1350）。虛線框為圖位（C24），正式產圖時替換。</p>
<div class="filters">
  <button data-f="all" class="active">全部</button>
  <button data-f="task">範例頁面</button>
  <button data-f="obj">全部物件</button>
  <button data-f="小">小物件</button>
  <button data-f="中">中物件</button>
  <button data-f="半">半頁物件</button>
  <button data-f="全">全頁物件</button>
  <button data-f="題">標題</button>
</div>
<section id="sec-obj">
<h2>物件（積木：可調檔位、可變化，變化寫進工單）</h2>
<div class="grid">
""" + obj_cards + """
</div>
</section>
<section id="sec-task">
<h2>任務實例（組裝範例：結構可重排，任務才是不變的）</h2>
<div class="grid">
""" + task_cards + """
</div>
</section>
<script>
  function rescale() {
    document.querySelectorAll(".frame-wrap").forEach(function (w) {
      w.querySelector("iframe").style.transform = "scale(" + (w.clientWidth / 1080) + ")";
    });
  }
  window.addEventListener("resize", rescale);
  window.addEventListener("load", rescale);
  rescale();

  document.querySelectorAll(".filters button").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".filters button").forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");
      var f = btn.dataset.f;
      document.querySelectorAll(".thumb").forEach(function (t) {
        var cats = t.dataset.cat.split(" ");
        var show = (f === "all") || cats.indexOf(f) !== -1;
        t.classList.toggle("hide", !show);
      });
      document.getElementById("sec-obj").classList.toggle("hide", f === "task");
      document.getElementById("sec-task").classList.toggle("hide", f !== "all" && f !== "task");
      rescale();
    });
  });
</script>
</body>
</html>
"""
io.open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(out)
print("index.html rebuilt: %d tiles (%d objects + %d tasks)" % (total, len(OBJECTS), len(TASKS)))
