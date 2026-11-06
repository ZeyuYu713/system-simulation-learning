"""A minimal, reproducible discrete-event simulation of two parallel servers.

Rules:
    - One shared first-come, first-served queue.
    - Server M1 is preferred when both servers are idle.
    - At equal timestamps, process ALL completions and serve the old queue
      before processing new arrivals.
    - If several arrivals share a timestamp, keep their input order.
    - Service times must be strictly positive; all times are >= 0.

Run: python examples/m1_priority_queue.py
Dependencies: Python standard library only (Python 3.10+).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from typing import Iterable


@dataclass(frozen=True)
class Customer:
    customer_id: int
    arrival: float
    service: float


@dataclass(frozen=True)
class ServiceRecord:
    customer_id: int
    machine: str
    arrival: float
    service: float
    start: float
    departure: float

    @property
    def wait(self) -> float:
        return self.start - self.arrival

    @property
    def system_time(self) -> float:
        return self.departure - self.arrival


@dataclass(frozen=True)
class SimulationRun:
    records: list[ServiceRecord]
    horizon: float
    mean_wait: float
    mean_system_time: float
    mean_queue_length: float
    utilization: dict[str, float]


def simulate(customers: Iterable[Customer]) -> SimulationRun:
    """Run a terminating simulation; the horizon ends at the last departure."""
    items = list(customers)
    if not items:
        raise ValueError("At least one customer is required")
    if len({c.customer_id for c in items}) != len(items):
        raise ValueError("Customer IDs must be unique")
    if any(c.arrival < 0 or c.service <= 0 for c in items):
        raise ValueError("Arrivals must be >= 0 and service times > 0")

    # Tuple ordering: timestamp, priority, insertion order, type, payload.
    # Priority 0 means completion and 1 means arrival.
    sequence = count()
    events: list[tuple[float, int, int, str, object]] = []

    def schedule(time: float, priority: int, kind: str, payload: object) -> None:
        heappush(events, (time, priority, next(sequence), kind, payload))

    for customer in items:
        schedule(customer.arrival, 1, "arrival", customer)

    machines = ("M1", "M2")
    busy: dict[str, int | None] = {name: None for name in machines}
    busy_area = {name: 0.0 for name in machines}
    queue: deque[Customer] = deque()
    queue_area = 0.0
    started: dict[int, tuple[str, float, Customer]] = {}
    completed: dict[int, ServiceRecord] = {}
    previous_time = 0.0

    def fill_idle_machines(now: float) -> None:
        for machine in machines:  # M1 is examined before M2.
            if busy[machine] is None and queue:
                customer = queue.popleft()
                busy[machine] = customer.customer_id
                started[customer.customer_id] = (machine, now, customer)
                schedule(
                    now + customer.service,
                    0,
                    "completion",
                    (machine, customer.customer_id),
                )

    while events:
        now = events[0][0]
        elapsed = now - previous_time
        if elapsed < 0:
            raise AssertionError("Event clock moved backward")

        # Integrate time-weighted statistics BEFORE updating the state.
        queue_area += len(queue) * elapsed
        for machine in machines:
            if busy[machine] is not None:
                busy_area[machine] += elapsed

        completions: list[tuple[str, int]] = []
        arrivals: list[Customer] = []
        while events and events[0][0] == now:
            _, _, _, kind, payload = heappop(events)
            if kind == "completion":
                completions.append(payload)  # type: ignore[arg-type]
            else:
                arrivals.append(payload)  # type: ignore[arg-type]

        # Release both machines before routing queued work.
        for machine, customer_id in completions:
            if busy[machine] != customer_id:
                raise AssertionError("Completion event does not match machine")
            busy[machine] = None
            used_machine, start, customer = started.pop(customer_id)
            completed[customer_id] = ServiceRecord(
                customer_id=customer_id,
                machine=used_machine,
                arrival=customer.arrival,
                service=customer.service,
                start=start,
                departure=now,
            )

        # The preexisting FCFS queue has priority over arrivals at this time.
        fill_idle_machines(now)
        queue.extend(arrivals)
        fill_idle_machines(now)
        previous_time = now

    horizon = previous_time
    records = [completed[customer.customer_id] for customer in items]
    n = len(records)
    return SimulationRun(
        records=records,
        horizon=horizon,
        mean_wait=sum(record.wait for record in records) / n,
        mean_system_time=sum(record.system_time for record in records) / n,
        mean_queue_length=queue_area / horizon,
        utilization={name: busy_area[name] / horizon for name in machines},
    )


def main() -> None:
    arrivals = [0, 1, 2, 3, 4, 5]
    services = [4, 3, 2, 1, 3, 2]
    customers = [
        Customer(customer_id=i + 1, arrival=a, service=s)
        for i, (a, s) in enumerate(zip(arrivals, services))
    ]
    result = simulate(customers)

    print("ID  Machine  Arrive  Service  Start  Leave  Wait  System")
    for r in result.records:
        print(
            f"{r.customer_id:>2}  {r.machine:>7}  {r.arrival:>6g}  "
            f"{r.service:>7g}  {r.start:>5g}  {r.departure:>5g}  "
            f"{r.wait:>4g}  {r.system_time:>6g}"
        )
    print(f"Mean wait:         {result.mean_wait:.6f}")
    print(f"Mean system time:  {result.mean_system_time:.6f}")
    print(f"Mean queue length: {result.mean_queue_length:.6f}")
    for machine in ("M1", "M2"):
        print(f"{machine} utilization:    {result.utilization[machine]:.2%}")

    # Validate against the event table in notes/02-discrete-event-queue.md.
    expected_starts = [0, 1, 4, 4, 5, 6]
    expected_leaves = [4, 4, 6, 5, 8, 8]
    assert [r.start for r in result.records] == expected_starts
    assert [r.departure for r in result.records] == expected_leaves
    assert abs(result.mean_wait - 5 / 6) < 1e-12
    assert abs(result.mean_queue_length - 5 / 8) < 1e-12
    assert result.utilization == {"M1": 1.0, "M2": 7 / 8}
    print("Self-check passed.")


if __name__ == "__main__":
    main()
