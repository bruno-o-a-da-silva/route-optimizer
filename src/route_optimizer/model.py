"""Problem instance and route evaluation.

Node 0 is the depot; nodes 1..n are customers. Times are minutes from the start
of the shift, distances km, demand kg, speed km/h.
"""

from dataclasses import dataclass, field

from route_optimizer.geo import distance_matrix


@dataclass(frozen=True)
class Node:
    lat: float
    lon: float
    demand_kg: float = 0.0
    ready_min: float = 0.0
    due_min: float = 1e9
    service_min: float = 0.0


@dataclass
class Instance:
    nodes: list[Node]
    capacity_kg: float
    speed_kmh: float = 40.0
    max_vehicles: int = 50
    detour: float = 1.3
    dist: list[list[float]] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.capacity_kg <= 0 or self.speed_kmh <= 0:
            raise ValueError("capacity and speed must be positive")
        self.dist = distance_matrix([(n.lat, n.lon) for n in self.nodes], self.detour)

    @property
    def customers(self) -> list[int]:
        return list(range(1, len(self.nodes)))

    def travel_min(self, i: int, j: int) -> float:
        return self.dist[i][j] / self.speed_kmh * 60.0


Route = list[int]  # customer indices, depot implicit at both ends


def route_distance(inst: Instance, route: Route) -> float:
    path = [0, *route, 0]
    return sum(inst.dist[a][b] for a, b in zip(path, path[1:], strict=False))


def route_feasible(inst: Instance, route: Route) -> bool:
    """Capacity and hard time windows (waiting allowed); must return before depot due."""
    if sum(inst.nodes[c].demand_kg for c in route) > inst.capacity_kg + 1e-9:
        return False
    t, prev = inst.nodes[0].ready_min, 0
    for c in [*route, 0]:
        node = inst.nodes[c]
        t = max(t + inst.travel_min(prev, c), node.ready_min)
        if t > node.due_min + 1e-9:
            return False
        t += node.service_min
        prev = c
    return True


@dataclass
class Solution:
    routes: list[Route]
    unserved: list[int] = field(default_factory=list)

    def distance(self, inst: Instance) -> float:
        return sum(route_distance(inst, r) for r in self.routes)

    def feasible(self, inst: Instance) -> bool:
        served = sorted(c for r in self.routes for c in r)
        if len(served) != len(set(served)):
            return False
        if sorted(served + self.unserved) != inst.customers:
            return False
        return len(self.routes) <= inst.max_vehicles and all(
            route_feasible(inst, r) for r in self.routes
        )
