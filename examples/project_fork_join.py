"""Deterministic checks for project precedence, critical path and resources.

The example uses four activities:
    A (2 h), B (4 h) after A, C (3 h) after A, D (2 h) after B and C.

With independent B/C resources, the project finishes in 8 hours.
If B and C share one non-preemptive capacity-one resource, it takes 11 hours.
Only the Python standard library is required.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Activity:
    name: str
    duration: float
    predecessors: tuple[str, ...] = ()


@dataclass(frozen=True)
class Times:
    early_start: float
    early_finish: float
    late_start: float
    late_finish: float

    @property
    def total_float(self) -> float:
        return self.late_start - self.early_start


def critical_path(activities: list[Activity]) -> tuple[dict[str, Times], float]:
    """Perform a forward and backward pass on an acyclic activity network."""
    if not activities:
        raise ValueError("At least one activity is required")
    by_name = {a.name: a for a in activities}
    if len(by_name) != len(activities):
        raise ValueError("Activity names must be unique")
    if any(a.duration < 0 for a in activities):
        raise ValueError("Durations cannot be negative")

    # Kahn-style topological ordering, keeping the input order for ties.
    predecessors = {a.name: set(a.predecessors) for a in activities}
    for name, dependencies in predecessors.items():
        if name in dependencies:
            raise ValueError("Self-dependency is not allowed")
        if dependencies.difference(by_name):
            raise ValueError(f"Unknown predecessor for {name}")

    successors: dict[str, set[str]] = {name: set() for name in by_name}
    for name, dependencies in predecessors.items():
        for dependency in dependencies:
            successors[dependency].add(name)

    indegree = {name: len(dependencies) for name, dependencies in predecessors.items()}
    ordered: list[str] = []
    while len(ordered) < len(activities):
        ready = [
            a.name for a in activities
            if indegree[a.name] == 0 and a.name not in ordered
        ]
        if not ready:
            raise ValueError("The precedence network contains a cycle")
        current = ready[0]
        ordered.append(current)
        indegree[current] = -1
        for successor in successors[current]:
            indegree[successor] -= 1

    es: dict[str, float] = {}
    ef: dict[str, float] = {}
    for name in ordered:
        es[name] = max((ef[p] for p in predecessors[name]), default=0.0)
        ef[name] = es[name] + by_name[name].duration

    project_finish = max(ef.values())
    ls: dict[str, float] = {}
    lf: dict[str, float] = {}
    for name in reversed(ordered):
        lf[name] = min((ls[s] for s in successors[name]), default=project_finish)
        ls[name] = lf[name] - by_name[name].duration

    return {
        name: Times(es[name], ef[name], ls[name], lf[name])
        for name in ordered
    }, project_finish


def schedule_shared_resource(first: str = "B") -> dict[str, tuple[float, float]]:
    """Construct a valid four-activity schedule with one common B/C machine."""
    if first not in ("B", "C"):
        raise ValueError("First shared-resource activity must be B or C")
    durations = {"A": 2.0, "B": 4.0, "C": 3.0, "D": 2.0}
    second = "C" if first == "B" else "B"
    blocks: dict[str, tuple[float, float]] = {"A": (0.0, durations["A"])}

    machine_available = blocks["A"][1]
    for activity in (first, second):
        start = machine_available
        end = start + durations[activity]
        blocks[activity] = (start, end)
        machine_available = end

    join_time = max(blocks["B"][1], blocks["C"][1])
    blocks["D"] = (join_time, join_time + durations["D"])
    return blocks


def expected_random_fork_duration() -> float:
    """Exact expectation when B,C independently take 1 or 3 hours (p=.5)."""
    choices = (1.0, 3.0)
    return 2.0 + sum(max(b, c) * 0.25 for b in choices for c in choices) + 2.0


def main() -> None:
    network = [
        Activity("A", 2.0),
        Activity("B", 4.0, ("A",)),
        Activity("C", 3.0, ("A",)),
        Activity("D", 2.0, ("B", "C")),
    ]
    times, project_finish = critical_path(network)
    print("CPM activity times (hours)")
    print("Activity  ES  EF  LS  LF  Float")
    for name, entry in times.items():
        print(
            f"{name:>8}  {entry.early_start:>2g}  "
            f"{entry.early_finish:>2g}  {entry.late_start:>2g}  "
            f"{entry.late_finish:>2g}  {entry.total_float:>5g}"
        )
    print(f"Resource-unconstrained project duration: {project_finish:g} h")

    assert project_finish == 8
    assert [name for name, entry in times.items() if entry.total_float == 0] == [
        "A", "B", "D"
    ]
    assert times["C"].total_float == 1

    for first in ("B", "C"):
        blocks = schedule_shared_resource(first)
        duration = blocks["D"][1]
        print(f"Shared resource: {first} first; duration = {duration:g} h")
        assert duration == 11
        assert blocks["B"][1] <= blocks["C"][0] or (
            blocks["C"][1] <= blocks["B"][0]
        )
        assert blocks["D"][0] == max(blocks["B"][1], blocks["C"][1])

    result = expected_random_fork_duration()
    print(f"Exact expected random fork duration: {result:g} h")
    assert result == 6.5
    print("All project scheduling checks passed.")


if __name__ == "__main__":
    main()
