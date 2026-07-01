from __future__ import annotations

from mlbotnav.stress_backtest_contour import _parse_json_tail, _parse_profiles


def test_parse_profiles_default():
    got = _parse_profiles("")
    assert got == [("base", 5.0), ("stress_1", 10.0), ("stress_2", 15.0)]


def test_parse_profiles_named():
    got = _parse_profiles("base:5,stress_1:10,stress_2:15")
    assert got == [("base", 5.0), ("stress_1", 10.0), ("stress_2", 15.0)]


def test_parse_profiles_unnamed_values():
    got = _parse_profiles("5,10,15")
    assert got == [("base", 5.0), ("stress_1", 10.0), ("stress_2", 15.0)]


def test_parse_json_tail_uses_last_json_object():
    raw = "\n".join(
        [
            "log line",
            '{"status":"PASS","report_path":"x"}',
            "",
        ]
    )
    got = _parse_json_tail(raw)
    assert isinstance(got, dict)
    assert got["status"] == "PASS"
