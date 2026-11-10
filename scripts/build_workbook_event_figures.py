"""Reproducible diagrams and numerical conservation checks for workbook Q1–Q3."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


OUT = Path(__file__).resolve().parents[1] / "assets"
OUT.mkdir(exist_ok=True)
NAVY = "#253f60"
BLUE = "#254b73"
TEAL = "#16878c"
ORANGE = "#c47b43"
RED = "#af5b5b"
PURPLE = "#8064a2"
GREY = "#8b99a9"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#bccbd8",
    "text.color": NAVY,
    "axes.labelcolor": NAVY,
    "xtick.color": GREY,
    "ytick.color": GREY,
    "savefig.facecolor": "white",
    "figure.facecolor": "white",
    "svg.fonttype": "none",
})


CASES = {
    "single": {
        "title": "Q1 | one machine, FCFS",
        "h": 10,
        "customer": [
            ("A", 0, [("M1 service", 0, 3, BLUE)], 3),
            ("B", 1, [("M1 wait", 1, 3, ORANGE), ("M1 service", 3, 5, BLUE)], 5),
            ("C", 4, [("M1 wait", 4, 5, ORANGE), ("M1 service", 5, 9, BLUE)], 9),
            ("D", 4, [("M1 wait", 4, 9, ORANGE), ("M1 service", 9, 10, BLUE)], 10),
        ],
        "times": [0, 1, 3, 4, 5, 9, 10],
        "states": [
            ("Q(t), waiting only", [0, 1, 0, 2, 1, 0, 0], ORANGE, 8),
            ("M1 busy", [1, 1, 1, 1, 1, 1, 0], BLUE, 10),
        ],
    },
    "parallel": {
        "title": "Q2 | M1-priority parallel servers, shared FCFS",
        "h": 7,
        "customer": [
            ("A", 0, [("M1 service", 0, 4, BLUE)], 4),
            ("B", 1, [("M2 service", 1, 4, TEAL)], 4),
            ("C", 2, [("Queue", 2, 4, ORANGE), ("M1 service", 4, 6, BLUE)], 6),
            ("D", 3, [("Queue", 3, 4, ORANGE), ("M2 service", 4, 5, TEAL)], 5),
            ("E", 4, [("Queue", 4, 5, ORANGE), ("M2 service", 5, 7, TEAL)], 7),
        ],
        "times": [0, 1, 2, 3, 4, 5, 6, 7],
        "states": [
            ("Queue Q(t), waiting only", [0, 0, 1, 2, 1, 0, 0, 0], ORANGE, 4),
            ("M1 busy", [1, 1, 1, 1, 1, 1, 0, 0], BLUE, 6),
            ("M2 busy", [0, 1, 1, 1, 1, 1, 1, 0], TEAL, 6),
        ],
    },
    "tandem": {
        "title": "Q3 | M1 - transit - M2, separate FCFS queues",
        "h": 11,
        "customer": [
            ("A", 0, [("M1 service", 0, 2, BLUE), ("Transit", 2, 3, PURPLE),
                       ("M2 service", 3, 6, TEAL)], 6),
            ("B", 1, [("M1 wait", 1, 2, ORANGE), ("M1 service", 2, 3, BLUE),
                       ("Transit", 3, 4, PURPLE), ("M2 wait", 4, 6, RED),
                       ("M2 service", 6, 8, TEAL)], 8),
            ("C", 2, [("M1 wait", 2, 3, ORANGE), ("M1 service", 3, 5, BLUE),
                       ("Transit", 5, 6, PURPLE), ("M2 wait", 6, 8, RED),
                       ("M2 service", 8, 9, TEAL)], 9),
            ("D", 4, [("M1 wait", 4, 5, ORANGE), ("M1 service", 5, 6, BLUE),
                       ("Transit", 6, 7, PURPLE), ("M2 wait", 7, 9, RED),
                       ("M2 service", 9, 11, TEAL)], 11),
        ],
        "times": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11],
        "states": [
            ("M1 waiting Q1(t)", [0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0], ORANGE, 3),
            ("M2 waiting Q2(t)", [0, 0, 0, 0, 1, 1, 1, 2, 1, 0, 0], RED, 6),
            ("M1 busy", [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0], BLUE, 6),
            ("M2 busy", [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0], TEAL, 8),
            ("In transit", [0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0], PURPLE, 4),
        ],
    },
}


def save(fig, name):
    fig.savefig(OUT / name, format="svg", bbox_inches="tight", pad_inches=.24)
    plt.close(fig)


def plot_customers(key, data):
    from matplotlib.patches import Patch

    tasks = data["customer"]
    h = data["h"]
    fig, ax = plt.subplots(figsize=(12.1, 4.7 if key != "parallel" else 5.2),
                           constrained_layout=True)
    palette = []
    for i, (name, arrival, stages, departure) in enumerate(tasks):
        y = len(tasks)-i
        for phase, start, end, color in stages:
            ax.broken_barh([(start, end-start)], (y-.26, .52), facecolor=color)
            if end-start >= 1.55:
                ax.text((start+end)/2, y, str(end-start), fontsize=11,
                        ha="center", va="center", color="white", weight="bold")
            palette.append((phase, color))
        waited = sum(end-start for phase, start, end, _ in stages if "wait" in phase.lower() or phase == "Queue")
        ax.text(h+.17, y, f"Wq={waited:g} | T={departure-arrival:g}",
                color=NAVY, va="center", fontsize=10)
    distinct = dict(palette)
    legend = [Patch(color=color, label=phase) for phase, color in distinct.items()]
    ax.legend(handles=legend, loc="upper left", bbox_to_anchor=(0, 1.05),
              frameon=False, ncol=len(legend), fontsize=9.7)
    ax.set(xlim=(-.2,h+3), ylim=(.35,len(tasks)+.7),
           yticks=range(1,len(tasks)+1),
           yticklabels=[name for name, _, _, _ in reversed(tasks)],
           xticks=range(h+1), xlabel="Absolute simulation time")
    fig.suptitle(data["title"] + " | per-customer lifecycle",
                 fontsize=14.2, fontweight="bold")
    ax.grid(axis="x", alpha=.15)
    save(fig, f"workbook-q{['single','parallel','tandem'].index(key)+1}-customer-timeline.svg")


def plot_states(key, data):
    times = np.array(data["times"])
    states = data["states"]
    fig, axes = plt.subplots(len(states), 1, figsize=(11.5, len(states)*1.92+1.1),
                             sharex=True, constrained_layout=True)
    for ax, (label, values, color, expected_area) in zip(axes, states):
        area = sum((r-l)*value for l, r, value in zip(times[:-1],times[1:],values[:-1]))
        assert area == expected_area, (key, label, area, expected_area)
        ax.step(times, values, where="post", color=color, lw=2.6)
        ax.fill_between(times, values, step="post", color=color, alpha=.11)
        ax.set(xlim=(0,data["h"]), ylim=(-.12, 2.35 if max(values)>1 else 1.25),
               yticks=[0,1,2] if max(values)>1 else [0,1], ylabel=label)
        ax.text(data["h"]-.1, max(values)+.1, f"Area = {area}", color=color,
                ha="right", va="bottom", fontsize=11, fontweight="bold")
        ax.grid(axis="both", alpha=.14)
    axes[-1].set(xticks=data["times"], xlabel="Absolute simulation time")
    fig.suptitle(data["title"] + " | exact queue-area and utilization plots",
                 fontsize=15.4, fontweight="bold")
    save(fig, f"workbook-q{['single','parallel','tandem'].index(key)+1}-queue-busy.svg")


def verify_conservation(key, data):
    h = data["h"]
    customers = data["customer"]
    waits = sum(sum(end-start for phase,start,end,_ in stages
                    if phase == "Queue" or "wait" in phase.lower())
                for _, _, stages, _ in customers)
    sojourn = sum(departure-arrival for _,arrival,_,departure in customers)
    all_service = sum(end-start for _,_,stages,_ in customers
                      for phase,start,end,_ in stages if "service" in phase.lower())
    transit = sum(end-start for _,_,stages,_ in customers
                  for phase,start,end,_ in stages if phase == "Transit")
    area_queue = sum(expected for label,_,_,expected in data["states"]
                     if "waiting" in label.lower() or "queue" in label.lower())
    busy = sum(expected for label,_,_,expected in data["states"] if "busy" in label.lower())
    assert waits == area_queue, (key, "queue", waits, area_queue)
    assert all_service == busy, (key, "busy", all_service, busy)
    assert sojourn == waits + all_service + transit, (key, "sojourn")
    print(f"{key}: H={h}; total Wq={waits}; total T={sojourn}; "
          f"queue area={area_queue}; busy area={busy}; transit area={transit}")


if __name__ == "__main__":
    for name, case in CASES.items():
        verify_conservation(name, case)
        plot_customers(name, case)
        plot_states(name, case)
    print("Created six exact workbook figures for Q1, Q2 and Q3.")
