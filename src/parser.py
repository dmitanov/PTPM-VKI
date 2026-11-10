"""Парсер страниц форума на основе requests и BeautifulSoup."""

from __future__ import annotations

import re
from typing import Iterable, Optional

import requests
from bs4 import BeautifulSoup, FeatureNotFound

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}

POST_SELECTORS = (
    "article.post",
    "div.post",
    "li.post",
    "article.message",
    "div.message",
    "li.message",
    "div.comment",
    "li.comment",
)

AUTHOR_SELECTORS = (
    ".post-author",
    ".message-author",
    ".author",
    ".username",
    ".user-name",
    ".login",
    "[data-author]",
)

MESSAGE_SELECTORS = (
    ".message-body",
    ".post-message",
    ".message-content",
    ".post-content",
    ".message-text",
    ".content",
    ".body",
)

ID_ATTRIBUTES = ("data-post-id", "data-comment-id", "data-message-id", "data-id")
ID_PATTERN = re.compile(r"^(?:post|comment|message)?[-_]?(\d+)$", re.IGNORECASE)


class ForumParseError(RuntimeError):
    """Ошибка загрузки или разбора страницы форума."""


class ForumParser:
    """Извлекает ID, автора и текст сообщений со страницы форума."""

    def __init__(
        self,
        headers: Optional[dict] = None,
        timeout: int = 15,
        session: Optional[requests.Session] = None,
        parser: str = "lxml",
    ) -> None:
        self.headers = {**DEFAULT_HEADERS, **(headers or {})}
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update(self.headers)
        self.parser = parser

    def fetch(self, url: str) -> str:
        """Скачивает HTML-страницу с передачей заголовков."""
        try:
            response = self.session.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ForumParseError(f"Не удалось загрузить {url}: {exc}") from exc

        if not response.encoding or response.encoding.lower() == "iso-8859-1":
            response.encoding = response.apparent_encoding
        return response.text

    def parse_page(self, url: str) -> list[dict]:
        """Скачивает страницу по URL и возвращает список сообщений."""
        return self.parse_html(self.fetch(url))

    def parse_html(self, html: str) -> list[dict]:
        """Разбирает готовый HTML (удобно для тестов на фикстурах)."""
        soup = self._make_soup(html)
        posts = []
        for node in self._find_post_containers(soup):
            post = self._parse_post(node)
            if post is not None:
                posts.append(post)
        return posts

    def _make_soup(self, html: str) -> BeautifulSoup:
        try:
            return BeautifulSoup(html, self.parser)
        except FeatureNotFound:
            return BeautifulSoup(html, "html.parser")

    def _find_post_containers(self, soup: BeautifulSoup) -> Iterable:
        seen = set()
        for selector in POST_SELECTORS:
            for node in soup.select(selector):
                if id(node) not in seen:
                    seen.add(id(node))
                    yield node

    def _parse_post(self, node) -> Optional[dict]:
        comment_id = self._extract_id(node)
        name = self._extract_author(node)
        message = self._extract_message(node)

        if comment_id is None or name is None or message is None:
            return None
        return {"id": comment_id, "name": name, "message": message}

    def _extract_id(self, node) -> Optional[int]:
        for attribute in ID_ATTRIBUTES:
            value = node.get(attribute)
            if value and str(value).strip().isdigit():
                return int(str(value).strip())

        for attribute in ("id", "name"):
            value = node.get(attribute)
            if not value:
                continue
            match = ID_PATTERN.match(str(value).strip())
            if match:
                return int(match.group(1))

        link = node.find("a", href=True)
        if link is not None:
            match = ID_PATTERN.match(str(link["href"]).strip().lstrip("#"))
            if match:
                return int(match.group(1))
        return None

    def _extract_author(self, node) -> Optional[str]:
        for selector in AUTHOR_SELECTORS:
            element = node.select_one(selector)
            if element is None:
                continue
            if element.has_attr("data-author"):
                value = element.get("data-author", "")
            else:
                value = element.get_text(strip=True)
            if value:
                return value

        author = node.get("data-author")
        if author and str(author).strip():
            return str(author).strip()
        return None

    def _extract_message(self, node) -> Optional[str]:
        for selector in MESSAGE_SELECTORS:
            element = node.select_one(selector)
            if element is None:
                continue
            message = element.decode_contents().strip()
            if message:
                return message
        return None

    def save_to_db(self, parsed_data: Iterable[dict], repository) -> int:
        """Сохраняет разобранные сообщения через DatabaseRepository."""
        saved = 0
        for post in parsed_data:
            repository.add(post["id"], post["name"], post["message"])
            saved += 1
        return saved
