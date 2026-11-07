"""Reproduce the five-part FIFO single-machine example with exact decimals.

The original simulation stops at T=15; the second report deliberately
continues to the time when all five parts have departed.

Run from the repository root:
    python examples/single_machine_five_parts_event_simulation.py
"""

from dataclasses import dataclass
from decimal import Decimal


def dec(value: str) -> Decimal:
    return Decimal(value)


@dataclass(frozen=True)
class Part:
    number: int
    arrival: Decimal
    service: Decimal
    start: Decimal
    departure: Decimal

    @property
    def waiting(self) -> Decimal:
        return self.start - self.arrival

    @property
    def sojourn(self) -> Decimal:
        return self.departure - self.arrival


def build_fifo_schedule() -> list[Part]:
    intervals = [dec(v) for v in ("0", "6.84", "2.40", "2.70", "2.59")]
    durations = [dec(v) for v in ("4.58", "2.96", "5.86", "3.21", "3.11")]

    result: list[Part] = []
    arrival = dec("0")
    machine_available = dec("0")

    for i, (interval, service) in enumerate(zip(intervals, durations), 1):
        arrival += interval
        start = max(arrival, machine_available)
        departure = start + service
        result.append(Part(i, arrival, service, start, departure))
        machine_available = departure
    return result


def elapsed_within_window(start: Decimal, end: Decimal, horizon: Decimal) -> Decimal:
    """Length of [start, end) intersected with [0, horizon)."""
    return max(dec("0"), min(end, horizon) - max(start, dec("0")))


def statistics(parts: list[Part], horizon: Decimal) -> dict[str, Decimal | int]:
    arrived = [part for part in parts if part.arrival <= horizon]
    started = [part for part in parts if part.start <= horizon]
    completed = [part for part in parts if part.departure <= horizon]

    queue_area = sum(
        (elapsed_within_window(part.arrival, part.start, horizon) for part in parts),
        dec("0"),
    )
    busy_area = sum(
        (elapsed_within_window(part.start, part.departure, horizon) for part in parts),
        dec("0"),
    )
    occupancy_area = sum(
        (elapsed_within_window(part.arrival, part.departure, horizon) for part in parts),
        dec("0"),
    )

    # One part is either queued or being served, never both.
    assert queue_area + busy_area == occupancy_area
    assert horizon - busy_area >= 0

    return {
        "horizon": horizon,
        "arrived": len(arrived),
        "started": len(started),
        "completed": len(completed),
        "queue_at_horizon": sum(part.arrival <= horizon < part.start for part in parts),
        "busy_at_horizon": sum(part.start <= horizon < part.departure for part in parts),
        "queue_area": queue_area,
        "busy_area": busy_area,
        "occupancy_area": occupancy_area,
        "average_queue": queue_area / horizon,
        "utilization": busy_area / horizon,
        "average_occupancy": occupancy_area / horizon,
        "average_completed_sojourn": (
            sum((part.sojourn for part in completed), dec("0")) / len(completed)
            if completed
            else dec("0")
        ),
        "average_started_wait": (
            sum((part.waiting for part in started), dec("0")) / len(started)
            if started
            else dec("0")
        ),
    }


def display(label: str, values: dict[str, Decimal | int]) -> None:
    print(f"\n{label}")
    print(
        "arrived={arrived}, started={started}, completed={completed}, "
        "queue_now={queue_at_horizon}, machine_busy_now={busy_at_horizon}".format(
            **values
        )
    )
    print(
        "queue_area={queue_area}, busy_area={busy_area}, "
        "occupancy_area={occupancy_area}".format(**values)
    )
    print(
        "mean_queue={:.6f}, utilization={:.6%}, mean_occupancy={:.6f}".format(
            values["average_queue"],
            values["utilization"],
            values["average_occupancy"],
        )
    )
    print(
        "mean_sojourn(completed)={average_completed_sojourn}, "
        "mean_wait(started)={average_started_wait}".format(**values)
    )


def main() -> None:
    parts = build_fifo_schedule()
    print("Part | arrival | start | completion | complete waiting | complete sojourn")
    for part in parts:
        print(
            f"{part.number:>4} | {part.arrival:>7} | {part.start:>5} | "
            f"{part.departure:>10} | {part.waiting:>16} | {part.sojourn:>16}"
        )

    cutoff = statistics(parts, dec("15"))
    full = statistics(parts, parts[-1].departure)
    display("Original cutoff at T=15", cutoff)
    display("Counterfactual run until all parts depart", full)

    assert [(p.start, p.departure) for p in parts] == [
        (dec("0"), dec("4.58")),
        (dec("6.84"), dec("9.80")),
        (dec("9.80"), dec("15.66")),
        (dec("15.66"), dec("18.87")),
        (dec("18.87"), dec("21.98")),
    ]
    assert cutoff["completed"] == 2
    assert cutoff["queue_at_horizon"] == 2
    assert cutoff["busy_at_horizon"] == 1
    assert cutoff["queue_area"] == dec("4.09")
    assert cutoff["busy_area"] == dec("12.74")
    assert cutoff["occupancy_area"] == dec("16.83")
    assert cutoff["average_completed_sojourn"] == dec("3.77")
    assert full["completed"] == 5
    assert full["queue_area"] == dec("8.62")
    assert full["busy_area"] == dec("19.72")
    assert full["occupancy_area"] == dec("28.34")
    print("\nSelf-check passed.")


if __name__ == "__main__":
    main()
