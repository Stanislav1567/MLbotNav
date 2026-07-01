from __future__ import annotations

import os
import re
import subprocess
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class CpuBudgetResult:
    waited_sec: float
    last_cpu_pct: float | None
    checks: int
    timed_out: bool


@dataclass(frozen=True)
class CpuWindowStats:
    avg_pct: float | None
    max_pct: float | None
    min_pct: float | None
    samples: int
    duration_sec: float


def _read_total_cpu_pct_windows() -> float | None:
    # Windows host counter read; returns None if unavailable.
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        "(Get-Counter '\\Processor(_Total)\\% Processor Time').CounterSamples[0].CookedValue",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    text = (proc.stdout or "").strip()
    if not text:
        return None
    # Normalize decimal separators.
    text = text.replace(",", ".")
    m = re.search(r"[-+]?\d+(\.\d+)?", text)
    if not m:
        return None
    try:
        return float(m.group(0))
    except Exception:
        return None


def read_total_cpu_pct() -> float | None:
    """Best-effort CPU utilization probe for orchestration logic."""
    return _read_total_cpu_pct_windows()


def sample_cpu_window(*, window_sec: float = 10.0, sample_interval_sec: float = 1.0) -> CpuWindowStats:
    """
    Collect CPU samples for a short window and return aggregate stats.
    Uses best-effort host counter reads; if all reads fail, avg/max/min are None.
    """
    w = max(1.0, float(window_sec))
    dt = min(max(0.2, float(sample_interval_sec)), w)
    vals: list[float] = []
    start = time.time()
    while True:
        v = _read_total_cpu_pct_windows()
        if v is not None:
            vals.append(float(v))
        elapsed = time.time() - start
        if elapsed >= w:
            break
        sleep_left = min(dt, w - elapsed)
        if sleep_left > 0:
            time.sleep(sleep_left)
    if not vals:
        return CpuWindowStats(avg_pct=None, max_pct=None, min_pct=None, samples=0, duration_sec=time.time() - start)
    return CpuWindowStats(
        avg_pct=float(sum(vals) / len(vals)),
        max_pct=float(max(vals)),
        min_pct=float(min(vals)),
        samples=len(vals),
        duration_sec=time.time() - start,
    )


def choose_next_threads(
    *,
    current_threads: int,
    max_threads: int,
    min_threads: int,
    cpu_now_pct: float | None,
    cpu_max_pct: float,
    up_step: int = 1,
    down_step: int = 2,
) -> int:
    """
    Smoothly adjust thread budget to stay below cpu_max_pct.

    Rules:
    - If CPU probe unavailable, gently increase by up_step.
    - If CPU is near/above the ceiling, decrease faster (down_step).
    - If CPU is clearly below target, increase slowly (up_step).
    - Never exceed [min_threads, max_threads].
    """
    lo = max(1, int(min_threads))
    hi = max(lo, int(max_threads))
    cur = min(max(lo, int(current_threads)), hi)
    up = max(1, int(up_step))
    down = max(1, int(down_step))

    if cpu_now_pct is None:
        return min(hi, cur + up)

    cpu = float(cpu_now_pct)
    ceiling = float(cpu_max_pct)
    # Keep a small guard band below hard ceiling to avoid spike overshoots.
    hot = ceiling - 1.0
    mid = ceiling * 0.85
    cool = ceiling * 0.65

    if cpu >= hot:
        return max(lo, cur - down)
    if cpu >= mid:
        return max(lo, cur - 1)
    if cpu <= cool:
        return min(hi, cur + up)
    return cur


def choose_next_threads_sustained(
    *,
    current_threads: int,
    max_threads: int,
    min_threads: int,
    cpu_window_avg_pct: float | None,
    cpu_window_max_pct: float | None,
    cpu_hot_threshold_pct: float = 90.0,
    cpu_cool_threshold_pct: float = 45.0,
    up_step: int = 1,
    down_step: int = 2,
) -> int:
    """
    Thread control that reacts to sustained behavior over a CPU window:
    - sustained hot window => stronger downshift
    - sustained cool window => stronger upshift
    - otherwise fallback to conservative single-sample policy using window average
    """
    lo = max(1, int(min_threads))
    hi = max(lo, int(max_threads))
    cur = min(max(lo, int(current_threads)), hi)
    up = max(1, int(up_step))
    down = max(1, int(down_step))

    if cpu_window_avg_pct is None:
        return min(hi, cur + up)

    avg = float(cpu_window_avg_pct)
    mx = float(cpu_window_max_pct) if cpu_window_max_pct is not None else avg
    hot = float(cpu_hot_threshold_pct)
    cool = float(cpu_cool_threshold_pct)

    if avg >= hot or mx >= hot:
        return max(lo, cur - max(down, 2))
    if avg <= cool:
        return min(hi, cur + max(up, 2))
    return choose_next_threads(
        current_threads=cur,
        max_threads=hi,
        min_threads=lo,
        cpu_now_pct=avg,
        cpu_max_pct=max(hot - 2.0, 1.0),
        up_step=up,
        down_step=down,
    )


def wait_for_cpu_budget(
    *,
    max_cpu_pct: float = 85.0,
    check_interval_sec: float = 5.0,
    max_wait_sec: float = 300.0,
    consecutive_ok: int = 2,
) -> CpuBudgetResult:
    start = time.time()
    checks = 0
    ok = 0
    last = None
    while True:
        checks += 1
        last = _read_total_cpu_pct_windows()
        # If CPU probe unavailable, don't block the workflow.
        if last is None:
            return CpuBudgetResult(waited_sec=time.time() - start, last_cpu_pct=None, checks=checks, timed_out=False)
        if last <= max_cpu_pct:
            ok += 1
            if ok >= consecutive_ok:
                return CpuBudgetResult(waited_sec=time.time() - start, last_cpu_pct=last, checks=checks, timed_out=False)
        else:
            ok = 0
        elapsed = time.time() - start
        if elapsed >= max_wait_sec:
            return CpuBudgetResult(waited_sec=elapsed, last_cpu_pct=last, checks=checks, timed_out=True)
        time.sleep(check_interval_sec)


def apply_thread_limits(env: dict[str, str], *, max_threads: int) -> dict[str, str]:
    out = dict(env)
    val = str(max(1, int(max_threads)))
    # BLAS/OpenMP stacks used by numpy/scipy/sklearn.
    out["OMP_NUM_THREADS"] = val
    out["MKL_NUM_THREADS"] = val
    out["OPENBLAS_NUM_THREADS"] = val
    out["NUMEXPR_NUM_THREADS"] = val
    return out


def default_env_with_limits(*, max_threads: int) -> dict[str, str]:
    env = os.environ.copy()
    return apply_thread_limits(env, max_threads=max_threads)
