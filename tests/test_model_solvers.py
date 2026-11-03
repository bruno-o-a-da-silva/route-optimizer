import pytest

from route_optimizer.model import Instance, Node, Solution, route_distance, route_feasible
from route_optimizer.solvers import local_search, nearest_neighbour, or_opt, two_opt
from route_optimizer.synth import synthetic_instance


def line_instance(**kw: float) -> Instance:
    # depot at lon 0, customers along the equator at lon 0.1..0.4 (~11.1 km apart)
    nodes = [Node(0, 0, due_min=10_000)] + [Node(0, 0.1 * k, demand_kg=10) for k in range(1, 5)]
    return Instance(nodes, capacity_kg=kw.get("cap", 100), speed_kmh=60, detour=1.0)


def test_invalid_instance() -> None:
    with pytest.raises(ValueError):
        Instance([Node(0, 0)], capacity_kg=0)


def test_capacity_and_time_window_feasibility() -> None:
    inst = line_instance(cap=25)
    assert route_feasible(inst, [1, 2])
    assert not route_feasible(inst, [1, 2, 3])
    tight = Instance(
        [Node(0, 0), Node(0, 0.5, due_min=5)], capacity_kg=10, speed_kmh=60, detour=1.0
    )
    assert not route_feasible(tight, [1])


def test_waiting_is_allowed() -> None:
    inst = Instance(
        [Node(0, 0), Node(0, 0.01, ready_min=100, due_min=110)], capacity_kg=1, detour=1.0
    )
    assert route_feasible(inst, [1])


def test_two_opt_removes_the_zigzag_1_3_2_4() -> None:
    inst = line_instance()
    bad = [1, 3, 2, 4]
    good, improved = two_opt(inst, bad)
    assert improved and route_distance(inst, good) < route_distance(inst, bad)
    assert two_opt(inst, good) == (good, False)


def test_or_opt_moves_between_routes() -> None:
    inst = line_instance()
    routes = [[1, 2], [4, 3]]
    assert or_opt(inst, routes)
    assert sum(route_distance(inst, r) for r in routes) < route_distance(
        inst, [1, 2]
    ) + route_distance(inst, [4, 3])


def test_or_opt_intra_route_and_no_move() -> None:
    inst = line_instance()
    routes = [[2, 1, 3, 4]]
    assert or_opt(inst, routes)
    assert not or_opt(inst, [[1, 2, 3, 4]])


def test_customer_50_degrees_away_is_left_unserved() -> None:
    nodes = [Node(0, 0, due_min=600), Node(0, 0.1, demand_kg=10), Node(0, 50, demand_kg=10)]
    inst = Instance(nodes, capacity_kg=100, detour=1.0)
    sol = nearest_neighbour(inst)
    assert sol.routes == [[1]] and sol.unserved == [2]
    assert sol.feasible(inst)


def test_single_order_heavier_than_the_truck_is_unserved() -> None:
    # A 1.3 t order on a 1.2 t truck: nothing to split it with, so it stays out.
    nodes = [Node(0, 0, due_min=600), Node(0, 0.1, demand_kg=10), Node(0, 0.12, demand_kg=1300)]
    sol = nearest_neighbour(Instance(nodes, capacity_kg=1200, detour=1.0))
    assert sol.routes == [[1]] and sol.unserved == [2]


def test_fleet_limit() -> None:
    inst = line_instance(cap=10)
    inst.max_vehicles = 2
    sol = nearest_neighbour(inst)
    assert len(sol.routes) == 2 and len(sol.unserved) == 2


def test_solution_feasible_checks() -> None:
    inst = line_instance()
    assert not Solution([[1, 1, 2, 3, 4]]).feasible(inst)
    assert not Solution([[1, 2]]).feasible(inst)
    assert Solution([[1, 2, 3, 4]]).feasible(inst)


def test_local_search_beats_nearest_neighbour_on_seed_3() -> None:
    inst = synthetic_instance(n=25, seed=3)
    nn = nearest_neighbour(inst)
    ls = local_search(inst, nn)
    assert ls.feasible(inst)
    assert ls.distance(inst) < nn.distance(inst)
    assert synthetic_instance(n=25, seed=3).nodes == inst.nodes


def test_local_search_respects_iteration_cap() -> None:
    inst = line_instance()
    start = Solution([[2, 1, 4, 3]])
    assert local_search(inst, start, max_iter=0).routes == [[2, 1, 4, 3]]
