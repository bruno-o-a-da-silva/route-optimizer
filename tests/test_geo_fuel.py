import math

import pytest

from route_optimizer.fuel import (
    G,
    Vehicle,
    energy_mj_per_km,
    fuel_l_per_km,
    route_fuel_l,
    tractive_force_n,
)
from route_optimizer.geo import EARTH_RADIUS_KM, distance_matrix, haversine_km
from route_optimizer.model import Instance, Node


def test_haversine_one_degree_of_latitude() -> None:
    assert haversine_km(0, 0, 1, 0) == pytest.approx(2 * math.pi * EARTH_RADIUS_KM / 360)


def test_haversine_known_pair() -> None:
    # Paris (48.8566, 2.3522) to London (51.5074, -0.1278): about 343.5 km
    assert haversine_km(48.8566, 2.3522, 51.5074, -0.1278) == pytest.approx(343.5, abs=1.0)


def test_matrix_symmetric_with_detour() -> None:
    m = distance_matrix([(0, 0), (0, 1)], detour=1.5)
    assert m[0][1] == m[1][0] == pytest.approx(1.5 * haversine_km(0, 0, 0, 1))
    with pytest.raises(ValueError):
        distance_matrix([(0, 0)], detour=0.9)


def test_tractive_force_hand_computed() -> None:
    v = Vehicle()
    # m = 5000 kg at 54 km/h (15 m/s):
    # rolling 0.008*5000*9.80665 = 392.27 N; aero 0.5*1.2*0.6*6*225 = 486.0 N
    f = tractive_force_n(v, 5000, 54)
    assert f == pytest.approx(0.008 * 5000 * G + 486.0)
    assert energy_mj_per_km(v, 5000, 54) == pytest.approx(f / 1000)
    assert fuel_l_per_km(v, 5000, 54) == pytest.approx(f / 1000 / (0.30 * 36.0))


def test_heavier_is_thirstier() -> None:
    v = Vehicle()
    assert fuel_l_per_km(v, 6000, 40) > fuel_l_per_km(v, 4000, 40)


def test_route_fuel_sheds_load() -> None:
    nodes = [Node(0, 0), Node(0, 0.1, demand_kg=1000)]
    inst = Instance(nodes, capacity_kg=2000, speed_kmh=40, detour=1.0)
    v = Vehicle()
    d = inst.dist[0][1]
    expected = d * fuel_l_per_km(v, 4500, 40) + d * fuel_l_per_km(v, 3500, 40)
    assert route_fuel_l(inst, [1], v) == pytest.approx(expected)
