"""Простой пример парсинга каталога ноутбуков Apple на biggeek.ru."""

import requests
import bs4

URL = "https://biggeek.ru/catalog/noutbuki-apple"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}


def main() -> None:
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    bs = bs4.BeautifulSoup(response.text, "html.parser")
    all_cards = bs.find_all("div", class_="catalog-card")

    for card in all_cards:
        name_tag = card.find("a", class_="catalog-card__title")
        price_tag = card.find("a", class_="catalog-card__price")
        if name_tag is None or price_tag is None:
            continue

        price_value = price_tag.find("b", class_="cart-modal-count") or price_tag
        name = name_tag.get_text(" ", strip=True)
        price = price_value.get_text(" ", strip=True)
        print(f"{name} - {price}")

    print(f"\nВсего товаров: {len(all_cards)}")


if __name__ == "__main__":
    main()
