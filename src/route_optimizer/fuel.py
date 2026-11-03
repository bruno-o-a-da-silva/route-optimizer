"""Steady-state, flat-road fuel model.

Tractive force F = Crr * m * g + 0.5 * rho * Cd * A * v^2   [N]
Wheel energy per km E = F * 1000 m                          [J/km]
Fuel per km = E / (eta * LHV)                               [L/km]

All default parameters are stated assumptions for a light delivery truck.
"""

from dataclasses import dataclass

from route_optimizer.model import Instance, Route

G = 9.80665  # standard gravity, m/s^2


@dataclass(frozen=True)
class Vehicle:
    curb_mass_kg: float = 3500.0
    crr: float = 0.008  # rolling resistance coefficient, dimensionless
    cd: float = 0.6  # drag coefficient, dimensionless
    frontal_area_m2: float = 6.0
    air_density_kg_m3: float = 1.2  # about 20 C at sea level
    drivetrain_eff: float = 0.30  # tank-to-wheel efficiency, dimensionless
    fuel_lhv_mj_per_l: float = 36.0  # diesel lower heating value, MJ/L


def tractive_force_n(v: Vehicle, mass_kg: float, speed_kmh: float) -> float:
    ms = speed_kmh / 3.6
    return v.crr * mass_kg * G + 0.5 * v.air_density_kg_m3 * v.cd * v.frontal_area_m2 * ms**2


def energy_mj_per_km(v: Vehicle, mass_kg: float, speed_kmh: float) -> float:
    """Energy at the wheels per km, MJ/km (F [N] * 1000 [m] / 1e6)."""
    return tractive_force_n(v, mass_kg, speed_kmh) / 1000.0


def fuel_l_per_km(v: Vehicle, mass_kg: float, speed_kmh: float) -> float:
    return energy_mj_per_km(v, mass_kg, speed_kmh) / (v.drivetrain_eff * v.fuel_lhv_mj_per_l)


def route_fuel_l(inst: Instance, route: Route, v: Vehicle) -> float:
    """Fuel for a delivery route: the vehicle leaves full and sheds load at each stop."""
    load = sum(inst.nodes[c].demand_kg for c in route)
    total, prev = 0.0, 0
    for c in [*route, 0]:
        total += inst.dist[prev][c] * fuel_l_per_km(v, v.curb_mass_kg + load, inst.speed_kmh)
        load -= inst.nodes[c].demand_kg
        prev = c
    return total
