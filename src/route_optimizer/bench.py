"""Baseline vs improved benchmark over seeded synthetic instances."""

from dataclasses import dataclass

from route_optimizer.fuel import Vehicle, route_fuel_l
from route_optimizer.solvers import local_search, nearest_neighbour
from route_optimizer.synth import synthetic_instance


@dataclass(frozen=True)
class BenchRow:
    seed: int
    customers: int
    nn_km: float
    ls_km: float
    nn_vehicles: int
    ls_vehicles: int
    nn_fuel_l: float
    ls_fuel_l: float
    unserved: int

    @property
    def km_saving_pct(self) -> float:
        return 100.0 * (self.nn_km - self.ls_km) / self.nn_km


def run_benchmark(seeds: list[int], n: int = 60) -> list[BenchRow]:
    v = Vehicle()
    rows = []
    for seed in seeds:
        inst = synthetic_instance(n=n, seed=seed)
        nn = nearest_neighbour(inst)
        ls = local_search(inst, nn)
        assert nn.feasible(inst) and ls.feasible(inst)
        rows.append(
            BenchRow(
                seed,
                n,
                nn.distance(inst),
                ls.distance(inst),
                len(nn.routes),
                len(ls.routes),
                sum(route_fuel_l(inst, r, v) for r in nn.routes),
                sum(route_fuel_l(inst, r, v) for r in ls.routes),
                len(ls.unserved),
            )
        )
    return rows
