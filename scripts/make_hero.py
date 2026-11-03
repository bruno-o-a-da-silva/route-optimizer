"""Draw docs/img/hero.png (1600x640): instance seed 1, nearest neighbour under local search.

Every number is computed from the instance and both solutions.
"""

import matplotlib.pyplot as plt
from _style import GOLD, IMG, MUTED, SERIF, TEXT, style
from make_charts import draw_routes, draw_stops

from route_optimizer.solvers import local_search, nearest_neighbour
from route_optimizer.synth import synthetic_instance


def main() -> None:
    style()
    inst = synthetic_instance(n=60, seed=1)
    nn = nearest_neighbour(inst)
    ls = local_search(inst, nn)
    a, b = nn.distance(inst), ls.distance(inst)

    fig = plt.figure(figsize=(16, 6.4), dpi=100)
    fig.text(0.05, 0.70, "route-optimizer", fontfamily=SERIF, fontsize=50, color=TEXT)
    fig.text(0.05, 0.60, "Delivery routes under time windows and capacity,", fontsize=17,
             color=TEXT)
    fig.text(0.05, 0.545, "improved by 2-opt and or-opt local search.", fontsize=17,
             color=MUTED)
    fig.add_artist(plt.Line2D([0.05, 0.12], [0.47, 0.47], color=GOLD, lw=2))
    fig.add_artist(plt.Line2D([0.05, 0.08], [0.395, 0.395], color=MUTED, lw=1.4))
    fig.text(0.09, 0.38, f"Nearest neighbour   {a:,.1f} km   {len(nn.routes)} trucks",
             fontsize=13, color=MUTED)
    fig.add_artist(plt.Line2D([0.05, 0.08], [0.325, 0.325], color=GOLD, lw=2.2))
    fig.text(0.09, 0.31, f"Local search          {b:,.1f} km   {len(ls.routes)} trucks",
             fontsize=13, color=TEXT)
    fig.text(0.05, 0.20, f"{len(inst.customers)} customers around central S\u00e3o Paulo, "
             f"{100 * (a - b) / a:.1f}% less distance", fontsize=12, color=GOLD)

    ax = fig.add_axes((0.52, 0.04, 0.44, 0.92))
    draw_routes(ax, inst, nn, "#4A4A4A", 0.9)
    draw_routes(ax, inst, ls, GOLD, 1.8)
    draw_stops(ax, inst)
    ax.set_aspect("equal")
    ax.set_axis_off()
    fig.savefig(IMG / "hero.png", dpi=100)


if __name__ == "__main__":
    main()
