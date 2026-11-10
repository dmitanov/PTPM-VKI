import unittest

from src.database import DatabaseRepository
from src.parser import BigGeekParser, DEFAULT_URL, ForumParser


class BigGeekParserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.parser = BigGeekParser()
        cls.html = cls.parser.fetch(DEFAULT_URL)
        cls.products = cls.parser.parse_html(cls.html)

    def test_parse_html_returns_products(self) -> None:
        self.assertGreater(len(self.products), 0)

    def test_parse_html_extracts_required_fields(self) -> None:
        for product in self.products:
            self.assertIsInstance(product["id"], int)
            self.assertTrue(product["name"])
            self.assertTrue(product["price"])
            self.assertIn("₽", product["price"])
            self.assertEqual(product["message"], product["price"])
            self.assertTrue(product["url"].startswith("https://biggeek.ru/"))

    def test_parse_html_ids_are_unique(self) -> None:
        ids = [product["id"] for product in self.products]
        self.assertEqual(len(ids), len(set(ids)))

    def test_parse_page_loads_live_site(self) -> None:
        products = self.parser.parse_page(DEFAULT_URL)
        self.assertGreater(len(products), 0)
        live_ids = {product["id"] for product in products}
        cached_ids = {product["id"] for product in self.products}
        self.assertEqual(live_ids, cached_ids)

    def test_save_to_db_stores_parsed_products(self) -> None:
        repo = DatabaseRepository(":memory:")
        self.addCleanup(repo.close)

        saved = self.parser.save_to_db(self.products, repo)

        self.assertEqual(saved, len(self.products))
        self.assertEqual(len(repo.get_all()), len(self.products))
        first = repo.get_by_id(self.products[0]["id"])
        self.assertEqual(first["name"], self.products[0]["name"])
        self.assertEqual(first["message"], self.products[0]["price"])

    def test_forum_parser_alias_points_to_biggeek_parser(self) -> None:
        self.assertIs(ForumParser, BigGeekParser)


if __name__ == "__main__":
    unittest.main()
