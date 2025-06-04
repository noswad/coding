"""從 books.com.tw 抓取排行榜並依排名與折扣推薦書籍。"""

import re
import requests
from bs4 import BeautifulSoup

URL = "https://www.books.com.tw/web/sys_saletopb/books/"


def fetch_books(url=URL):
    """抓取排行榜上的書籍資訊並回傳為字典列表。"""
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    for li in soup.select('li.item:has(div.type02_bd-a)'):
        rank_tag = li.select_one('p.no_list strong.no')
        title_tag = li.select_one('div.type02_bd-a h4 a')
        author_tag = li.select_one('ul.msg li')
        price_text = li.select_one('li.price_a')
        if not (rank_tag and title_tag and author_tag and price_text):
            continue
        # Extract numbers
        rank = int(rank_tag.text.strip())
        title = title_tag.text.strip()
        author = author_tag.text.strip().replace('作者：', '').strip()
        # price_text like "優惠價：79折474元"
        m = re.search(r'(\d+)\D*折(\d+)', price_text.text)
        if m:
            discount = int(m.group(1))
            price = int(m.group(2))
        else:
            discount = 100
            price = 0
        items.append({
            'rank': rank,
            'title': title,
            'author': author,
            'discount': discount,
            'price': price,
        })
    return items


def recommend(n=5):
    """依排名與折扣計算分數並回傳前 n 名書籍。"""
    books = fetch_books()
    for book in books:
        # 分數 = (101 - 排名) * 折扣，數字越大代表越推薦
        book['score'] = (101 - book['rank']) * book['discount']
    books.sort(key=lambda b: b['score'], reverse=True)
    return books[:n]


def main():
    """以 CLI 方式列出推薦書單。"""
    recs = recommend()
    print("Top recommendations from books.com.tw:")
    for idx, b in enumerate(recs, 1):
        print(f"{idx}. {b['title']} ({b['author']}) - Rank {b['rank']} | {b['discount']}折 {b['price']}元")


if __name__ == "__main__":
    main()
