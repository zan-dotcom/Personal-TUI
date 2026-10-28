import tempfile
import unittest
from pathlib import Path

from personal_tui.app import apply, load, render, save


class DashboardTests(unittest.TestCase):
    def test_task_and_note_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested/data.json"
            data = load(path)
            apply(data, "add Ship the project")
            apply(data, "done 1")
            apply(data, "note Remember café")
            save(path, data)
            restored = load(path)
            self.assertEqual(restored, data)
            self.assertIn("[x] Ship the project", render(restored))
            apply(restored, "delete 1")
            apply(restored, "unnote 1")
            self.assertEqual(restored, {"tasks": [], "notes": []})

    def test_invalid_commands_do_not_change_data(self):
        data = {"tasks": [], "notes": []}
        for command in ("add", "note", "done 0", "delete -1", "unnote x", "oops"):
            with self.subTest(command=command), self.assertRaises(ValueError):
                apply(data, command)
        self.assertEqual(data, {"tasks": [], "notes": []})

    def test_corrupt_data_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.json"
            original = '{"tasks": [42], "notes": []}'
            path.write_text(original)
            with self.assertRaises(ValueError):
                load(path)
            self.assertEqual(path.read_text(), original)
