from __future__ import annotations

import unittest

from sklearn.linear_model import LogisticRegression

from mlbotnav.validation import create_model


class ValidationModelsTests(unittest.TestCase):
    def test_create_logreg(self) -> None:
        m = create_model("logreg")
        self.assertIsInstance(m, LogisticRegression)


if __name__ == "__main__":
    unittest.main()

