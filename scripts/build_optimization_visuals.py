"""Reproducible precision diagrams for the lecture-08 optimization drills."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

NAVY = "#203852"
BLUE = "#3675a7"
TEAL = "#16868a"
ORANGE = "#bd6939"
GREY = "#68798a"
LITE = "#e6edf2"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10.5,
    "axes.edgecolor": "#c8d2db",
    "axes.labelcolor": NAVY,
    "text.color": NAVY,
    "xtick.color": GREY,
    "ytick.color": GREY,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "svg.fonttype": "none",
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})


def finish(fig, name):
    fig.savefig(ASSETS / name, format="svg", dpi=150, bbox_inches="tight", pad_inches=0.22)
    plt.close(fig)


def cost(x):
    return 16 * x / (1 - .5 * x) + 4 / x


def cost_diagram():
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.6), constrained_layout=True)
    fig.suptitle("M/M/1 service-time optimization | unconstrained vs feasible optimum",
                 fontsize=15.5, fontweight="bold", color=NAVY)
    x = np.linspace(.18, 1.05, 600)
    axs[0].plot(x, cost(x), color=BLUE, lw=2.8)
    axs[0].scatter([.4], [18], color=ORANGE, zorder=4, s=60)
    axs[0].annotate("Global min: x*=0.4, F=18", (.4, 18),
                    xytext=(.48, 25), color=ORANGE, fontweight="bold",
                    arrowprops={"arrowstyle": "-", "color": ORANGE, "lw": 1.2})
    axs[0].set(title="A. Unconstrained stable domain", xlabel="Mean service time x (minutes)",
               ylabel="Cost F(x)", ylim=(16, 48), xlim=(.18, 1.05))
    axs[0].grid(axis="y", alpha=.27)

    x = np.linspace(.6, 1.4, 600)
    axs[1].axvspan(.6, 1.4, color="#e3f0ef", alpha=.8)
    axs[1].plot(x, cost(x), color=TEAL, lw=2.8)
    val = cost(.6)
    axs[1].scatter([.6], [val], color=ORANGE, zorder=4, s=60)
    axs[1].annotate("Feasible min: x=0.6\nF=20.381", (.6, val),
                    xytext=(.79, 34), color=ORANGE, fontweight="bold",
                    arrowprops={"arrowstyle": "-", "color": ORANGE, "lw": 1.2})
    axs[1].set(title="B. Constraint: 0.6 <= x <= 1.4", xlabel="Mean service time x (minutes)",
               ylabel="Cost F(x)", ylim=(18, 82), xlim=(.58, 1.42))
    axs[1].grid(axis="y", alpha=.27)
    finish(fig, "exam-optimization-mm1-cost.svg")


def objective(x, y):
    return (x - 1)**2 + 2 * (y + 2)**2


def pattern_diagram():
    fig, ax = plt.subplots(figsize=(10, 7), constrained_layout=True)
    xx, yy = np.meshgrid(np.linspace(-.8, 2.6, 300), np.linspace(-2.9, 1.3, 300))
    zz = objective(xx, yy)
    levels = [.25, 1, 2, 4, 8, 12, 18]
    cont = ax.contour(xx, yy, zz, levels=levels, colors="#bbcbd8", linewidths=1.3)
    ax.clabel(cont, fmt="%.2g", inline=True, fontsize=9)
    accepted = np.array([[0, 0], [1, 0], [1, -1], [2, -2], [1, -2]])
    ax.plot(accepted[:, 0], accepted[:, 1], "-o", lw=2.6, ms=8,
            color=TEAL, markerfacecolor="white", markeredgewidth=2.2, zorder=4)
    ax.annotate("b1=(0,0), F=9", (0, 0), xytext=(-.7, .55),
                color=NAVY, fontweight="bold", arrowprops={"arrowstyle": "-", "color": GREY})
    ax.annotate("+e1: F=8", (1, 0), xytext=(1.27, .60), color=TEAL, fontweight="bold",
                arrowprops={"arrowstyle": "-", "color": TEAL})
    ax.plot([1, 1], [0, 1], linestyle=":", color=ORANGE, lw=2)
    ax.plot([1], [1], "x", color=ORANGE, ms=10, mew=2.5)
    ax.annotate("+e2 rejected: F=18", (1, 1), xytext=(1.25, .92), color=ORANGE)
    ax.annotate("b2=(1,-1), F=2", (1, -1), xytext=(-.53, -1.1), color=TEAL, fontweight="bold",
                arrowprops={"arrowstyle": "-", "color": TEAL})
    ax.annotate("Pattern point (2,-2), F=1", (2, -2), xytext=(1.29, -2.7),
                color=TEAL, arrowprops={"arrowstyle": "-", "color": TEAL})
    ax.annotate("Optimum (1,-2), F=0", (1, -2), xytext=(-.65, -2.67),
                color=ORANGE, fontweight="bold", arrowprops={"arrowstyle": "-", "color": ORANGE})
    ax.set(xlabel="Decision x1", ylabel="Decision x2", xlim=(-.8, 2.6),
           ylim=(-2.9, 1.3), title="Pattern search | exploratory moves, rejection and pattern move")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=.13)
    finish(fig, "exam-optimization-pattern-search.svg")


def response_diagram():
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.7), constrained_layout=True)
    fig.suptitle("Response surface | fit, locate a candidate, then validate",
                 fontsize=15.5, fontweight="bold")
    x = np.linspace(.4, 3.6, 300)
    y = (x - 2)**2 + 1
    axs[0].plot(x, y, lw=2.8, color=BLUE, label="Fitted quadratic")
    axs[0].scatter([1, 2, 3], [2, 1, 2], color=ORANGE, s=65, zorder=3, label="Design points")
    axs[0].axvline(2, linestyle="--", color=TEAL, lw=1.4)
    axs[0].annotate("Candidate x=2, y=1", (2, 1), xytext=(2.25, 2.6), color=ORANGE,
                    arrowprops={"arrowstyle": "-", "color": ORANGE})
    axs[0].set(title="A. Three observations determine a quadratic",
               xlabel="Controllable x", ylabel="Estimated response y", xlim=(.4, 3.6), ylim=(.7, 3.8))
    axs[0].legend(loc="upper left", frameon=False)
    axs[0].grid(axis="y", alpha=.2)

    xx, yy = np.meshgrid(np.linspace(-1.5, 3.5, 250), np.linspace(-4, .5, 250))
    zz = (xx - 1)**2 + 2*(yy + 2)**2
    c = axs[1].contour(xx, yy, zz, levels=[.5, 2, 4, 8, 12, 18], colors="#9ebbc8")
    axs[1].clabel(c, fontsize=9)
    axs[1].scatter([1], [-2], color=ORANGE, s=75, zorder=4)
    axs[1].annotate("Predicted minimum (1,-2)", (1, -2), xytext=(1.15, -3.1),
                    color=ORANGE, fontweight="bold", arrowprops={"arrowstyle": "-", "color": ORANGE})
    axs[1].set(title="B. Two-factor second-order surface", xlabel="x1", ylabel="x2")
    axs[1].set_aspect("equal", adjustable="box")
    axs[1].grid(alpha=.13)
    finish(fig, "exam-optimization-response-surface.svg")


def gradient_diagram():
    fig, axs = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    fig.suptitle("Central differences vs SPSA | accuracy of one direction and evaluation cost",
                 fontsize=15.2, fontweight="bold")
    ax = axs[0]
    for x, y, label, color, offset in [
        (2, 12, "True gradient / central FD (2,12)", TEAL, (4, 11.4)),
        (-10, 10, "SPSA trial 1 (-10,10)", ORANGE, (-12, 12.5)),
        (14, 14, "SPSA trial 2 (14,14)", BLUE, (5, 16.2)),
    ]:
        ax.annotate("", (x, y), (0, 0), arrowprops={"arrowstyle": "-|>", "lw": 2.4, "color": color})
        ax.scatter([x], [y], color=color, s=55, zorder=4)
        ax.annotate(label, (x, y), xytext=offset, color=color, fontsize=9.8)
    ax.set(xlim=(-13, 19), ylim=(-1, 19), xlabel="Estimated gradient component g1",
           ylabel="Estimated gradient component g2", title="A. Same function, different perturbation estimates")
    ax.axhline(0, color=GREY, lw=.8);ax.axvline(0, color=GREY, lw=.8)
    ax.grid(alpha=.18)

    ax = axs[1]
    k = np.arange(1, 51)
    ax.plot(k, 2*k, color=BLUE, lw=2.8, label="Central FD: 2K")
    ax.plot(k, 0*k+2, color=TEAL, lw=2.8, label="SPSA: 2")
    ax.scatter([20], [40], color=BLUE, s=58, zorder=3)
    ax.scatter([20], [2], color=TEAL, s=58, zorder=3)
    ax.annotate("K=20: 40 evaluations", (20,40), xytext=(25, 56),
                arrowprops={"arrowstyle":"-","color":BLUE}, color=BLUE)
    ax.annotate("K=20: 2 evaluations", (20,2), xytext=(25,18),
                arrowprops={"arrowstyle":"-","color":TEAL}, color=TEAL)
    ax.set(title="B. Evaluations per gradient estimate", xlabel="Number of decision variables K",
           ylabel="Function evaluations per round", xlim=(0, 51), ylim=(0,105))
    ax.grid(axis="y", alpha=.20)
    ax.legend(frameon=False, loc="upper left")
    finish(fig, "exam-optimization-gradient-comparison.svg")


if __name__ == "__main__":
    cost_diagram()
    pattern_diagram()
    response_diagram()
    gradient_diagram()
    for name in ["exam-optimization-mm1-cost.svg", "exam-optimization-pattern-search.svg",
                 "exam-optimization-response-surface.svg", "exam-optimization-gradient-comparison.svg"]:
        print(ASSETS / name)
