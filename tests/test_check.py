import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import agents_md_check as checker


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, text, name="AGENTS.md"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def codes(self, threshold=32768):
        return [item["code"] for item in checker.scan(self.root, threshold)[1]]

    def test_clean_and_nested_files(self):
        self.write("# Project\nRun tests before publishing.\n")
        self.write("# Subproject\nKeep changes scoped.\n", "sub/AGENTS.md")
        files, issues, incomplete = checker.scan(self.root, 32768)
        self.assertEqual(files, ["AGENTS.md", "sub/AGENTS.md"])
        self.assertEqual(issues, [])
        self.assertFalse(incomplete)

    def test_find_conflicts_duplicates_and_invisible_controls(self):
        self.write("<<<<<<< HEAD\nAn instruction that is intentionally long enough.\nAn instruction that is intentionally long enough.\nA\u202eB\n=======\n>>>>>>> branch\n")
        self.assertEqual(self.codes().count("merge_marker"), 3)
        self.assertIn("duplicate_line", self.codes())
        self.assertIn("bidi_control", self.codes())

    def test_repeated_code_block_is_not_counted(self):
        line = "This instruction is intentionally long enough to repeat."
        self.write(f"```text\n{line}\n{line}\n```\n")
        self.assertNotIn("duplicate_line", self.codes())

    def test_empty_invalid_utf8_and_size(self):
        self.write("")
        self.assertIn("empty", self.codes())
        (self.root / "AGENTS.md").write_bytes(b"\xff")
        self.assertIn("encoding", self.codes())
        self.write("long enough\n")
        self.assertIn("size", self.codes(4))

    def test_excludes_dependencies_and_does_not_follow_symlinks(self):
        self.write("", "node_modules/example/AGENTS.md")
        with tempfile.TemporaryDirectory() as other:
            (Path(other) / "AGENTS.md").write_text("", encoding="utf-8")
            (self.root / "linked").symlink_to(other, target_is_directory=True)
            files, issues, _ = checker.scan(self.root, 32768)
        self.assertEqual(files, [])
        self.assertEqual(issues, [])

    def test_skips_file_symlink(self):
        with tempfile.TemporaryDirectory() as other:
            target = Path(other) / "instructions"
            target.write_text("secret content", encoding="utf-8")
            (self.root / "AGENTS.md").symlink_to(target)
            self.assertIn("symlink", self.codes())

    def test_json_and_exit_status(self):
        self.write("\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = checker.main([str(self.root), "--json"])
        report = json.loads(out.getvalue())
        self.assertEqual(code, 1)
        self.assertEqual(report["schema_version"], 1)
        self.assertFalse(report["incomplete"])
        self.assertNotIn("content", report)

    def test_over_one_mib_is_not_read(self):
        (self.root / "AGENTS.md").write_bytes(b"x" * (checker.MAX_READ + 1))
        self.assertIn("read_limit", self.codes())
        self.assertTrue(checker.scan(self.root, 32768)[2])


if __name__ == "__main__":
    unittest.main()
