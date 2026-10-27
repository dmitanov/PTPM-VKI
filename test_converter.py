import unittest
from converter import Converter

class ConverterTests(unittest.TestCase):

    # ---------- x >= 100.7 -> 1000 ----------
    def test_upper_boundary_exact(self):
        self.assertEqual(Converter.do(100.7), 1000)

    def test_above_upper_boundary(self):
        self.assertEqual(Converter.do(100.8), 1000)

    def test_large_positive(self):
        self.assertEqual(Converter.do(99999.9), 1000)

    # ---------- (0; 100.7) -> int(x) ----------
    def test_just_below_upper_boundary(self):
        self.assertEqual(Converter.do(100.6), 100)

    def test_regular_positive(self):
        self.assertEqual(Converter.do(65.7), 65)

    def test_positive_integer_value(self):
        self.assertEqual(Converter.do(50.0), 50)

    def test_smallest_positive(self):
        self.assertEqual(Converter.do(0.1), 0)

    def test_positive_one(self):
        self.assertEqual(Converter.do(1.0), 1)

    def test_positive_truncates_not_rounds(self):
        self.assertEqual(Converter.do(9.9), 9)

    # ---------- x == 0 -> ValueError ----------
    def test_zero_raises(self):
        with self.assertRaises(ValueError):
            Converter.do(0.0)

    def test_negative_zero_raises(self):
        with self.assertRaises(ValueError):
            Converter.do(-0.0)

    # ---------- [-30.4; 0) -> int(x) - 5 ----------
    def test_closest_negative_to_zero(self):
        self.assertEqual(Converter.do(-0.1), -5)

    def test_negative_minus_one(self):
        self.assertEqual(Converter.do(-1.0), -6)

    def test_regular_negative(self):
        self.assertEqual(Converter.do(-15.5), -20)

    def test_negative_truncates_toward_zero(self):
        self.assertEqual(Converter.do(-9.9), -14)

    def test_lower_boundary_of_middle_range(self):
        self.assertEqual(Converter.do(-30.4), -35)

    def test_negative_30_exact(self):
        self.assertEqual(Converter.do(-30.0), -35)

    # ---------- x <= -30.5 -> -2000 ----------
    def test_lower_boundary_exact(self):
        self.assertEqual(Converter.do(-30.5), -2000)

    def test_below_lower_boundary(self):
        self.assertEqual(Converter.do(-30.6), -2000)

    def test_large_negative(self):
        self.assertEqual(Converter.do(-94.5), -2000)

    def test_very_large_negative(self):
        self.assertEqual(Converter.do(-99999.9), -2000)

    # ---------- return type ----------
    def test_return_type_is_int(self):
        for value in (150.0, 5.5, -5.5, -50.0):
            self.assertIsInstance(Converter.do(value), int)


if __name__ == "__main__":
    unittest.main()