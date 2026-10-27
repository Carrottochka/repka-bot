import unittest

from bot.guide import SECTIONS, all_lessons, lesson_by_id, section_by_id


class GuideCatalogTest(unittest.TestCase):
    def test_ids_are_unique_and_callback_safe(self) -> None:
        seen: set[str] = set()
        for lesson in all_lessons():
            self.assertNotIn(lesson.id, seen)
            seen.add(lesson.id)
            self.assertLessEqual(len(f"gl:{lesson.id}"), 64)
            self.assertTrue(lesson.body.strip())
            self.assertLessEqual(len(lesson.body), 3500)
        for section in SECTIONS:
            self.assertLessEqual(len(f"gs:{section.id}"), 64)
            self.assertIsNotNone(section_by_id(section.id))

    def test_seed_lessons_cover_requested_actions(self) -> None:
        seeds = section_by_id("seeds")
        self.assertIsNotNone(seeds)
        assert seeds is not None
        ids = {lesson.id for lesson in seeds.lessons}
        for lesson_id in (
            "seeds_create",
            "seeds_edit",
            "seeds_copy",
            "seeds_collect",
            "seeds_delete",
            "seeds_filters",
            "seeds_bulk",
        ):
            self.assertIn(lesson_id, ids)
            self.assertIsNotNone(lesson_by_id(lesson_id))


if __name__ == "__main__":
    unittest.main()
