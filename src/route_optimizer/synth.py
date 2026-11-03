"""Seeded synthetic VRPTW instances (synthetic example data, not real customers)."""

import random

from route_optimizer.model import Instance, Node

DEPOT = (-23.55, -46.63)  # an arbitrary public city-centre coordinate used as origin


def synthetic_instance(
    n: int = 60, seed: int = 1, capacity_kg: float = 1200.0, radius_deg: float = 0.25
) -> Instance:
    """n customers scattered around the depot with demand 20-150 kg and 2-4 h windows
    inside a 10 h shift (600 min)."""
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
