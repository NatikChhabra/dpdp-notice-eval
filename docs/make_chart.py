"""Draw docs/checks-chart.png from the stored leaderboard (no API calls).

pip install matplotlib
python docs/make_chart.py
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
BOARD = ROOT / "results" / "leaderboard-gemini-3.5-flash-lite.json"
OUT = ROOT / "docs" / "checks-chart.png"

LABELS = {
    "data_itemised": "Lists the personal data",
    "purpose_specific": "States specific purposes",
    "contact": "Contact for questions",
    "no_foreign_law": "No GDPR-only ideas",
    "grievance": "Grievance route, reply ≤ 90 days",
    "rights": "How to access, correct, erase",
    "withdraw_consent": "How to withdraw consent",
    "children": "Children's data handled right",
    "board_complaint": "How to complain to the Board",
    "nomination": "Right to nominate",
    "language": "Offered in an Indian language",
}

PLAIN, LAW = "#eb6834", "#2a78d6"  # categorical slots 2 and 1
INK, MUTED, GRID = "#1f1f1e", "#6b6a63", "#e6e5df"


def mean_per_check(rows, condition):
    # Only models with the full core set, so a partly run model doesn't skew the average.
    rows = [r for r in rows if r["condition"] == condition and r["n"] >= 12]
    return {k: sum(r["per_check"][k] for r in rows) / len(rows) for k in LABELS}


def main():
    core = json.loads(BOARD.read_text())["core"]
    plain = mean_per_check(core, "plain")
    law = mean_per_check(core, "dpdp_open")
    order = sorted(LABELS, key=lambda k: (law[k], plain[k]))

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=200)
    fig.patch.set_facecolor("white")
    ys = range(len(order))
    for y, k in enumerate(order):
        ax.plot([plain[k] * 100, law[k] * 100], [y, y], color=GRID, lw=3, zorder=1, solid_capstyle="round")
    ax.scatter(
        [plain[k] * 100 for k in order],
        ys,
        s=70,
        color=PLAIN,
        zorder=3,
        edgecolor="white",
        linewidth=2,
        label="Plain request (law not named)",
    )
    ax.scatter(
        [law[k] * 100 for k in order],
        ys,
        s=70,
        color=LAW,
        zorder=4,
        edgecolor="white",
        linewidth=2,
        label="Request names the DPDP Act and Rules",
    )
    for y, k in enumerate(order):
        v = law[k] * 100
        ax.text(v + 2.4, y, f"{v:.0f}%", va="center", ha="left", color=INK, fontsize=10, fontweight="bold")

    ax.set_yticks(list(ys), [LABELS[k] for k in order], color=INK)
    ax.set_xlim(-3, 112)
    ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"], color=MUTED)
    ax.xaxis.grid(True, color=GRID, lw=1)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    ax.set_title(
        "Share of notices that pass each legal check", loc="left", color=INK, fontsize=14, fontweight="bold", pad=34
    )
    ax.text(
        0,
        1.035,
        "Average of 4 models, 12 businesses each. Labels show the law-named result.",
        transform=ax.transAxes,
        color=MUTED,
        fontsize=10.5,
    )
    ax.legend(loc="lower right", frameon=False, fontsize=10, labelcolor=INK)
    fig.tight_layout()
    fig.savefig(OUT, facecolor="white")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
