"""Reproducible, exact figures for the three 2026 simulation mock exams."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t as student_t


OUT = Path(__file__).resolve().parents[1] / "assets"
OUT.mkdir(exist_ok=True)
NAVY = "#203854"
ORANGE = "#bd7642"
BLUE = "#28476a"
TEAL = "#16868a"
GREY = "#8190a3"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#bfcbd4",
    "text.color": NAVY,
    "axes.labelcolor": NAVY,
    "xtick.color": GREY,
    "ytick.color": GREY,
    "svg.fonttype": "none",
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})


def save(fig, name):
    fig.savefig(OUT / name, format="svg", bbox_inches="tight", pad_inches=.25)
    plt.close(fig)


def a_lifecycle():
    # Arrival, first-service start, departure, assigned machine.
    tasks = [
        ("A", 0, 0, 3, "M1"),
        ("B", 1, 1, 5, "M2"),
        ("C", 1, 3, 5, "M1"),
        ("D", 3, 5, 7, "M1"),
        ("E", 4, 5, 6, "M2"),
    ]
    fig, ax = plt.subplots(figsize=(11, 5.1), constrained_layout=True)
    for i, (name, arr, start, end, machine) in enumerate(tasks):
        y = len(tasks) - i
        if start > arr:
            ax.broken_barh([(arr, start-arr)], (y-.25, .5), facecolors=ORANGE)
            ax.text((arr+start)/2, y, f"W={start-arr}", color="white", fontsize=10,
                    ha="center", va="center", fontweight="bold")
        col = BLUE if machine == "M1" else TEAL
        ax.broken_barh([(start, end-start)], (y-.25, .5), facecolors=col)
        ax.text((start+end)/2, y, f"{machine}: {end-start}", ha="center",
                va="center", color="white", fontweight="bold", fontsize=10)
        ax.text(7.16, y, f"Wq={start-arr} | T={end-arr}", va="center",
                fontsize=10, color=NAVY)
    ax.set(xlim=(-.2, 9.65), ylim=(.5, 5.65),
           yticks=np.arange(1, 6), yticklabels=["E", "D", "C", "B", "A"],
           xticks=np.arange(0, 8), xlabel="Absolute simulation time",
           title="Mock A | per-customer waiting, service and total sojourn")
    ax.grid(axis="x", alpha=.16)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=ORANGE, label="Queue wait"),
                       Patch(color=BLUE, label="M1 service"),
                       Patch(color=TEAL, label="M2 service")],
              loc="upper right", bbox_to_anchor=(.95, 1.03), ncol=3, frameon=False)
    save(fig, "exam-mock-a-customer-timing.svg")


def a_states():
    fig, axs = plt.subplots(3, 1, figsize=(11, 8), sharex=True, constrained_layout=True)
    times = np.array([0, 1, 3, 4, 5, 6, 7])
    curves = [
        ([0, 1, 1, 2, 0, 0, 0], "Queue length Q(t) | waiting only", ORANGE, 2.35),
        ([1, 1, 1, 1, 1, 1, 0], "M1 busy B1(t)", BLUE, 1.35),
        ([0, 1, 1, 1, 1, 0, 0], "M2 busy B2(t)", TEAL, 1.35),
    ]
    for ax, (val, lab, col, high) in zip(axs, curves):
        ax.step(times, val, where="post", color=col, lw=2.8)
        ax.fill_between(times, val, step="post", alpha=.12, color=col)
        ax.set(ylim=(-.1, high), yticks=[0, 1, 2] if high > 2 else [0, 1],
               ylabel=lab)
        ax.grid(axis="both", alpha=.15)
        ax.set_xlim(0, 7)
    axs[0].text(6.85, 2.10, "Queue area = 5", color=ORANGE,
                fontsize=11, ha="right", fontweight="bold")
    axs[1].text(6.85, 1.14, "Busy area M1 = 7", color=BLUE,
                fontsize=11, ha="right", fontweight="bold")
    axs[2].text(6.85, 1.14, "Busy area M2 = 5", color=TEAL,
                fontsize=11, ha="right", fontweight="bold")
    axs[2].set(xlabel="Absolute simulation time", xticks=range(8))
    fig.suptitle("Mock A | queue-area and machine utilization checks",
                 fontsize=16, fontweight="bold")
    save(fig, "exam-mock-a-queue-utilization.svg")


def b_output():
    means = np.array([5., 7., 6., 9.])
    avg = means.mean()
    sd = means.std(ddof=1)
    half = student_t.ppf(.975, 3) * sd / np.sqrt(4)
    n = np.arange(4, 49)
    h = student_t.ppf(.975, n-1) * sd / np.sqrt(n)
    h_updated = student_t.ppf(.975, n-1) * 1.9 / np.sqrt(n)
    fig, axs = plt.subplots(1, 2, figsize=(12.7, 4.8), constrained_layout=True)
    ax = axs[0]
    for i, x in enumerate(means):
        ax.scatter([i+1], [x], color=TEAL, s=65)
        ax.text(i+1+.08, x+.15, f"Run {i+1}: {x:g}", color=TEAL, fontsize=9)
    ax.axhline(avg, color=BLUE, lw=2, linestyle="--")
    ax.axhspan(avg-half, avg+half, color=BLUE, alpha=.10)
    ax.text(.75, avg+half+.36, f"95% CI [{avg-half:.3f}, {avg+half:.3f}]",
            fontsize=10, color=BLUE, fontweight="bold")
    ax.set(title="A. Independent-run means and confidence interval",
           xlabel="Replication index", ylabel="Run-mean waiting time",
           xlim=(.65, 4.7), ylim=(3, 11), xticks=[1, 2, 3, 4])
    ax.grid(axis="y", alpha=.18)
    ax = axs[1]
    ax.plot(n, h, color=BLUE, lw=2.7, label=f"Pilot SD={sd:.4f}")
    ax.plot(n, h_updated, color=ORANGE, lw=2.4,
            label="After n=26, updated SD=1.90")
    ax.axhline(.70, color=GREY, ls="--", lw=1.5, label="Target half-width <=0.70")
    ax.scatter([25, 26, 30, 31], [h[25-4], h[26-4], h_updated[30-4], h_updated[31-4]],
               color=[ORANGE, TEAL, ORANGE, TEAL], s=62, zorder=5)
    ax.annotate("n=25 fails", (25,h[25-4]), xytext=(12,1.13), color=ORANGE,
                arrowprops={"arrowstyle": "-", "color": ORANGE})
    ax.annotate("n=26 passes", (26,h[26-4]), xytext=(27,1.05), color=BLUE,
                arrowprops={"arrowstyle": "-", "color": BLUE})
    ax.annotate("updated n=31", (31,h_updated[31-4]), xytext=(32,.87), color=ORANGE,
                arrowprops={"arrowstyle": "-", "color": ORANGE})
    ax.set(title="B. Minimum planned replications by t-trials", xlabel="Total replications n",
           ylabel="Predicted 95% CI half-width", xlim=(4, 48), ylim=(.4, 2.1))
    ax.grid(axis="y", alpha=.18)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    fig.suptitle("Mock B | correct confidence interval and successive trial search",
                 fontsize=15.6, fontweight="bold")
    save(fig, "exam-mock-b-confidence-trial.svg")


def c_generator():
    m, a, c, seed = 3900, 1561, 11, 17
    values = []
    x = seed
    for _ in range(10):
        x = (a*x+c) % m
        values.append(x)
    fig, ax = plt.subplots(figsize=(11, 4.7), constrained_layout=True)
    n = np.arange(1, 11)
    ax.vlines(n, 0, values, color=BLUE, lw=3)
    ax.scatter(n, values, s=78, color=TEAL, zorder=4)
    for i, (k, state) in enumerate(zip(n, values)):
        ax.text(k, state+(155 if i % 2==0 else 120), str(state), ha="center",
                va="bottom", color=NAVY, fontsize=10, fontweight="bold")
    ax.axhline(m, color=ORANGE, linestyle="--", lw=1.5)
    ax.text(9.85, m-160, "m=3900", color=ORANGE, ha="right", fontsize=10)
    ax.set(xlim=(.45, 10.55), ylim=(0, 4450), xticks=range(1, 11),
           xlabel="Output index n", ylabel="Integer state X(n)",
           title="Mock C | first ten states (a=1561, c=11, seed=17)")
    ax.grid(axis="y", alpha=.16)
    save(fig, "exam-mock-c-lcg-ten-states.svg")


if __name__ == "__main__":
    a_lifecycle()
    a_states()
    b_output()
    c_generator()
    print("Generated four exam-mock figures")
