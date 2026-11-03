"""Random VRPTW instances around a depot. Not real customers."""

import random

from route_optimizer.model import Instance, Node

DEPOT = (-23.55, -46.63)  # Praca da Se, Sao Paulo; any point would do


def synthetic_instance(
    n: int = 60, seed: int = 1, capacity_kg: float = 1200.0, radius_deg: float = 0.25
) -> Instance:
    # Demand 20-150 kg, windows 2-4 h opening within the first 7 h of a 10 h shift.
    rng = random.Random(seed)
    nodes = [Node(*DEPOT, ready_min=0.0, due_min=600.0)]
    for _ in range(n):
        start = rng.uniform(0, 420)
        nodes.append(
            Node(
                lat=DEPOT[0] + rng.uniform(-radius_deg, radius_deg),
                lon=DEPOT[1] + rng.uniform(-radius_deg, radius_deg),
                demand_kg=float(rng.randint(20, 150)),
                ready_min=start,
                due_min=start + rng.uniform(120, 240),
                service_min=10.0,
            )
        )
    return Instance(nodes, capacity_kg=capacity_kg)
