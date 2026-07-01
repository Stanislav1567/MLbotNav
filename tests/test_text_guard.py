from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mlbotnav.text_guard import file_scan, iter_targets


class TextGuardTests(unittest.TestCase):
    def test_clean_russian_text_has_zero_mojibake_score(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "clean.md"
            p.write_text("Привет, это нормальный UTF-8 текст.", encoding="utf-8")
            row = file_scan(p)
            self.assertTrue(row["utf8_ok"])
            self.assertEqual(row["mojibake_score"], 0)

    def test_mojibake_like_pairs_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "broken.md"
            # Typical mojibake pairs seen when cp1251 bytes are mis-rendered in UTF-8 text.
            p.write_text("\u0420\u045e\u0420\u2014 \u0420\u00b4\u0420\u00b0\u0421\u201a\u0420\u00b0", encoding="utf-8")
            row = file_scan(p)
            self.assertTrue(row["utf8_ok"])
            self.assertGreater(row["mojibake_score"], 0)

    def test_iter_targets_includes_root_text_files_and_deduplicates(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs").mkdir(parents=True, exist_ok=True)
            (root / "tests").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "a.md").write_text("ok", encoding="utf-8")
            (root / "tests" / "t_case.py").write_text("x=1\n", encoding="utf-8")
            (root / "ROOT_NOTE.md").write_text("ok", encoding="utf-8")
            (root / "root_script.py").write_text("print('ok')", encoding="utf-8")
            (root / "root_cfg.yaml").write_text("k: v\n", encoding="utf-8")
            (root / "root_cfg2.yml").write_text("k2: v2\n", encoding="utf-8")
            (root / "root_data.json").write_text("{\"k\":1}", encoding="utf-8")
            (root / "run_sample.ps1").write_text("Write-Host ok", encoding="utf-8")
            (root / "requirements.txt").write_text("pandas==2.2.2", encoding="utf-8")
            paths = list(iter_targets(root))
            resolved = [str(p.resolve()) for p in paths]
            self.assertIn(str((root / "ROOT_NOTE.md").resolve()), resolved)
            self.assertIn(str((root / "root_script.py").resolve()), resolved)
            self.assertIn(str((root / "root_cfg.yaml").resolve()), resolved)
            self.assertIn(str((root / "root_cfg2.yml").resolve()), resolved)
            self.assertIn(str((root / "root_data.json").resolve()), resolved)
            self.assertIn(str((root / "tests" / "t_case.py").resolve()), resolved)
            self.assertIn(str((root / "run_sample.ps1").resolve()), resolved)
            self.assertIn(str((root / "requirements.txt").resolve()), resolved)
            self.assertEqual(len(resolved), len(set(resolved)))


if __name__ == "__main__":
    unittest.main()

