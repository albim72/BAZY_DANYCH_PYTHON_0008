#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper demo: requests + BeautifulSoup
Serwis: https://books.toscrape.com/  (serwis szkoleniowy do scrapingu)

Funkcje:
- Szanuje robots.txt (robotparser)
- Sesja HTTP z nagłówkami, timeoutami i retry (HTTPAdapter + Retry)
- Paginacja listy produktów
- Przejście na stronę szczegółową i pobranie dodatkowych danych
- Czyszczenie tekstu
- Zapis do CSV i JSON
"""

from __future__ import annotations
import csv
import json
import time
import re
from dataclasses import dataclass, asdict
from typing import Iterator, Optional, Dict, List, Tuple
from urllib.parse import urljoin, urlparse
from urllib import robotparser

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

try:
    from tqdm import tqdm  # opcjonalnie do ładnego paska postępu
    HAS_TQDM = True
except Exception:
    HAS_TQDM = False


BASE = "https://books.toscrape.com/"
START_CATEGORY = urljoin(BASE, "catalogue/category/books_1/index.html")  # cała księgarnia
OUTPUT_CSV = "books.csv"
OUTPUT_JSON = "books.json"
REQUEST_DELAY = 0.5  # opóźnienie między żądaniami (sekundy) — uprzejmość dla serwera


# ---------------------------
# Pomocnicze: czyszczenie tekstu
# ---------------------------
def clean_text(s: Optional[str]) -> str:
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s).strip()
    return s


def price_to_float(price_str: str) -> float:
    # przykłady: "£51.77" → 51.77
    s = re.sub(r"[^\d.,]", "", price_str)
    s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def rating_to_int(star_class: str) -> int:
    """
    Klasy w HTML: 'star-rating One' ... 'Five'
    """
    mapping = {"Zero": 0, "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    for word, val in mapping.items():
        if word.lower() in star_class.lower():
            return val
    return 0


# ---------------------------
# Dane domenowe
# ---------------------------
@dataclass
class Book:
    title: str
    price: float
    availability: str
    rating: int
    product_url: str
    product_upc: str
    product_type: str
    tax: float
    price_excl_tax: float
    price_incl_tax: float
    description: str
    category: str
    image_url: str


# ---------------------------
# Sesja HTTP z retry i headers
# ---------------------------
def build_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0 Safari/537.36",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
    })
    retries = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s


# ---------------------------
# robots.txt
# ---------------------------
def can_fetch(url: str, user_agent: str = "*") -> bool:
    parsed = urlparse(BASE)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        # jeśli nie uda się wczytać robots.txt, bądź ostrożny – tu zwracamy True dla serwisu demonstracyjnego
        return True
    return rp.can_fetch(user_agent, url)


# ---------------------------
# Pobranie i parsowanie HTML
# ---------------------------
def get_soup(session: requests.Session, url: str, delay: float = REQUEST_DELAY) -> BeautifulSoup:
    if not can_fetch(url):
        raise RuntimeError(f"Robots.txt zabrania pobierania: {url}")
    resp = session.get(url, timeout=15)
    resp.raise_for_status()
    time.sleep(delay)  # uprzejme opóźnienie
    return BeautifulSoup(resp.text, "html.parser")


# ---------------------------
# Parsowanie listy i paginacji
# ---------------------------
def parse_list_page(soup: BeautifulSoup, base_url: str) -> Tuple[List[str], Optional[str], str]:
    """
    Zwraca:
    - listę URLi do stron produktów,
    - URL do kolejnej strony (lub None),
    - nazwę kategorii (z breadcrumbs)
    """
    # kategoria z okruszków
    cat = soup.select_one("ul.breadcrumb li.active")
    category = clean_text(cat.get_text()) if cat else ""

    product_links = []
    for article in soup.select("article.product_pod h3 a"):
        href = article.get("href")
        if not href:
            continue
        # linki są relatywne, np. "../../../the-grand-design_405/index.html"
        prod_url = urljoin(base_url, href)
        product_links.append(prod_url)

    # paginacja
    next_link = soup.select_one("li.next a")
    next_url = urljoin(base_url, next_link["href"]) if next_link and next_link.get("href") else None

    return product_links, next_url, category


# ---------------------------
# Parsowanie strony produktu
# ---------------------------
def parse_product_page(soup: BeautifulSoup, product_url: str, category_fallback: str) -> Book:
    title = clean_text(soup.select_one("div.product_main h1").get_text())

    # cena i rating
    price_str = clean_text(soup.select_one("p.price_color").get_text())
    price_val = price_to_float(price_str)

    rating_class = soup.select_one("p.star-rating")
    rating_val = rating_to_int(" ".join(rating_class.get("class", []))) if rating_class else 0

    # dostępność
    availability = clean_text(soup.select_one("p.availability").get_text())

    # opis
    desc_tag = soup.select_one("#product_description ~ p")
    description = clean_text(desc_tag.get_text()) if desc_tag else ""

    # tabela parametrów
    info: Dict[str, str] = {}
    for row in soup.select("table.table.table-striped tr"):
        th = clean_text(row.select_one("th").get_text())
        td = clean_text(row.select_one("td").get_text())
        info[th] = td

    # obraz
    img = soup.select_one("div.item.active img")
    img_url = urljoin(product_url, img.get("src")) if img and img.get("src") else ""

    # kategoria (breadcrumbs → przedostatni element)
    crumbs = [clean_text(x.get_text()) for x in soup.select("ul.breadcrumb li a, ul.breadcrumb li.active")]
    category = crumbs[-2] if len(crumbs) >= 2 else category_fallback

    # dodatkowe pola liczbowe
    def getf(key: str) -> float:
        return price_to_float(info.get(key, ""))

    book = Book(
        title=title,
        price=price_val,
        availability=availability,
        rating=rating_val,
        product_url=product_url,
        product_upc=info.get("UPC", ""),
        product_type=info.get("Product Type", ""),
        tax=getf("Tax"),
        price_excl_tax=getf("Price (excl. tax)"),
        price_incl_tax=getf("Price (incl. tax)"),
        description=description,
        category=category,
        image_url=img_url,
    )
    return book


# ---------------------------
# Iteracja po całej kategorii (z paginacją) i szczegółach
# ---------------------------
def crawl_category(session: requests.Session, start_url: str) -> Iterator[Book]:
    current_url = start_url
    page_no = 1
    while current_url:
        soup = get_soup(session, current_url)
        product_links, next_url, category = parse_list_page(soup, current_url)

        iterator = product_links
        if HAS_TQDM:
            iterator = tqdm(product_links, desc=f"Strona {page_no}: produkty", unit="prod")

        for prod_url in iterator:
            # Upewnij się, że link prowadzi do /catalogue/..., nie do relative „../../..”
            full_url = urljoin(current_url, prod_url)
            prod_soup = get_soup(session, full_url)
            yield parse_product_page(prod_soup, full_url, category)

        current_url = next_url
        page_no += 1


# ---------------------------
# Zapis wyników
# ---------------------------
def save_csv(books: List[Book], path: str) -> None:
    if not books:
        return
    fields = list(asdict(books[0]).keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for b in books:
            writer.writerow(asdict(b))


def save_json(books: List[Book], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(b) for b in books], f, ensure_ascii=False, indent=2)


# ---------------------------
# Główne wykonanie
# ---------------------------
def main() -> None:
    session = build_session()

    print(f"Start: {START_CATEGORY}")
    books: List[Book] = []
    for book in crawl_category(session, START_CATEGORY):
        books.append(book)

    print(f"Pobrano pozycji: {len(books)}")
    save_csv(books, OUTPUT_CSV)
    save_json(books, OUTPUT_JSON)
    print(f"Zapisano: {OUTPUT_CSV}, {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
