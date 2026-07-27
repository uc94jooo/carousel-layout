# carousel-layout 排版小幫手

IG 輪播的設計系統，目標：讓 AI 產圖／排版維持全系列一致性。

召喚詞：排版小幫手。`SKILL.md` 為啟動器，`system/` 為規格唯一事實來源。

三主題制：**螢光筆灰色**（預設，思考類）／**螢光暖色**（生活感類，class `warm`）／**螢光粉色**（感情輕生活類，class `pink`），定義各自獨立成檔於 `themes/`（一主題一檔，規格在檔頭註解），每組輪播擇一。輸出選配：線框（`.lined`）× 格線（`.grid-paper`／`.no-grid`；暖、粉內頁預設帶格）。

## 架構

版式與文字由 HTML/CSS 模板控制（一致性由 code 保證），AI 只負責生成插畫素材。

| 位置 | 內容 |
|------|------|
| [system/design-tokens.md](system/design-tokens.md) | 共用 token（字型層級、間距圓角）、主題制與新增主題 SOP、字數預算 |
| [system/components.md](system/components.md) | C1～C17 元件文法（螢光筆、對照卡、自介卡…） |
| [system/page-layouts.md](system/page-layouts.md) | L1～L11＋L1b 頁型規格＋敘事順序建議 |
| [themes/](themes/) | 主題定義（一主題一檔） |
| [system/templates/](system/templates/) | 版型 HTML 模板＋共用腳本：`build-board.py`（試衣間）、`export.py`（PNG 輸出）、`build-index.py`（總覽） |
| [examples/qipa-logic/](examples/qipa-logic/) | 完整實戰範例：六頁灰色主題原始檔＋互動試衣間 board.html |

## 範例組（examples/qipa-logic/）

- 新輪播開工時的「預設起點」：複製此資料夾、改頁面內容，版式與品牌層直接繼承
- 版型實例：P1=L1b 雙行封面、P2~P4=L3 出題/揭答、P5=L8 變體、P6=L10 變體
- `assets/set.css`＝「自組元件層」示範（本組專用元件與全域庫的分工方式）
- board.html 重建與變體切換：主題＝頁面根元素 class 加 `warm`／`pink`，線框加 `lined`

## 字體

字體檔不隨 repo 散布。未放入時模板自動退回 Noto Sans TC → PingFang TC（蘋方），版面結構不變，只是字的個性不同。

持有金萱授權者：建立 `system/templates/fonts/` 資料夾（clone 下來不會有），把字體檔複製進去並改名為以下檔名（`tokens.css` 的 `@font-face` 會自動載入）：

| 檔名 | 用途 |
|------|------|
| `jf-jinxuan-extrabold.otf` | 標題（font-weight 900；授權包無 heavy，900 由 extrabold 擔任） |
| `jf-jinxuan-bold.otf` | 次級標題（font-weight 700） |
| `jf-jinxuan-medium.otf` | 內文（font-weight 500） |

若拿到的是 `.ttf`，把 `tokens.css` 裡的副檔名與 `format("opentype")` 改成 `format("truetype")` 即可。
