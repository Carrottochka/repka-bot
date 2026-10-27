import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bot.visitors import allow_stats, record_visit, stats_text

_ZONE = timezone(timedelta(hours=3))


class VisitorCountTest(unittest.TestCase):
    def setUp(self) -> None:
        self._previous = os.environ.get("REPKA_DATA_DIR")
        self._directory = tempfile.TemporaryDirectory()
        os.environ["REPKA_DATA_DIR"] = self._directory.name

    def tearDown(self) -> None:
        if self._previous is None:
            os.environ.pop("REPKA_DATA_DIR", None)
        else:
            os.environ["REPKA_DATA_DIR"] = self._previous
        self._directory.cleanup()

    def test_same_person_is_counted_once(self) -> None:
        first = datetime(2026, 10, 27, 9, 0, tzinfo=_ZONE)
        later = datetime(2026, 10, 28, 12, 0, tzinfo=_ZONE)
        record_visit(10, first)
        record_visit(10, later)
        record_visit(20, later)
        self.assertIn("Всего: 2", stats_text(later.date()))
        self.assertIn("Новых сегодня: 1", stats_text(later.date()))
        self.assertIn("Писали сегодня: 2", stats_text(later.date()))

    def test_first_stats_caller_becomes_owner(self) -> None:
        self.assertTrue(allow_stats(5))
        self.assertTrue(allow_stats(5))
        self.assertFalse(allow_stats(6))
        saved = Path(self._directory.name, "owner.txt").read_text(encoding="utf-8")
        self.assertEqual(saved.strip(), "5")


if __name__ == "__main__":
    unittest.main()
