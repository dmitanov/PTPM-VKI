import unittest

from src.database import (
    CommentNotFoundError,
    DatabaseRepository,
    DuplicateIdError,
    ValidationError,
)


class DatabaseRepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = DatabaseRepository(":memory:")

    def tearDown(self) -> None:
        self.repo.close()

    def test_add_success(self) -> None:
        self.assertTrue(self.repo.add(1, "alice", "Привет"))
        self.assertEqual(
            self.repo.get_by_id(1),
            {"id": 1, "name": "alice", "message": "Привет"},
        )

    def test_add_duplicate_id_raises(self) -> None:
        self.repo.add(1, "alice", "Привет")
        with self.assertRaises(DuplicateIdError):
            self.repo.add(1, "bob", "Другой текст")

    def test_add_invalid_types_raises(self) -> None:
        with self.assertRaises(ValidationError):
            self.repo.add("1", "alice", "Привет")
        with self.assertRaises(ValidationError):
            self.repo.add(1, 123, "Привет")
        with self.assertRaises(ValidationError):
            self.repo.add(1, "alice", None)

    def test_add_too_long_fields_raises(self) -> None:
        with self.assertRaises(ValidationError):
            self.repo.add(1, "a" * 257, "Привет")
        with self.assertRaises(ValidationError):
            self.repo.add(1, "alice", "x" * 8097)

    def test_get_by_id_existing(self) -> None:
        self.repo.add(5, "bob", "<b>Текст</b>")
        row = self.repo.get_by_id(5)
        self.assertIsNotNone(row)
        self.assertEqual(row["name"], "bob")
        self.assertEqual(row["message"], "<b>Текст</b>")

    def test_get_by_id_missing_returns_none(self) -> None:
        self.assertIsNone(self.repo.get_by_id(999))

    def test_get_by_name_returns_list(self) -> None:
        self.repo.add(1, "alice", "Первый")
        self.repo.add(2, "alice", "Второй")
        self.repo.add(3, "bob", "Чужой")

        rows = self.repo.get_by_name("alice")
        self.assertEqual(len(rows), 2)
        self.assertEqual([row["id"] for row in rows], [1, 2])
        self.assertTrue(all(row["name"] == "alice" for row in rows))

    def test_get_by_name_unknown_returns_empty_list(self) -> None:
        self.assertEqual(self.repo.get_by_name("nobody"), [])

    def test_update_success(self) -> None:
        self.repo.add(1, "alice", "Старый текст")
        self.assertTrue(self.repo.update(1, "Новый текст"))
        self.assertEqual(self.repo.get_by_id(1)["message"], "Новый текст")

    def test_update_missing_raises(self) -> None:
        with self.assertRaises(CommentNotFoundError):
            self.repo.update(42, "Новый текст")

    def test_update_too_long_message_raises(self) -> None:
        self.repo.add(1, "alice", "Текст")
        with self.assertRaises(ValidationError):
            self.repo.update(1, "x" * 8097)

    def test_delete_success(self) -> None:
        self.repo.add(1, "alice", "Текст")
        self.assertTrue(self.repo.delete(1))
        self.assertIsNone(self.repo.get_by_id(1))

    def test_delete_missing_raises(self) -> None:
        with self.assertRaises(CommentNotFoundError):
            self.repo.delete(42)


if __name__ == "__main__":
    unittest.main()
