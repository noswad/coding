# 書籍推薦程式

此專案提供 `recommend.py` 腳本，會從 [books.com.tw](https://www.books.com.tw/) 讀取最新暢銷書排行榜，依排名與折扣計算分數並挑選適合的書籍。`app.py` 則使用 Flask 提供簡易網頁介面。

## 安裝與執行

1. 安裝所需套件：

```bash
python3 -m pip install requests beautifulsoup4 flask
```

2. 從命令列執行推薦腳本：

```bash
python3 recommend.py
```

3. 啟動網頁介面：

```bash
python3 app.py
```

瀏覽器開啟 `http://localhost:5000` 後，可輸入要顯示的推薦數量並查看結果。

## 演算法說明

腳本會抓取排行榜上每本書的「排名」與「折扣」，並用下式計算分數：

```
score = (101 - rank) * discount
```

排名越高（數字越小）且折扣越大者，分數越高。最後依分數排序取前 `n` 名，輸出至終端或在網頁上呈現。
