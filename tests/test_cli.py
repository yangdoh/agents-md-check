import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "agents_md_check.py"


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, args)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    def test_conflict_example_and_exit_code(self):
        (self.root / "AGENTS.md").write_text("<<<<<<< HEAD\n", encoding="utf-8")
        result = self.run_cli(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stdout,
            "Scanned 1 AGENTS.md file(s); found 1 issue(s).\n"
            "AGENTS.md:1: merge_marker: Possible unresolved merge-conflict marker.\n",
        )
        self.assertEqual(result.stderr, "")

    def test_json_is_machine_readable_and_does_not_include_contents(self):
        (self.root / "AGENTS.md").write_text("secret sample\n", encoding="utf-8")
        result = self.run_cli(self.root, "--json")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["files_scanned"], ["AGENTS.md"])
        self.assertNotIn("secret sample", result.stdout)

    def test_nonexistent_root_fails(self):
        result = self.run_cli(self.root / "missing")
        self.assertEqual(result.returncode, 2)
        self.assertIn("root must be an existing directory", result.stderr)

    def test_zero_limit_fails(self):
        result = self.run_cli(self.root, "--max-bytes", "0")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--max-bytes must be positive", result.stderr)

    def test_oversized_file_reports_incomplete(self):
        (self.root / "AGENTS.md").write_bytes(b"x" * (1024 * 1024 + 1))
        result = self.run_cli(self.root, "--json")
        self.assertEqual(result.returncode, 2)
        report = json.loads(result.stdout)
        self.assertTrue(report["incomplete"])
        self.assertIn("read_limit", [item["code"] for item in report["findings"]])

    def test_require_files_reports_missing_only_when_requested(self):
        default = self.run_cli(self.root, "--json")
        self.assertEqual(default.returncode, 0)
        self.assertEqual(json.loads(default.stdout)["findings"], [])
        required = self.run_cli(self.root, "--json", "--require-files")
        self.assertEqual(required.returncode, 1)
        report = json.loads(required.stdout)
        self.assertEqual(report["files_scanned"], [])
        self.assertEqual(report["findings"][0]["code"], "no_files")
        self.assertFalse(report["incomplete"])

    def test_require_files_accepts_a_clean_file(self):
        (self.root / "AGENTS.md").write_text("# Instructions\n", encoding="utf-8")
        result = self.run_cli(self.root, "--json", "--require-files")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["findings"], [])


if __name__ == "__main__":
    unittest.main()
