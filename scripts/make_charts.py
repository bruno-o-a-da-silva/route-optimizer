"""Render docs/ benchmark charts and CSV from seeded synthetic instances (needs matplotlib)."""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

from route_optimizer.bench import run_benchmark  # noqa: E402
from route_optimizer.solvers import local_search, nearest_neighbour  # noqa: E402
from route_optimizer.synth import synthetic_instance  # noqa: E402

INDIGO, INDIGO_MID, INDIGO_LIGHT = "#3A2FD0", "#6E66F0", "#8F89FF"
PINK, PINK_TEXT = "#FF2E88", "#D81B6E"
DOCS = Path(__file__).resolve().parent.parent / "docs"
NOTE = "synthetic example data, seeds 1-10, 60 customers each"


def style() -> None:
    for f in font_manager.findSystemFonts():
        if any(n in f for n in ("Playfair", "Inter", "IBMPlexMono")):
            font_manager.fontManager.addfont(f)
    plt.rcParams.update({
        "font.family": "Inter", "axes.edgecolor": "#C9C6F5", "axes.labelcolor": "#1B1650",
        "xtick.color": "#1B1650", "ytick.color": "#1B1650", "axes.spines.top": False,
        "axes.spines.right": False, "figure.dpi": 150,
    })


def title(ax: plt.Axes, text: str) -> None:
    ax.set_title(text, fontfamily="Playfair Display", fontsize=15, color=INDIGO, loc="left")


def main() -> None:
    style()
    rows = run_benchmark(list(range(1, 11)), n=60)
    with (DOCS / "benchmark.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["seed", "nn_km", "ls_km", "saving_pct", "nn_vehicles", "ls_vehicles",
                    "nn_fuel_l", "ls_fuel_l"])
        for r in rows:
            w.writerow([r.seed, f"{r.nn_km:.1f}", f"{r.ls_km:.1f}", f"{r.km_saving_pct:.1f}",
                        r.nn_vehicles, r.ls_vehicles, f"{r.nn_fuel_l:.1f}",
                        f"{r.ls_fuel_l:.1f}"])
    x = list(range(len(rows)))
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.bar([i - 0.2 for i in x], [r.nn_km for r in rows], 0.4, color=INDIGO_LIGHT,
           label="Nearest neighbour")
    ax.bar([i + 0.2 for i in x], [r.ls_km for r in rows], 0.4, color=INDIGO,
           label="2-opt + or-opt")
    ax.set_xticks(x, [str(r.seed) for r in rows])
    ax.set_xlabel("Instance seed")
    ax.set_ylabel("Total distance (km)")
    mean = sum(r.km_saving_pct for r in rows) / len(rows)
    ax.text(0.99, 1.02, f"mean saving {mean:.1f}%", transform=ax.transAxes, ha="right",
            color=PINK_TEXT, fontfamily="IBM Plex Mono", fontsize=10)
    title(ax, "Baseline vs local search")
    ax.legend(frameon=False, loc="lower right")
    fig.text(0.01, 0.01, NOTE, fontsize=8, color="#6B679A", fontfamily="IBM Plex Mono")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(DOCS / "benchmark.png")

    inst = synthetic_instance(n=60, seed=1)
    sols = (("Nearest neighbour", nearest_neighbour(inst)),)
    sols += (("2-opt + or-opt", local_search(inst, sols[0][1])),)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5), sharex=True, sharey=True)
    palette = [INDIGO, INDIGO_MID, INDIGO_LIGHT, PINK]
    for ax, (name, sol) in zip(axes, sols, strict=True):
        for k, r in enumerate(sol.routes):
            path = [0, *r, 0]
            ax.plot([inst.nodes[i].lon for i in path], [inst.nodes[i].lat for i in path],
                    color=palette[k % len(palette)], lw=1.2)
        ax.scatter([n.lon for n in inst.nodes[1:]], [n.lat for n in inst.nodes[1:]],
                   s=10, color="#1B1650", zorder=3)
        ax.scatter([inst.nodes[0].lon], [inst.nodes[0].lat], s=70, marker="s", color=PINK,
                   zorder=4)
        title(ax, f"{name}: {sol.distance(inst):.0f} km")
        ax.set_xlabel("Longitude")
    axes[0].set_ylabel("Latitude")
    fig.text(0.01, 0.01, "synthetic example data, seed 1", fontsize=8, color="#6B679A",
             fontfamily="IBM Plex Mono")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(DOCS / "routes_seed1.png")


if __name__ == "__main__":
    main()
