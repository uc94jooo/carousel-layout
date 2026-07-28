# carousel-layout 排版小幫手

IG 輪播的設計系統，目標：讓 AI 產圖／排版維持全系列一致性。

召喚詞：排版小幫手。`SKILL.md` 為啟動器，`system/` 為規格唯一事實來源。

## 產線流程（給協作者的白話版）

社群輪播圖是這樣生出來的，總共三個角色：AI、編輯人員、出圖人員。

1. **AI 排草稿**：把文章交給 AI，它會先整理出一份「工單」（每一頁要放什麼字、
   用什麼版型的清單）。⏸ 編輯人員裁決工單（可直接改工單檔或下指令），
   確認後 AI 把它排成網頁版的草稿頁面。
2. **編輯人員在 Keynote 定稿**：AI 把草稿轉成一份**可編輯的 Keynote／PowerPoint
   檔**（文字都是真的文字框，點兩下就能改）。編輯人員在這裡做最後修整——改字、
   挪位置、調留白。**這份改完的簡報檔就是最終版本**，前面的網頁草稿不用管它。
3. **編輯人員輸出 PNG**：定稿後，用 Keynote 的「輸出至影像」批次轉出每頁 PNG。
4. **出圖人員補插圖**：PNG 裡會有幾個**留白的插圖框，框內有一行灰字說明**
   （例如「插圖：上課東張西望的小孩」）。把整張 PNG 丟給 ChatGPT 或 NotebookLM，
   請它照框內說明把圖生在那個位置。
5. **上傳社群**：補完圖的成品 PNG 就是最終交付，直接上傳。

一句話總結：**AI 排到 80 分 → 編輯人員在 Keynote 改到 100 分 → Keynote 出 PNG →
補圖 → 上線**。中途要改文字或版面，一律回 Keynote 檔改、重新輸出 PNG，
不要直接改圖檔；也不要回頭改網頁草稿——定稿只認 Keynote 檔。

三主題制：**螢光筆灰色**（預設，思考類）／**螢光暖色**（生活感類，class `warm`）／**螢光粉色**（感情輕生活類，class `pink`），定義各自獨立成檔於 `themes/`（一主題一檔，規格在檔頭註解），每組輪播擇一。輸出選配：線框（`.lined`）× 格線（`.grid-paper`／`.no-grid`；暖、粉內頁預設帶格）。

## 架構

版式與文字由 HTML/CSS 模板控制（一致性由 code 保證），AI 只負責生成插畫素材。

| 位置 | 內容 |
|------|------|
| [system/design-tokens.md](system/design-tokens.md) | 共用 token（字型層級、間距圓角）、主題制與新增主題 SOP、字數預算 |
| [system/components.md](system/components.md) | C1～C17 元件文法（螢光筆、對照卡、自介卡…） |
| [system/page-layouts.md](system/page-layouts.md) | L1～L11＋L1b 頁型規格＋敘事順序建議 |
| [themes/](themes/) | 主題定義（一主題一檔） |
| [system/templates/](system/templates/) | 版型 HTML 模板＋共用腳本：`export-editable-pptx.py`（可編輯 PPTX，預設產線終點）、`build-board.py`（試衣間，選配）、`export.py`（HTML 直出 PNG，選配）、`build-index.py`（總覽） |

## 字體

字體檔不隨 repo 散布。未放入時模板自動退回 Noto Sans TC → PingFang TC（蘋方），版面結構不變，只是字的個性不同。

持有金萱授權者：建立 `system/templates/fonts/` 資料夾（clone 下來不會有），把字體檔複製進去並改名為以下檔名（`tokens.css` 的 `@font-face` 會自動載入）：

| 檔名 | 用途 |
|------|------|
| `jf-jinxuan-extrabold.otf` | 標題（font-weight 900；授權包無 heavy，900 由 extrabold 擔任） |
| `jf-jinxuan-bold.otf` | 次級標題（font-weight 700） |
| `jf-jinxuan-medium.otf` | 內文（font-weight 500） |

若拿到的是 `.ttf`，把 `tokens.css` 裡的副檔名與 `format("opentype")` 改成 `format("truetype")` 即可。
