import requests
import base64
from bs4 import BeautifulSoup


def fetch_html(url):

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html",
        "Accept-Language": "en-US,en;q=0.9",
    }

    response = requests.get(url, headers=headers, timeout=20)

    return response.text


def image_to_base64(url):

    try:
        res = requests.get(url, timeout=10)

        if res.status_code == 200:
            return base64.b64encode(res.content).decode("utf-8")

    except Exception:
        pass

    return None


def parse_products(html):

    soup = BeautifulSoup(html, "html.parser")

    products = []

    # 🔥 GENERIC SELECTORS
    items = soup.select("div.product, li.product, .product-item")

    for item in items:

        name_tag = item.select_one("h1, h2, h3")
        img_tag = item.select_one("img")

        name = name_tag.get_text(strip=True) if name_tag else ""
        img_url = img_tag["src"] if img_tag else ""

        image_base64 = image_to_base64(img_url) if img_url else None

        if name:
            products.append({
                "name": name,
                "image_base64": image_base64
            })

    return products


def scrape_url(url):

    html = fetch_html(url)

    products = parse_products(html)

    return products