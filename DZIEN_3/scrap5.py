#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper demo: requests + BeautifulSoup z limitem stron (MAX_PAGES)
Serwis: https://books.toscrape.com/  (serwis szkoleniowy do scrapingu)

Funkcje:
- Parametr MAX_PAGES ogranicza liczbę stron listy do pobrania
- Szanuje robots.txt (robotparser)
- Sesja HTTP z nagłówkami, timeoutami i retry (HTTPAdapter + Retry)
- Paginacja listy produktów
- Wejście na stronę szczegółową (zbieranie dodatkowych danych)
- Czyszczenie tekstu i konwersje (cena, rating)
- Zapis do CSV i JSON
"""

from __future__ import annotations
import csv
import json
import time
import re
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Tuple, Iterator
from urllib.parse import urljoin, urlparse
from urllib import robotparser

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

try:
    from tqdm import tqdm
    HAS_TQDM = True
except Exception:
    HAS_TQDM = False


# ---------------------------
# Konfiguracja
# ---------------------------
BASE = "https://books.toscrape.com/"
START_CATEGORY = urljoin(BASE, "catalogue/category/books_1/index.html")  # cała księgarnia
OUTPUT_CSV = "books.csv"
OUTPUT_JSON = "books.json"
REQUEST_DELAY = 0.4  # sek. opóźnienia między żądaniami
MAX_PAGES = 5        # <=== ILE STRON LISTY POBIERAMY (np. 2, 5, 10, 50)


# ---------------------------
# Utils: czyszczenie / konwersje
# ---------------------------
def clean_text(s: Optional[str]) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()


def price_to_float(price_str: str) -> float:
    # "£51.77" -> 51.77
    s = re.sub(r"[^\d.,]", "", price_str or "")
    s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def rating_to_int(star_class: str) -> int:
    # Klasy: "star-rating One/Two/Three/Four/Five"
    mapping = {"Zero": 0, "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    for word, val in mapping.items():
        if word.lower() in (star_class or "").lower():
            return val
    return 0


# ---------------------------
# Model danych
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
# Sesja HTTP (retry + headers)
# ---------------------------
def build_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
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
        return True  # dla serwisu demo; w realu rozważ ostrożność
    return rp.can_fetch(user_agent, url)


# ---------------------------
# Pobieranie i parsowanie HTML
# ---------------------------
def get_soup(session: requests.Session, url: str, delay: float = REQUEST_DELAY) -> BeautifulSoup:
    if not can_fetch(url):
        raise RuntimeError(f"Robots.txt zabrania pobierania: {url}")
    resp = session.get(url, timeout=15)
    resp.raise_for_status()
    time.sleep(delay)  # uprzejme opóźnienie między requestami
    return BeautifulSoup(resp.text, "html.parser")


# ---------------------------
# Lista + paginacja
# ---------------------------
def parse_list_page(soup: BeautifulSoup, base_url: str) -> Tuple[List[str], Optional[str], str]:
    # kategoria: breadcrumbs
    cat = soup.select_one("ul.breadcrumb li.active")
    category = clean_text(cat.get_text()) if cat else ""

    # linki do produktów
    product_links: List[str] = []
    for a in soup.select("article.product_pod h3 a"):
        href = a.get("href")
        if not href:
            continue
        product_links.append(urljoin(base_url, href))

    # next page
    next_link = soup.select_one("li.next a")
    next_url = urljoin(base_url, next_link["href"]) if next_link and next_link.get("href") else None

    return product_links, next_url, category


# ---------------------------
# Strona produktu -> Book
# ---------------------------
def parse_product_page(soup: BeautifulSoup, product_url: str, category_fallback: str) -> Book:
    title = clean_text(soup.select_one("div.product_main h1").get_text())
    price_val = price_to_float(clean_text(soup.select_one("p.price_color").get_text()))

    rating_tag = soup.select_one("p.star-rating")
    rating_val = rating_to_int(" ".join(rating_tag.get("class", []))) if rating_tag else 0

    availability = clean_text(soup.select_one("p.availability").get_text())

    desc_tag = soup.select_one("#product_description ~ p")
    description = clean_text(desc_tag.get_text()) if desc_tag else ""

    info: Dict[str, str] = {}
    for row in soup.select("table.table.table-striped tr"):
        th = clean_text(row.select_one("th").get_text())
        td = clean_text(row.select_one("td").get_text())
        info[th] = td

    img = soup.select_one("div.item.active img")
    image_url = urljoin(product_url, img.get("src")) if img and img.get("src") else ""

    # kategoria (breadcrumbs: przedostatni element)
    crumbs = [clean_text(x.get_text()) for x in soup.select("ul.breadcrumb li a, ul.breadcrumb li.active")]
    category = crumbs[-2] if len(crumbs) >= 2 else category_fallback

    def getf(key: str) -> float:
        return price_to_float(info.get(key, ""))

    return Book(
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
        image_url=image_url,
    )


# ---------------------------
# Crawl kategorii z limitem stron
# ---------------------------
def crawl_category(session: requests.Session, start_url: str, max_pages: int) -> Iterator[Book]:
    current_url = start_url
    page_no = 1
    while current_url and page_no <= max_pages:
        soup = get_soup(session, current_url)
        product_links, next_url, category = parse_list_page(soup, current_url)

        iterator = product_links if not HAS_TQDM else tqdm(product_links, desc=f"Strona {page_no}", unit="prod")
        for prod_url in iterator:
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
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for b in books:
            w.writerow(asdict(b))


def save_json(books: List[Book], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(b) for b in books], f, ensure_ascii=False, indent=2)


# ---------------------------
# Main
# ---------------------------
def main() -> None:
    session = build_session()
    print(f"Start: {START_CATEGORY} | MAX_PAGES={MAX_PAGES}")
    books: List[Book] = []
    for book in crawl_category(session, START_CATEGORY, MAX_PAGES):
        books.append(book)

    print(f"Pobrano pozycji: {len(books)}")
    save_csv(books, OUTPUT_CSV)
    save_json(books, OUTPUT_JSON)
    print(f"Zapisano: {OUTPUT_CSV}, {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
