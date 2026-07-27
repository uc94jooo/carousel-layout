#!/usr/bin/env python3
"""共用試衣間組裝器：把輪播頁面組成互動 board.html（主題／線框／格線即時切換）。

全技能只有這一份（與 export.py 同模式），勿複製進專案資料夾。

用法：
  python3 build-board.py P1.html P2.html ... \
      [--title 標題] [--out board.html] \
      [--label "P1.html=01 · 封面"] ... \
      [--default-theme gray|warm|pink] [--default-frame on|off] [--default-grid on|off]

- 頁面檔需在同一資料夾；board.html 預設產在該資料夾
- 標籤不指定時自動用「編號 · 檔名」
- assets/themes/fonts 先找頁面資料夾的本地複本，沒有就回退技能目錄
- assets/set.css（本組自組元件）為選配，存在才併入
"""
import argparse, glob, html, io, os, re, sys

TPL = os.path.dirname(os.path.abspath(__file__))            # .../system/templates
SKILL_ROOT = os.path.dirname(os.path.dirname(TPL))          # .../carousel-layout

ap = argparse.ArgumentParser()
ap.add_argument("pages", nargs="+")
ap.add_argument("--title", default="輪播試衣間")
ap.add_argument("--out")
ap.add_argument("--label", action="append", default=[], help="檔名=標籤，可重複")
ap.add_argument("--default-theme", choices=["gray", "warm", "pink"], default="gray")
ap.add_argument("--default-frame", choices=["on", "off"], default="off")
ap.add_argument("--default-grid", choices=["on", "off"], default="off")
a = ap.parse_args()

DIR = os.path.dirname(os.path.abspath(a.pages[0]))
labels = dict(s.split("=", 1) for s in a.label)

def read(p): return io.open(p, encoding="utf-8").read()
def local_or_skill(rel, skill_abs):
    p = os.path.join(DIR, rel)
    return p if os.path.exists(p) else skill_abs

tokens = read(local_or_skill("assets/tokens.css", os.path.join(TPL, "assets/tokens.css")))
themes_dir = DIR + "/themes" if os.path.isdir(os.path.join(DIR, "themes")) else os.path.join(SKILL_ROOT, "themes")
theme_css = "\n".join(read(p) for p in sorted(glob.glob(os.path.join(themes_dir, "*.css"))) if not p.endswith("themes.css"))
base = read(local_or_skill("assets/base.css", os.path.join(TPL, "assets/base.css")))
set_p = os.path.join(DIR, "assets/set.css")
set_css = read(set_p) if os.path.exists(set_p) else ""

css = tokens + "\n" + theme_css + "\n" + base + "\n" + set_css
if os.path.isdir(os.path.join(DIR, "fonts")):
    css = css.replace('url("../fonts/', 'url("fonts/')
else:
    css = css.replace('url("../fonts/', 'url("file://' + os.path.join(TPL, "fonts") + '/')

def embed_imgs(doc):
    import base64, mimetypes
    def repl(m):
        src = m.group(1)
        if src.startswith(("http", "data:", "file:")): return m.group(0)
        fp = os.path.join(DIR, src)
        if not os.path.exists(fp): return m.group(0)
        mime = mimetypes.guess_type(fp)[0] or "image/png"
        b64 = base64.b64encode(open(fp, "rb").read()).decode()
        return m.group(0).replace(src, "data:%s;base64,%s" % (mime, b64))
    return re.sub(r'<img[^>]*\ssrc="([^"]+)"', repl, doc)

def inline(doc):
    doc = embed_imgs(doc)
    doc = re.sub(r'<link rel="stylesheet" href="[^"]*tokens\.css">\s*', "", doc)
    doc = re.sub(r'<link rel="stylesheet" href="[^"]*themes\.css">\s*', "", doc)
    doc = re.sub(r'<link rel="stylesheet" href="[^"]*set\.css">\s*', "", doc)
    doc = re.sub(r'<link rel="stylesheet" href="[^"]*base\.css">',
                 lambda m: "<style>\n" + css + "\n</style>", doc, count=1)
    doc = doc.replace("</head>", "<style>body{padding:0;background:transparent;display:block;}</style></head>")
    return doc

cards = []
for i, f in enumerate(a.pages):
    stem = os.path.splitext(os.path.basename(f))[0]
    label = labels.get(os.path.basename(f), "%02d · %s" % (i + 1, stem))
    cards.append('<div class="thumb"><div class="frame-wrap"><iframe srcdoc="%s"></iframe></div><span class="label">%s</span></div>'
                 % (html.escape(inline(read(os.path.abspath(f))), quote=True), html.escape(label)))

def btn(k, v, text):
    on = {"theme": a.default_theme, "frame": a.default_frame, "grid": a.default_grid}[k] == v
    return '<button data-k="%s" data-v="%s"%s>%s</button>' % (k, v, ' class="on"' if on else "", text)

out = """<!DOCTYPE html>
<html lang="zh-Hant">
<head><meta charset="UTF-8"><title>""" + html.escape(a.title) + """</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#3a3a36; font-family:"PingFang TC",sans-serif; padding:40px; }
h1 { font-size:26px; color:#e8e8e2; margin-bottom:14px; }
.controls { position:sticky; top:0; z-index:9; background:#3a3a36; padding:14px 0 18px;
  display:flex; flex-wrap:wrap; gap:18px; align-items:center; border-bottom:1px solid #55554d; margin-bottom:28px; }
.ctl { display:flex; align-items:center; gap:8px; }
.ctl .name { color:#9a9a90; font-size:13px; letter-spacing:.1em; }
.ctl button { font-size:14px; padding:8px 16px; border-radius:999px; border:1px solid #6a6a60;
  background:#4a4a44; color:#e8e8e2; cursor:pointer; }
.ctl button.on { background:#f7e94e; color:#1b1b19; border-color:#f7e94e; font-weight:700; }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:28px; }
.thumb { color:#e8e8e2; }
.thumb .label { font-size:14px; font-weight:700; margin-top:10px; display:block; }
.frame-wrap { width:100%; aspect-ratio:1080/1350; overflow:hidden; border-radius:8px;
  box-shadow:0 6px 24px rgba(0,0,0,.4); position:relative; background:#eaeae8; }
.frame-wrap iframe { width:1080px; height:1350px; border:0; transform-origin:top left;
  position:absolute; top:0; left:0; pointer-events:none; }
</style></head>
<body>
<h1>""" + html.escape(a.title) + """</h1>
<div class="controls">
  <div class="ctl"><span class="name">主題</span>
    """ + btn("theme", "gray", "灰色") + btn("theme", "warm", "暖色") + btn("theme", "pink", "粉色") + """
  </div>
  <div class="ctl"><span class="name">線框</span>
    """ + btn("frame", "off", "無框") + btn("frame", "on", "有框") + """
  </div>
  <div class="ctl"><span class="name">格線</span>
    """ + btn("grid", "off", "無格") + btn("grid", "on", "有格") + """
  </div>
</div>
<div class="grid">
""" + "\n".join(cards) + """
</div>
<script>
var state = { theme:\"""" + a.default_theme + """\", frame:\"""" + a.default_frame + """\", grid:\"""" + a.default_grid + """\" };

function applyOne(f){
  var d = f.contentDocument; if(!d) return;
  var p = d.querySelector(".page"); if(!p) return;
  p.classList.remove("warm","pink","lined","grid-paper","no-grid");
  if(state.theme==="warm") p.classList.add("warm");
  if(state.theme==="pink") p.classList.add("pink");
  if(state.frame==="on") p.classList.add("lined");
  var isCover = p.classList.contains("cover");
  if(state.grid==="on"){ if(!isCover) p.classList.add("grid-paper"); }
  else { p.classList.add("no-grid"); }
}
function applyAll(){ document.querySelectorAll("iframe").forEach(applyOne); }

document.querySelectorAll(".ctl button").forEach(function(b){
  b.addEventListener("click", function(){
    state[b.dataset.k] = b.dataset.v;
    document.querySelectorAll('.ctl button[data-k="'+b.dataset.k+'"]').forEach(function(x){ x.classList.remove("on"); });
    b.classList.add("on");
    applyAll();
  });
});
document.querySelectorAll("iframe").forEach(function(f){ f.addEventListener("load", function(){ applyOne(f); }); });

function rescale(){document.querySelectorAll(".frame-wrap").forEach(function(w){
  w.querySelector("iframe").style.transform="scale("+(w.clientWidth/1080)+")";});}
window.addEventListener("resize",rescale);window.addEventListener("load",function(){rescale();applyAll();});rescale();
</script>
</body></html>"""

out_path = a.out or os.path.join(DIR, "board.html")
io.open(out_path, "w", encoding="utf-8").write(out)
print("board.html rebuilt: %s（%d 頁，預設 %s/%s框/%s格）" % (out_path, len(a.pages), a.default_theme, a.default_frame, a.default_grid))
