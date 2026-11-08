"""Every name the user sees says Hestia: the former name lives in engine/legacy.py and the socle's copies only."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
# The socle's copies (hestia-ecosysteme/socle) read the shared panel's former address from engine/legacy.py.
ALLOWED = {"engine/legacy.py", "socle.py", "domain_migration.py"}
SKIP = {"node_modules", ".git", ".venv", "__pycache__"}


class Names(unittest.TestCase):
    def test_the_former_name_is_nowhere_else(self):
        for path in ROOT.rglob("*"):
            if not path.is_file() or SKIP & set(path.parts) or path.suffix in (".ttf", ".woff2", ".gz", ".png"):
                continue
            relative = path.relative_to(ROOT).as_posix()
            if any(relative.endswith(name) for name in ALLOWED) or relative == "tests/test_names.py":
                continue
            self.assertNotIn("niak", path.read_text(encoding="utf-8", errors="ignore").lower(), relative)


class PrivateData(unittest.TestCase):
    def test_the_real_home_data_cannot_be_committed(self):
        # The replay reads hestia-energie/donnees-test from outside the repository; never a copy inside.
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for rule in ("donnees-test/", "*.csv", "*.csv.gz"):
            self.assertIn(rule, ignored)


if __name__ == "__main__":
    unittest.main()
