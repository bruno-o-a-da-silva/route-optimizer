"""Redraw docs/img charts and docs/benchmark.csv from seeded instances. Needs matplotlib."""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from _style import BG, GOLD, IMG, MUTED, TEXT, style, title

from route_optimizer.bench import run_benchmark
from route_optimizer.model import Instance, Solution
from route_optimizer.solvers import local_search, nearest_neighbour
from route_optimizer.synth import synthetic_instance

DOCS = Path(__file__).resolve().parent.parent / "docs"


def draw_routes(ax: plt.Axes, inst: Instance, sol: Solution, color: str, lw: float) -> None:
    for r in sol.routes:
        path = [0, *r, 0]
        ax.plot(
            [inst.nodes[i].lon for i in path],
            [inst.nodes[i].lat for i in path],
            color=color,
            lw=lw,
            solid_capstyle="round",
        )


def draw_stops(ax: plt.Axes, inst: Instance) -> None:
    ax.scatter(
        [n.lon for n in inst.nodes[1:]],
        [n.lat for n in inst.nodes[1:]],
        s=12,
        color=TEXT,
        zorder=3,
        linewidths=0,
    )
    ax.scatter(
        [inst.nodes[0].lon],
        [inst.nodes[0].lat],
        s=90,
        marker="s",
        color=BG,
        edgecolor=GOLD,
        linewidths=1.6,
        zorder=4,
    )


def main() -> None:
    style()
    rows = run_benchmark(list(range(1, 11)), n=60)
    with (DOCS / "benchmark.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            [
                "seed",
                "nn_km",
                "ls_km",
                "saving_pct",
                "nn_vehicles",
                "ls_vehicles",
                "nn_fuel_l",
                "ls_fuel_l",
            ]
        )
        for r in rows:
            w.writerow(
                [
                    r.seed,
                    f"{r.nn_km:.1f}",
                    f"{r.ls_km:.1f}",
                    f"{r.km_saving_pct:.1f}",
                    r.nn_vehicles,
                    r.ls_vehicles,
                    f"{r.nn_fuel_l:.1f}",
                    f"{r.ls_fuel_l:.1f}",
                ]
            )
    x = list(range(len(rows)))
    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.bar(
        [i - 0.2 for i in x],
        [r.nn_km for r in rows],
        0.38,
        color="#3A3A3A",
        label="Nearest neighbour",
    )
    ax.bar([i + 0.2 for i in x], [r.ls_km for r in rows], 0.38, color=GOLD, label="2-opt + or-opt")
    ax.set_xticks(x, [str(r.seed) for r in rows])
    ax.grid(axis="x", visible=False)
    ax.set_xlabel("Instance seed")
    ax.set_ylabel("Total distance (km)")
    mean = sum(r.km_saving_pct for r in rows) / len(rows)
    title(
        ax,
        "Nearest neighbour against local search",
        f"Mean distance saving {mean:.1f}% over 10 instances of 60 customers",
    )
    ax.legend(frameon=False, loc="upper right", bbox_to_anchor=(1, 1.16), ncol=2, fontsize=9)
    fig.tight_layout()
    fig.savefig(IMG / "benchmark.png")
    plt.close(fig)

    inst = synthetic_instance(n=60, seed=1)
    nn = nearest_neighbour(inst)
    ls = local_search(inst, nn)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5.2), sharex=True, sharey=True)
    for ax, name, sol, color in (
        (axes[0], "Nearest neighbour", nn, MUTED),
        (axes[1], "2-opt + or-opt", ls, GOLD),
    ):
        draw_routes(ax, inst, sol, color, 1.1)
        draw_stops(ax, inst)
        ax.set_aspect("equal")
        ax.grid(visible=False)
        title(ax, name, f"{sol.distance(inst):.1f} km, {len(sol.routes)} trucks")
        ax.set_xlabel("Longitude")
    axes[0].set_ylabel("Latitude")
    fig.tight_layout()
    fig.savefig(IMG / "routes_seed1.png", bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)


if __name__ == "__main__":
    main()
