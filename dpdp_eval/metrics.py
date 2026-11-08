"""Agreement metrics for judges, and scores with confidence intervals for models."""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Agreement:
    n: int
    accuracy: float
    kappa: float
    fail_precision: float  # of the violations the judge reported, how many were real
    fail_recall: float  # of the real violations, how many the judge caught

    def row(self) -> list[str]:
        return [
            str(self.n),
            f"{self.accuracy:.3f}",
            f"{self.kappa:.3f}",
            f"{self.fail_precision:.3f}",
            f"{self.fail_recall:.3f}",
        ]


def agreement(pairs: list[tuple[str, str]]) -> Agreement:
    """pairs = [(truth, predicted)], each "pass" or "fail". "fail" is the positive class."""
    n = len(pairs)
    if n == 0:
        return Agreement(0, float("nan"), float("nan"), float("nan"), float("nan"))
    tp = sum(t == "fail" and p == "fail" for t, p in pairs)
    fp = sum(t == "pass" and p == "fail" for t, p in pairs)
    fn = sum(t == "fail" and p == "pass" for t, p in pairs)
    acc = sum(t == p for t, p in pairs) / n
    pt = sum(t == "fail" for t, _ in pairs) / n
    pp = sum(p == "fail" for _, p in pairs) / n
    pe = pt * pp + (1 - pt) * (1 - pp)
    kappa = (acc - pe) / (1 - pe) if pe < 1 else 1.0
    prec = tp / (tp + fp) if tp + fp else 1.0
    rec = tp / (tp + fn) if tp + fn else 1.0
    return Agreement(n, acc, kappa, prec, rec)


def per_check(rows: list[tuple[str, str, str]]) -> dict[str, Agreement]:
    """rows = [(check_id, truth, predicted)] -> agreement per check, plus 'ALL'."""
    by: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for cid, t, p in rows:
        by[cid].append((t, p))
        by["ALL"].append((t, p))
    return {k: agreement(v) for k, v in by.items()}


def bootstrap_ci(clusters: dict[str, list[float]], iters: int = 2000, seed: int = 0) -> tuple[float, float, float]:
    """Mean and 95% CI, resampling whole scenarios (clusters) so correlated notices aren't over-counted."""
    keys = sorted(clusters)
    flat = [x for k in keys for x in clusters[k]]
    mean = sum(flat) / len(flat)
    rng = random.Random(seed)
    stats = []
    for _ in range(iters):
        sample = [x for _ in keys for x in clusters[rng.choice(keys)]]
        stats.append(sum(sample) / len(sample))
    stats.sort()
    return mean, stats[int(0.025 * iters)], stats[int(0.975 * iters) - 1]


def md_table(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)
