# 客家全球新聞網

服務臺灣客家社區與全球客家社群的繁體中文公共資訊站（展示版）。英文名稱 Hakka Global News Network。

本站不是客家委員會，也不是任何政府機關的官方網站。首頁卡片全部是虛構範例，用來展示欄目與版面，不是新聞，沒有受訪者，不能當事實引用。

版面與更新流程比照公開專案「新住民&新移民全球新聞網」：靜態頁面、分類瀏覽、側欄來源、摘要展開，以及 Python 抓取後由人寫摘要才上線。欄目、色彩與文案已改為客家事務。

## 頁面

| 檔案 | 內容 |
| --- | --- |
| `index.html` | 首頁、頭條、七個欄目、來源篩選、載入更多 |
| `about.html` | 宗旨、服務對象、欄目界線、編輯原則 |
| `organization.html` | 編輯分工、待公告的法定資料、展示用聯絡表單 |
| `accessibility.html` | 無障礙做法、字級、對比、響應式版面 |
| `article.html` | 單則範例說明與範例稿一覽 |
| `404.html` | 找不到頁面 |

七個欄目：客家文化、客庄新聞、客語推廣、節慶活動、產業與觀光、全球客家、政策與補助。

## 技術

- 介面：HTML、CSS、JavaScript。沒有框架、沒有資料庫、沒有登入。
- 字型：Noto Sans TC、Noto Serif TC，放在 `fonts/`，授權為 SIL Open Font License 1.1（見 `fonts/OFL.txt`）。
- 資料：`news_db.json` 經 `build_site.py` 產生 `data.js`。只有 `summary_ok` 且摘要 50～200 字的項目會出現在頁面上。
- 無障礙：跳至主要內容、鍵盤操作、三階字級、提高對比、手機版面。尚未申請無障礙標章，說明見無障礙頁。

預覽只需要 Python 3。抓公開來源才要安裝 `requirements.txt`（feedparser、requests、googlenewsdecoder）。

## 本機預覽

```bash
python3 sample_articles.py
python3 build_site.py
python3 check_site.py
./serve.sh
```

瀏覽器開啟 <http://127.0.0.1:41731/> 。`./serve.sh 41731` 會先重建 `data.js`，再在 41731 埠提供整個目錄。

## 改範例稿

編輯 `sample_articles.py`，標題須以「【範例】」開頭，摘要 50～200 字且標明範例。然後：

```bash
python3 sample_articles.py
python3 build_site.py
```

正式新聞不要寫進 `sample_articles.py`。

## 正式新聞怎麼進站

1. `pip install -r requirements.txt`
2. `python3 fetch_news.py 3`  
   從行政院、部會與中央社等公開 RSS，以及客家相關關鍵字篩選。新稿的 `summary_ok` 是 false，**不會出現在網站上**，清單在 `pending_summary.json`。
3. 編輯核對原文後，做一份 `summaries.json`：`{"網址": "50到200字摘要"}`。資訊不足的網址把值寫成 `REMOVE`。
4. `python3 apply_summaries.py summaries.json`
5. `python3 build_site.py`

摘要只改寫公開原文，不補上原文沒有的人名、引述或數字。

## 部署

靜態檔放在儲存庫根目錄，適合 GitHub Pages：設定為從 `main` 分支的根目錄發布。請一併保留 `.nojekyll`，避免 Jekyll 改寫檔案。

```bash
./deploy.sh publish
```

會重建 `data.js`、提交並推送目前分支。`./deploy.sh` 會先抓新聞再部署；沒有合格摘要的項目仍然不會上線。

送補助或標案之前，請先換上申請單位的法定名稱、統一編號與聯絡方式，並移除或替換全部範例稿。步驟寫在「關於我們」。

## 檢查

```bash
python3 check_site.py
```
