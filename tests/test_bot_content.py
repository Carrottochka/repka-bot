import unittest
from datetime import date

from bot.companions import find_neighbors
from bot.lunar import _gregorian_to_julian_day, for_date
from bot.texts import lunar_text, neighbors_text


class LunarCalendarTest(unittest.TestCase):
    def test_julian_day_matches_app_formula(self) -> None:
        self.assertEqual(_gregorian_to_julian_day(2000, 1, 1), 2451545.5)

    def test_today_snapshot_stays_in_range(self) -> None:
        info = for_date(date(2026, 10, 23))
        self.assertIn(info.phase_title, {
            "Новолуние",
            "Растущий серп",
            "Первая четверть",
            "Растущая Луна",
            "Полнолуние",
            "Убывающая Луна",
            "Последняя четверть",
            "Убывающий серп",
        })
        self.assertGreaterEqual(info.illumination_percent, 0)
        self.assertLessEqual(info.illumination_percent, 100)
        self.assertTrue(info.zodiac_sign)
        self.assertIn(info.zodiac_sign, lunar_text(date(2026, 10, 23), info))


class CompanionLookupTest(unittest.TestCase):
    def test_tomato_includes_basil(self) -> None:
        neighbors = find_neighbors("томат")
        self.assertIsNotNone(neighbors)
        assert neighbors is not None
        self.assertIn("базилик", neighbors)

    def test_alias_pomidor(self) -> None:
        neighbors = find_neighbors("помидоры")
        self.assertIsNotNone(neighbors)
        assert neighbors is not None
        self.assertIn("базилик", neighbors)

    def test_reverse_link_for_basil(self) -> None:
        neighbors = find_neighbors("базилик")
        self.assertIsNotNone(neighbors)
        assert neighbors is not None
        self.assertIn("томат", neighbors)

    def test_unknown_culture(self) -> None:
        self.assertIsNone(find_neighbors("баобаб"))
        self.assertIsNone(neighbors_text("баобаб"))

    def test_onion_matches_app_order(self) -> None:
        neighbors = find_neighbors("лук")
        self.assertIsNotNone(neighbors)
        assert neighbors is not None
        self.assertEqual(neighbors[0], "морковь")


if __name__ == "__main__":
    unittest.main()
