"""Command-line interface: solve one synthetic instance or run the benchmark."""

import argparse
import csv
from pathlib import Path

from route_optimizer.bench import run_benchmark
from route_optimizer.fuel import Vehicle, route_fuel_l
from route_optimizer.solvers import local_search, nearest_neighbour
from route_optimizer.synth import synthetic_instance


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="route-optimizer", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("solve", help="solve one seeded synthetic instance")
    s.add_argument("-n", type=int, default=60)
    s.add_argument("--seed", type=int, default=1)
    b = sub.add_parser("bench", help="baseline vs local search over several seeds")
    b.add_argument("-n", type=int, default=60)
    b.add_argument("--seeds", type=int, default=10)
    b.add_argument("--csv", type=Path)
    args = p.parse_args(argv)

    if args.cmd == "solve":
        inst = synthetic_instance(n=args.n, seed=args.seed)
        nn = nearest_neighbour(inst)
        ls = local_search(inst, nn)
        v = Vehicle()
        print("Synthetic example data")
        for name, sol in (("nearest neighbour", nn), ("local search", ls)):
            fuel = sum(route_fuel_l(inst, r, v) for r in sol.routes)
            print(
                f"{name:>18}: {sol.distance(inst):8.1f} km, {len(sol.routes)} vehicles, "
                f"{fuel:6.1f} L, unserved {len(sol.unserved)}"
            )
        for k, route in enumerate(ls.routes, 1):
            print(f"  route {k}: 0-{'-'.join(map(str, route))}-0")
        return 0

    rows = run_benchmark(list(range(1, args.seeds + 1)), args.n)
    print("seed  nn_km   ls_km  saving%  veh nn/ls  fuel nn/ls L  (synthetic example data)")
    for r in rows:
        print(
            f"{r.seed:4d} {r.nn_km:7.1f} {r.ls_km:7.1f} {r.km_saving_pct:7.1f}  "
            f"{r.nn_vehicles:3d}/{r.ls_vehicles:<3d}  {r.nn_fuel_l:6.1f}/{r.ls_fuel_l:<6.1f}"
        )
    mean = sum(r.km_saving_pct for r in rows) / len(rows)
    print(f"mean distance saving: {mean:.1f}%")
    if args.csv:
        with args.csv.open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(
                [
                    "seed",
                    "customers",
                    "nn_km",
                    "ls_km",
                    "nn_vehicles",
                    "ls_vehicles",
                    "nn_fuel_l",
                    "ls_fuel_l",
                    "unserved",
                    "km_saving_pct",
                ]
            )
            for r in rows:
                w.writerow(
                    [
                        r.seed,
                        r.customers,
                        f"{r.nn_km:.3f}",
                        f"{r.ls_km:.3f}",
                        r.nn_vehicles,
                        r.ls_vehicles,
                        f"{r.nn_fuel_l:.3f}",
                        f"{r.ls_fuel_l:.3f}",
                        r.unserved,
                        f"{r.km_saving_pct:.2f}",
                    ]
                )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
