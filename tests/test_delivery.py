"""
Лабораторная работа №2 — юнит-тесты для модуля расчёта доставки (src/delivery_service.py).

Бизнес-требования восстановлены по контексту исходного кода и документации метода:
  1. Допустимый вес: 0.1..50.0 кг, допустимое расстояние: 1..5000 км.
  2. Допустимые типы посылки: «обычный», «хрупкий», «опасный».
  3. Базовая стоимость 200 руб. + 5 руб. за каждый километр.
  4. Весовой коэффициент: 1.2 для веса строго между 5 и 20 кг; 1.5 для веса от 20 кг.
  5. Надбавка за тип: +300 руб. («хрупкий»), +1000 руб. («опасный»).
  6. Экспресс-доставка — платная услуга ускорения, поэтому она удорожает, а не удешевляет.
  7. Срок доставки в днях: distance // 500, но не менее 1 дня; экспресс сокращает срок вдвое,
     но доставка не может произойти в день отправки (минимум 1 день).
  8. Дата отправки фиксирована: 2026-09-03.
  9. Метод возвращает целое число рублей, округлённое по правилам арифметики,
     и дату в формате YYYY-MM-DD.
 10. На любые некорректные параметры метод возвращает (-1, "0000-00-00"), а не падает с исключением.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from delivery_service import calculate_delivery_cost

SENTINEL_INVALID = (-1, "0000-00-00")


class TestDeliveryValidation(unittest.TestCase):
    """Проверка границ физических ограничений и типов входных параметров."""

    def test_rejects_weight_below_minimum_allowed(self):
        """Вес 0.05 кг меньше минимально допустимых 0.1 кг — посылка не принимается."""
        self.assertEqual(
            calculate_delivery_cost(0.05, 100, "обычный"),
            SENTINEL_INVALID
        )

    def test_accepts_weight_at_lower_boundary(self):
        """Вес ровно 0.1 кг — нижняя граница допустимого диапазона, посылка принимается."""
        self.assertEqual(
            calculate_delivery_cost(0.1, 100, "обычный"),
            (700, "2026-09-04")
        )

    def test_accepts_weight_at_upper_boundary(self):
        """Вес ровно 50.0 кг — верхняя граница диапазона, посылка принимается."""
        self.assertEqual(
            calculate_delivery_cost(50.0, 100, "обычный"),
            (1050, "2026-09-04")
        )

    def test_rejects_weight_above_maximum_allowed(self):
        """Вес 50.1 кг превышает максимум — посылка не принимается."""
        self.assertEqual(
            calculate_delivery_cost(50.1, 100, "обычный"),
            SENTINEL_INVALID
        )

    def test_rejects_distance_below_minimum_allowed(self):
        """Расстояние 0 км меньше минимально допустимого 1 км."""
        self.assertEqual(
            calculate_delivery_cost(1.0, 0, "обычный"),
            SENTINEL_INVALID
        )

    def test_accepts_distance_at_lower_boundary(self):
        """Расстояние ровно 1 км — нижняя граница диапазона, посылка принимается."""
        self.assertEqual(
            calculate_delivery_cost(1.0, 1, "обычный"),
            (205, "2026-09-04")
        )

    def test_accepts_distance_at_upper_boundary(self):
        """Расстояние ровно 5000 км — верхняя граница диапазона, посылка принимается."""
        self.assertEqual(
            calculate_delivery_cost(1.0, 5000, "обычный"),
            (25200, "2026-09-13")
        )

    def test_rejects_distance_above_maximum_allowed(self):
        """Расстояние 5001 км превышает максимум."""
        self.assertEqual(
            calculate_delivery_cost(1.0, 5001, "обычный"),
            SENTINEL_INVALID
        )

    def test_rejects_unknown_package_type(self):
        """Тип посылки «срочный» отсутствует в списке допустимых."""
        self.assertEqual(
            calculate_delivery_cost(5.0, 100, "срочный"),
            SENTINEL_INVALID
        )

    def test_rejects_empty_package_type(self):
        """Пустая строка вместо типа посылки не совпадает ни с одним допустимым значением."""
        self.assertEqual(
            calculate_delivery_cost(5.0, 100, ""),
            SENTINEL_INVALID
        )

    def test_rejects_package_type_with_wrong_letter_case(self):
        """Регистр значения важен: «Обычный» не равен «обычный»."""
        self.assertEqual(
            calculate_delivery_cost(5.0, 100, "Обычный"),
            SENTINEL_INVALID
        )

    def test_rejects_none_package_type(self):
        """Значение None вместо типа посылки должно отклоняться, а не обрабатываться как «обычный»."""
        self.assertEqual(
            calculate_delivery_cost(5.0, 100, None),
            SENTINEL_INVALID
        )

    def test_rejects_non_numeric_weight_without_raising_exception(self):
        """
        Строковый вес — некорректный параметр. По документации метод обязан вернуть
        (-1, "0000-00-00"), а не возбуждать TypeError при сравнении строки с числом.
        """
        try:
            result = calculate_delivery_cost("десять", 100, "обычный")
        except TypeError as error:
            self.fail(
                f"Метод упал с TypeError ({error}) вместо возврата "
                f"{SENTINEL_INVALID} на некорректный тип веса"
            )
        self.assertEqual(result, SENTINEL_INVALID)

    def test_rejects_non_numeric_distance_without_raising_exception(self):
        """
        Строковое расстояние — некорректный параметр. Ожидается штатный отказ,
        а не необработанное исключение.
        """
        try:
            result = calculate_delivery_cost(5.0, "сто", "обычный")
        except TypeError as error:
            self.fail(
                f"Метод упал с TypeError ({error}) вместо возврата "
                f"{SENTINEL_INVALID} на некорректный тип расстояния"
            )
        self.assertEqual(result, SENTINEL_INVALID)


class TestDeliveryTariffCalculation(unittest.TestCase):
    """Проверка расчёта стоимости по базовому тарифу, весовым коэффициентам и надбавкам."""

    def test_calculates_base_cost_for_light_small_parcel(self):
        """200 руб. базовых + 5 руб./км: при 0.5 кг и 100 км итог 700 руб."""
        self.assertEqual(
            calculate_delivery_cost(0.5, 100, "обычный"),
            (700, "2026-09-04")
        )

    def test_charges_five_rubles_per_kilometer(self):
        """Тариф за километры: 200 + 1000*5 = 5200 руб. при 1000 км."""
        self.assertEqual(
            calculate_delivery_cost(1.0, 1000, "обычный"),
            (5200, "2026-09-05")
        )

    def test_does_not_apply_weight_coefficient_at_five_kg_boundary(self):
        """Ровно 5 кг — верхняя граница базового тарифа без коэффициента."""
        self.assertEqual(
            calculate_delivery_cost(5.0, 100, "обычный"),
            (700, "2026-09-04")
        )

    def test_applies_twenty_percent_coefficient_above_five_kg(self):
        """При 6 кг применяется коэффициент 1.2: 700 * 1.2 = 840 руб."""
        self.assertEqual(
            calculate_delivery_cost(6.0, 100, "обычный"),
            (840, "2026-09-04")
        )

    def test_applies_fifty_percent_coefficient_at_twenty_kg_boundary(self):
        """Ровно 20 кг попадает в ветку коэффициента 1.5: 700 * 1.5 = 1050 руб."""
        self.assertEqual(
            calculate_delivery_cost(20.0, 100, "обычный"),
            (1050, "2026-09-04")
        )

    def test_applies_fifty_percent_coefficient_for_heavy_parcel(self):
        """При 30 кг и 1000 км: 5200 * 1.5 = 7800 руб."""
        self.assertEqual(
            calculate_delivery_cost(30.0, 1000, "обычный"),
            (7800, "2026-09-05")
        )

    def test_adds_three_hundred_rubles_for_fragile_package(self):
        """Надбавка за хрупкую посылку: 700 + 300 = 1000 руб."""
        self.assertEqual(
            calculate_delivery_cost(5.0, 100, "хрупкий"),
            (1000, "2026-09-04")
        )

    def test_adds_one_thousand_rubles_for_hazardous_package(self):
        """Надбавка за опасную посылку: 700 + 1000 = 1700 руб."""
        self.assertEqual(
            calculate_delivery_cost(5.0, 100, "опасный"),
            (1700, "2026-09-04")
        )

    def test_combines_heavy_weight_coefficient_and_hazardous_surcharge(self):
        """Совместное применение коэффициента 1.5 и надбавки 1000: 5200*1.5 + 1000 = 8800 руб."""
        self.assertEqual(
            calculate_delivery_cost(25.0, 1000, "опасный"),
            (8800, "2026-09-05")
        )

    def test_calculates_maximum_cost_for_heaviest_farthest_hazardous_parcel(self):
        """Предельный случай: 50 кг, 5000 км, опасный — 25200*1.5 + 1000 = 38800 руб."""
        self.assertEqual(
            calculate_delivery_cost(50.0, 5000, "опасный"),
            (38800, "2026-09-13")
        )

    def test_rounds_half_ruble_cost_to_nearest_ruble(self):
        """
        25 кг и 101 км дают 200 + 505 = 705 руб., 705 * 1.5 = 1057.5 руб.
        Округление должно идти по правилам арифметики и давать 1058 руб.
        """
        self.assertEqual(
            calculate_delivery_cost(25.0, 101, "обычный")[0],
            1058
        )

    def test_keeps_cost_whole_when_even_distance_gives_exact_half_ruble(self):
        """При чётном расстоялении 705.0 округление не меняет результат: 1050 руб."""
        self.assertEqual(
            calculate_delivery_cost(25.0, 100, "обычный")[0],
            1050
        )


class TestExpressDelivery(unittest.TestCase):
    """Проверка того, что экспресс-доставка ускоряет, но не удешевляет доставку."""

    def test_charges_more_for_express_than_for_standard_delivery(self):
        """
        Экспресс — платная услуга. Для 10 кг и 1000 км обычная доставка стоит
        5200 * 1.2 = 6240 руб., экспресс должен стоить 6240 * 1.5 = 9360 руб.
        """
        self.assertEqual(
            calculate_delivery_cost(10.0, 1000, "обычный", is_express=True)[0],
            9360
        )

    def test_applies_express_surcharge_to_fragile_package(self):
        """
        Для 2 кг и 2000 км хрупкой посылки базовая стоимость 200 + 10000 + 300 = 10500 руб.
        Экспресс должен дать 10500 * 1.5 = 15750 руб.
        """
        self.assertEqual(
            calculate_delivery_cost(2.0, 2000, "хрупкий", is_express=True)[0],
            15750
        )

    def test_halves_shipping_time_for_long_distance_express_delivery(self):
        """При 5000 км срок 10 дней сокращается экспрессом до 5 дней: 2026-09-08."""
        self.assertEqual(
            calculate_delivery_cost(1.0, 5000, "обычный", is_express=True)[1],
            "2026-09-08"
        )

    def test_does_not_schedule_short_express_delivery_on_the_day_of_shipping(self):
        """
        При 100 км обычный срок равен 1 дню, экспресс не может дать 0 дней,
        иначе посылка «доставляется» в день отправки. Ожидается 2026-09-04.
        """
        self.assertEqual(
            calculate_delivery_cost(0.5, 100, "обычный", is_express=True)[1],
            "2026-09-04"
        )

    def test_does_not_schedule_near_express_delivery_on_the_day_of_shipping(self):
        """
        При 600 км срок также равен 1 дню (600 // 500 = 1), экспресс не должен
        обнулять его. Ожидается 2026-09-04.
        """
        self.assertEqual(
            calculate_delivery_cost(10.0, 600, "обычный", is_express=True)[1],
            "2026-09-04"
        )


class TestDeliveryScheduling(unittest.TestCase):
    """Проверка расчёта даты доставки для обычной отправки."""

    def test_schedules_standard_delivery_on_the_next_day(self):
        """Дата отправки 2026-09-03, минимальный срок 1 день — доставка 2026-09-04."""
        self.assertEqual(
            calculate_delivery_cost(0.5, 100, "обычный")[1],
            "2026-09-04"
        )

    def test_schedules_standard_delivery_in_five_hundred_km_steps(self):
        """При 1500 км срок равен 3 дням: 2026-09-06."""
        self.assertEqual(
            calculate_delivery_cost(1.0, 1500, "обычный")[1],
            "2026-09-06"
        )


class TestDeliveryReturnValue(unittest.TestCase):
    """Проверка формы возвращаемого значения."""

    def test_returns_integer_cost_and_string_date(self):
        """Метод возвращает кортеж из целого числа и строки даты в формате YYYY-MM-DD."""
        result = calculate_delivery_cost(5.0, 100, "обычный")

        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], int)
        self.assertIsInstance(result[1], str)

    def test_returns_date_in_iso_format(self):
        """Дата доставки всегда имеет вид YYYY-MM-DD."""
        self.assertRegex(
            calculate_delivery_cost(5.0, 100, "обычный")[1],
            r"^\d{4}-\d{2}-\d{2}$"
        )


if __name__ == "__main__":
    unittest.main()
