"""Four reproducible statistical diagrams for the final-exam output drill."""

from pathlib import Path
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import t

ASSETS = Path(__file__).resolve().parents[1] / "assets"
ASSETS.mkdir(exist_ok=True)
NAVY = "#223954"
TEAL = "#17898a"
ORANGE = "#be7342"
BLUE = "#3b6f9f"
GREY = "#758499"
COLORS = [BLUE, TEAL, ORANGE]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#b8c7d1", "text.color": NAVY,
    "axes.labelcolor": NAVY, "xtick.color": GREY,
    "ytick.color": GREY, "svg.fonttype": "none",
})


def output(fig, filename):
    fig.savefig(ASSETS / filename, format="svg", bbox_inches="tight", pad_inches=.22)
    plt.close(fig)


DATA = np.array([[2, 4, 6, 8], [4, 5, 6, 5], [6, 8, 10, 12]])
MEANS = DATA.mean(axis=1)


def data_plot():
    fig, ax = plt.subplots(figsize=(11, 5.4), constrained_layout=True)
    for i, row in enumerate(DATA):
        k = np.arange(1, 5)
        ax.plot(k, row, "-o", lw=2.2, color=COLORS[i],
                ms=8, label=f"Run {i+1} | run mean={MEANS[i]:.1f}")
        ax.hlines(MEANS[i], 1, 4, colors=COLORS[i], linestyles="dotted", lw=1.5)
    ax.set(xlabel="Observation index within one run (not independent replications)",
           ylabel="Observed waiting-time output", xticks=[1, 2, 3, 4], ylim=(1, 13),
           title="Three independent runs | four internally dependent observations per run")
    ax.grid(axis="y", alpha=.2)
    ax.legend(frameon=False, loc="upper left")
    ax.text(4.08, 11.6, "Run means: 5, 5, 9", color=NAVY, fontsize=11,
            fontweight="bold", va="center")
    ax.set_xlim(.85, 5.4)
    output(fig, "exam-output-replication-data.svg")


def ci_plot():
    mu = MEANS.mean()
    s = MEANS.std(ddof=1)
    h_correct = t.ppf(.975, 2)*s/np.sqrt(3)
    naive = DATA.ravel()
    h_naive = t.ppf(.975, 11)*naive.std(ddof=1)/np.sqrt(12)
    fig, ax = plt.subplots(figsize=(11, 4.5), constrained_layout=True)
    for y, h, color, label in [(2, h_correct, TEAL, "Correct: 3 run means; df=2"),
                               (1, h_naive, ORANGE, "Invalid: pool all 12; df=11")]:
        ax.plot([mu-h, mu+h], [y, y], color=color, lw=4, solid_capstyle="round")
        ax.scatter([mu], [y], color=color, s=85, zorder=5)
        ax.vlines([mu-h, mu+h], y-.16, y+.16, color=color, lw=2.3)
        ax.text(mu+h+.22, y, f"half-width = {h:.3f}", va="center",
                color=color, fontweight="bold", fontsize=10.5)
    ax.axvline(mu, color="#b4beca", ls="--", lw=1.2)
    ax.set(yticks=[1, 2], yticklabels=["Incorrect pooling", "Independent-run means"],
           xlabel="Estimated mean and 95% CI", xlim=(0, 14.7), ylim=(.5, 2.5),
           title="Same overall mean, very different uncertainty estimates")
    ax.grid(axis="x", alpha=.16)
    ax.text(.35, .63, "Only run means supply 3 independent statistical units.",
            color=GREY, fontsize=10)
    output(fig, "exam-output-replication-ci-contrast.svg")


def width(n, s, alpha=.05):
    return t.ppf(1-alpha/2, n-1)*s/np.sqrt(n)


def trial_plot():
    r = np.arange(6, 47)
    fig, ax = plt.subplots(figsize=(11.5, 5.3), constrained_layout=True)
    ax.plot(r, width(r, 1.2), color=BLUE, lw=2.6, label="Pilot SD=1.20 (planning)")
    ax.plot(r, width(r, 1.32), color=ORANGE, lw=2.6,
            label="Re-estimated SD=1.32 (illustrative)")
    ax.axhline(.5, color=GREY, lw=1.6, linestyle="--", label="Required half-width <= 0.50")
    for n, s, color, xytext in [
        (25, 1.2, BLUE, (12.5, .73)),
        (30, 1.32, ORANGE, (33, .76)),
    ]:
        y = width(n, s)
        ax.scatter([n], [y], color=color, s=74, zorder=5)
        ax.annotate(f"n={n}, h={y:.4f}", (n, y), xytext=xytext,
                    color=color, fontweight="bold",
                    arrowprops={"arrowstyle": "-", "color": color})
    ax.set(xlabel="Total independent runs n", ylabel="Predicted CI half-width h(n)",
           xlim=(6, 46), ylim=(.25, 1.45),
           title="Trial-count search | update the SD, then assess precision again")
    ax.grid(axis="y", alpha=.20)
    ax.legend(frameon=False, loc="upper right")
    output(fig, "exam-output-precision-sd-update.svg")


def target_plot():
    r = np.arange(6, 55)
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.7), constrained_layout=True)
    for ax, target, nstar, subtitle in [
        (axs[0], .5, 25, "Absolute tolerance = 0.50"),
        (axs[1], .4, 38, "Relative 5% of pilot mean 8 = 0.40"),
    ]:
        ax.plot(r, width(r, 1.2), lw=2.7, color=BLUE)
        ax.axhline(target, ls="--", lw=1.8, color=ORANGE)
        ax.scatter([nstar], [width(nstar, 1.2)], color=TEAL, s=70, zorder=4)
        ax.text(nstar+.8, target+.1, f"first feasible n={nstar}", color=TEAL,
                fontweight="bold", fontsize=10)
        ax.scatter([nstar-1], [width(nstar-1, 1.2)], color=ORANGE, s=55, zorder=4)
        ax.set(xlim=(6, 54), ylim=(.25, 1.34), xlabel="Total runs n",
               ylabel="95% CI half-width", title=subtitle)
        ax.grid(axis="y", alpha=.18)
    fig.suptitle("Precision wording changes the required replication count",
                 fontsize=15.2, color=NAVY, fontweight="bold")
    output(fig, "exam-output-absolute-relative-target.svg")


if __name__ == "__main__":
    data_plot()
    ci_plot()
    trial_plot()
    target_plot()
    for fn in ["exam-output-replication-data.svg", "exam-output-replication-ci-contrast.svg",
               "exam-output-precision-sd-update.svg", "exam-output-absolute-relative-target.svg"]:
        print(ASSETS / fn)
