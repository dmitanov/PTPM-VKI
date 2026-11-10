import unittest
from pathlib import Path
from unittest.mock import patch

from src.database import DatabaseRepository
from src.parser import BigGeekParser, DEFAULT_URL, ForumParser

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "biggeek_page.html"


class BigGeekParserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = FIXTURE_PATH.read_text(encoding="utf-8")

    def setUp(self) -> None:
        self.parser = BigGeekParser()
        self.products = self.parser.parse_html(self.html)

    def test_parse_html_returns_all_products(self) -> None:
        self.assertEqual(len(self.products), 3)
        self.assertEqual(
            {product["id"] for product in self.products},
            {37079, 35679, 35678},
        )

    def test_parse_html_extracts_name_price_and_id(self) -> None:
        first = self.products[0]
        self.assertEqual(first["id"], 37079)
        self.assertIn("MacBook Neo 13", first["name"])
        self.assertEqual(first["price"], "68 990 ₽")
        self.assertEqual(first["message"], first["price"])

    def test_parse_html_ignores_old_price(self) -> None:
        first = self.products[0]
        self.assertNotIn("75 990", first["price"])
        self.assertEqual(self.products[1]["price"], "311 990 ₽")

    def test_parse_html_builds_absolute_url(self) -> None:
        first = self.products[0]
        self.assertEqual(
            first["url"],
            "https://biggeek.ru/products/noutbuk-apple-macbook-neo-13-mhfa4",
        )

    def test_parse_page_uses_fetched_html(self) -> None:
        with patch.object(self.parser, "fetch", return_value=self.html) as fetch:
            products = self.parser.parse_page(DEFAULT_URL)
        fetch.assert_called_once_with(DEFAULT_URL)
        self.assertEqual(len(products), 3)

    def test_save_to_db_stores_parsed_products(self) -> None:
        repo = DatabaseRepository(":memory:")
        self.addCleanup(repo.close)

        saved = self.parser.save_to_db(self.products, repo)

        self.assertEqual(saved, 3)
        self.assertEqual(len(repo.get_all()), 3)
        first = repo.get_by_id(37079)
        self.assertIn("MacBook Neo 13", first["name"])
        self.assertEqual(first["message"], "68 990 ₽")

    def test_forum_parser_alias_points_to_biggeek_parser(self) -> None:
        self.assertIs(ForumParser, BigGeekParser)


if __name__ == "__main__":
    unittest.main()
