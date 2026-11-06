"""Event-scheduling demonstration: four parts through M1 -> transport -> M2.

Both machines have a separate FCFS queue. Parts are non-preemptive and need
both stages. At a shared timestamp, complete services and serve existing queues
before admitting new arrivals. The transport time is exactly one time unit.

Run: python examples/tandem_parts_event_simulation.py
Dependencies: Python standard library only, Python 3.10+.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count


@dataclass(frozen=True)
class Part:
    number: int
    arrival: float
    m1_time: float
    m2_time: float


@dataclass
class PartTimes:
    m1_start: float | None = None
    m1_end: float | None = None
    m2_arrival: float | None = None
    m2_start: float | None = None
    m2_end: float | None = None


@dataclass
class Summary:
    horizon: float
    part_times: dict[int, PartTimes]
    q1_area: float
    q2_area: float
    m1_busy_area: float
    m2_busy_area: float
    trace: list[tuple[float, str, str, str, str, str]]

    @property
    def mean_q1(self) -> float:
        return self.q1_area / self.horizon

    @property
    def mean_q2(self) -> float:
        return self.q2_area / self.horizon

    @property
    def m1_utilization(self) -> float:
        return self.m1_busy_area / self.horizon

    @property
    def m2_utilization(self) -> float:
        return self.m2_busy_area / self.horizon


PARTS = [
    Part(1, 0, 5, 3),
    Part(2, 3, 5, 4),
    Part(3, 4, 3, 5),
    Part(4, 6, 1, 4),
]


def run(parts: list[Part], *, transport: float = 1, until: float | None = None) -> Summary:
    if not parts or transport <= 0:
        raise ValueError("Parts must be nonempty and transport time positive")
    if until is not None and until <= 0:
        raise ValueError("Observation horizon must be positive")
    if len({part.number for part in parts}) != len(parts):
        raise ValueError("Part numbers must be unique")
    if any(part.arrival < 0 or part.m1_time <= 0 or part.m2_time <= 0 for part in parts):
        raise ValueError("Arrivals must be nonnegative and service times positive")

    by_id = {part.number: part for part in parts}
    times = {part.number: PartTimes() for part in parts}
    sequence = count()
    events: list[tuple[float, int, int, str, int]] = []

    def schedule(t: float, priority: int, kind: str, pid: int) -> None:
        heappush(events, (t, priority, next(sequence), kind, pid))

    for part in parts:
        schedule(part.arrival, 1, "arrive_m1", part.number)

    q1: deque[int] = deque()
    q2: deque[int] = deque()
    busy1: int | None = None
    busy2: int | None = None
    q1_area = q2_area = busy1_area = busy2_area = 0.0
    previous = 0.0
    trace: list[tuple[float, str, str, str, str, str]] = []

    def allocate(now: float) -> None:
        nonlocal busy1, busy2
        if busy1 is None and q1:
            pid = q1.popleft()
            busy1 = pid
            times[pid].m1_start = now
            schedule(now + by_id[pid].m1_time, 0, "finish_m1", pid)
        if busy2 is None and q2:
            pid = q2.popleft()
            busy2 = pid
            times[pid].m2_start = now
            schedule(now + by_id[pid].m2_time, 0, "finish_m2", pid)

    while events and (until is None or events[0][0] <= until):
        now = events[0][0]
        dt = now - previous
        q1_area += len(q1) * dt
        q2_area += len(q2) * dt
        busy1_area += (busy1 is not None) * dt
        busy2_area += (busy2 is not None) * dt

        completions: list[tuple[str, int]] = []
        arrivals: list[tuple[str, int]] = []
        while events and events[0][0] == now:
            _, _, _, kind, pid = heappop(events)
            (completions if kind.startswith("finish") else arrivals).append((kind, pid))

        for kind, pid in completions:
            if kind == "finish_m1":
                assert busy1 == pid
                busy1 = None
                times[pid].m1_end = now
                schedule(now + transport, 1, "arrive_m2", pid)
            else:
                assert busy2 == pid
                busy2 = None
                times[pid].m2_end = now

        # Preexisting queues get the newly idle machines first.
        allocate(now)
        for kind, pid in arrivals:
            if kind == "arrive_m1":
                q1.append(pid)
            else:
                times[pid].m2_arrival = now
                q2.append(pid)
        allocate(now)

        event_text = ", ".join(f"{kind}({pid})" for kind, pid in completions + arrivals)
        trace.append((now, event_text, str(list(q1)), str(busy1), str(list(q2)), str(busy2)))
        previous = now

    horizon = previous if until is None else until
    if until is not None:
        dt = horizon - previous
        q1_area += len(q1) * dt
        q2_area += len(q2) * dt
        busy1_area += (busy1 is not None) * dt
        busy2_area += (busy2 is not None) * dt

    return Summary(
        horizon=horizon,
        part_times=times,
        q1_area=q1_area,
        q2_area=q2_area,
        m1_busy_area=busy1_area,
        m2_busy_area=busy2_area,
        trace=trace,
    )


def main() -> None:
    partial = run(PARTS, until=10)
    full = run(PARTS)

    print("At t=10:")
    print(f"  M1 utilization = {partial.m1_utilization:.2%}")
    print(f"  M2 utilization = {partial.m2_utilization:.2%}")
    print(f"  Mean M1 queue  = {partial.mean_q1:.4f}")
    print("\nFull trajectory: ")
    print("Part  M1 start/end   M2 arrival/start/end   System sojourn")
    for part in PARTS:
        t = full.part_times[part.number]
        assert all(v is not None for v in vars(t).values())
        sojourn = t.m2_end - part.arrival  # type: ignore[operator]
        print(
            f"{part.number:>4}  {t.m1_start:>4g}/{t.m1_end:<4g}   "
            f"{t.m2_arrival:>4g}/{t.m2_start:>4g}/{t.m2_end:<4g}   {sojourn:>6g}"
        )
    mean_sojourn = sum(
        full.part_times[part.number].m2_end - part.arrival  # type: ignore[operator]
        for part in PARTS
    ) / len(PARTS)
    print(f"Total completion = {full.horizon:g}")
    print(f"Mean sojourn     = {mean_sojourn:.4f}")
    print(f"Mean Q1 / Q2     = {full.mean_q1:.4f} / {full.mean_q2:.4f}")
    print(f"M1 / M2 busy     = {full.m1_busy_area:g} / {full.m2_busy_area:g}")

    # Independent checks against the hand-worked event table.
    assert [full.part_times[i].m1_end for i in range(1, 5)] == [5, 10, 13, 14]
    assert [full.part_times[i].m2_end for i in range(1, 5)] == [9, 15, 20, 24]
    assert abs(full.q1_area - 15) < 1e-12
    assert abs(full.q2_area - 6) < 1e-12
    assert abs(full.m1_busy_area - 14) < 1e-12
    assert abs(full.m2_busy_area - 16) < 1e-12
    assert abs(mean_sojourn - 13.75) < 1e-12
    assert abs(partial.q1_area - 12) < 1e-12
    assert abs(partial.m1_utilization - 1) < 1e-12
    assert abs(partial.m2_utilization - 0.3) < 1e-12
    print("Self-check passed.")


if __name__ == "__main__":
    main()
