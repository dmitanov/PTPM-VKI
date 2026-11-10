"""Парсер каталога ноутбуков Apple на сайте biggeek.ru."""

from __future__ import annotations

from typing import Iterable, Optional

import requests
from bs4 import BeautifulSoup, FeatureNotFound

DEFAULT_URL = "https://biggeek.ru/catalog/noutbuki-apple"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}

CARD_CLASS = "catalog-card"
TITLE_CLASS = "catalog-card__title"
PRICE_CLASS = "catalog-card__price"
CURRENT_PRICE_CLASS = "cart-modal-count"


class ForumParseError(RuntimeError):
    """Ошибка загрузки или разбора страницы каталога."""


class BigGeekParser:
    """Извлекает ID, название и цену товаров из карточек BigGeek."""

    def __init__(
        self,
        headers: Optional[dict] = None,
        timeout: int = 30,
        session: Optional[requests.Session] = None,
        parser: str = "lxml",
    ) -> None:
        self.headers = {**DEFAULT_HEADERS, **(headers or {})}
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update(self.headers)
        self.parser = parser

    def fetch(self, url: str = DEFAULT_URL) -> str:
        """Скачивает HTML-страницу каталога с передачей заголовков."""
        try:
            response = self.session.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ForumParseError(f"Не удалось загрузить {url}: {exc}") from exc

        if not response.encoding or response.encoding.lower() == "iso-8859-1":
            response.encoding = response.apparent_encoding
        return response.text

    def parse_page(self, url: str = DEFAULT_URL) -> list[dict]:
        """Скачивает страницу по URL и возвращает список товаров."""
        return self.parse_html(self.fetch(url))

    def parse_html(self, html: str) -> list[dict]:
        """Разбирает готовый HTML каталога (удобно для отладки)."""
        soup = self._make_soup(html)
        products = []
        for card in soup.find_all("div", class_=CARD_CLASS):
            product = self._parse_card(card)
            if product is not None:
                products.append(product)
        return products

    def _make_soup(self, html: str) -> BeautifulSoup:
        try:
            return BeautifulSoup(html, self.parser)
        except FeatureNotFound:
            return BeautifulSoup(html, "html.parser")

    def _parse_card(self, card) -> Optional[dict]:
        title_tag = card.find("a", class_=TITLE_CLASS)
        price_tag = card.find("a", class_=PRICE_CLASS)
        if title_tag is None or price_tag is None:
            return None

        name = title_tag.get_text(" ", strip=True)
        price_tag = price_tag.find("b", class_=CURRENT_PRICE_CLASS) or price_tag
        price = price_tag.get_text(" ", strip=True)

        comment_id = self._extract_id(card)
        if comment_id is None or not name or not price:
            return None

        href = title_tag.get("href")
        url = f"https://biggeek.ru{href}" if href and href.startswith("/") else href

        return {
            "id": comment_id,
            "name": name,
            "price": price,
            "message": price,
            "url": url,
        }

    @staticmethod
    def _extract_id(card) -> Optional[int]:
        id_tag = card.select_one("[data-product-id]")
        if id_tag is None:
            return None

        value = str(id_tag.get("data-product-id", "")).strip()
        return int(value) if value.isdigit() else None

    def save_to_db(self, parsed_data: Iterable[dict], repository) -> int:
        """Сохраняет товары в БД: name — название, message — цена."""
        saved = 0
        for product in parsed_data:
            price = product.get("price", product.get("message", ""))
            repository.add(product["id"], product["name"], price)
            saved += 1
        return saved


ForumParser = BigGeekParser
