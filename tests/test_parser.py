import unittest
from pathlib import Path
from unittest.mock import patch

from src.database import DatabaseRepository
from src.parser import ForumParser

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "forum_page.html"


class ForumParserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = FIXTURE_PATH.read_text(encoding="utf-8")

    def setUp(self) -> None:
        self.parser = ForumParser()
        self.posts = self.parser.parse_html(self.html)

    def test_parse_html_returns_all_posts(self) -> None:
        self.assertEqual(len(self.posts), 3)
        self.assertEqual({post["id"] for post in self.posts}, {101, 102, 103})

    def test_parse_html_extracts_id_author_and_message(self) -> None:
        first = self.posts[0]
        self.assertEqual(first["id"], 101)
        self.assertEqual(first["name"], "alice")
        self.assertIn("Привет", first["message"])
        self.assertIn("<strong>мир</strong>", first["message"])

    def test_parse_html_keeps_inner_markup_and_authors(self) -> None:
        by_id = {post["id"]: post for post in self.posts}
        self.assertEqual(by_id[102]["name"], "bob")
        self.assertIn("<em>пост</em>", by_id[102]["message"])
        self.assertEqual(by_id[103]["name"], "carol")
        self.assertIn('href="https://example.com"', by_id[103]["message"])

    def test_parse_page_uses_fetched_html(self) -> None:
        with patch.object(self.parser, "fetch", return_value=self.html) as fetch:
            posts = self.parser.parse_page("https://forum.example/thread/1")
        fetch.assert_called_once_with("https://forum.example/thread/1")
        self.assertEqual(len(posts), 3)

    def test_save_to_db_stores_parsed_posts(self) -> None:
        repo = DatabaseRepository(":memory:")
        self.addCleanup(repo.close)

        saved = self.parser.save_to_db(self.posts, repo)

        self.assertEqual(saved, 3)
        self.assertEqual(repo.get_by_name("alice")[0]["id"], 101)
        self.assertIsNotNone(repo.get_by_id(102))
        self.assertIsNotNone(repo.get_by_id(103))


if __name__ == "__main__":
    unittest.main()
