"""Nearest-neighbour construction and 2-opt / or-opt local search."""

from route_optimizer.model import Instance, Route, Solution, route_distance, route_feasible

EPS = 1e-9


def nearest_neighbour(inst: Instance) -> Solution:
    """Extend the current route with the closest feasible customer; open a new
    vehicle when none fits. Customers no vehicle can reach are left unserved."""
    unvisited = set(inst.customers)
    routes: list[Route] = []
    while unvisited and len(routes) < inst.max_vehicles:
        route: Route = []
        while True:
            last = route[-1] if route else 0
            candidates = sorted(unvisited, key=lambda c: (inst.dist[last][c], c))
            nxt = next((c for c in candidates if route_feasible(inst, [*route, c])), None)
            if nxt is None:
                break
            route.append(nxt)
            unvisited.remove(nxt)
        if not route:
            break
        routes.append(route)
    return Solution(routes, sorted(unvisited))


def two_opt(inst: Instance, route: Route) -> tuple[Route, bool]:
    """Intra-route 2-opt: reverse a segment when it shortens the route feasibly."""
    best, best_d, improved = route, route_distance(inst, route), False
    n = len(route)
    for i in range(n - 1):
        for j in range(i + 1, n):
            cand = best[:i] + best[i : j + 1][::-1] + best[j + 1 :]
            d = route_distance(inst, cand)
            if d < best_d - EPS and route_feasible(inst, cand):
                best, best_d, improved = cand, d, True
    return best, improved


def or_opt(inst: Instance, routes: list[Route], max_seg: int = 3) -> bool:
    """Move a segment of 1..max_seg customers to its best feasible position in any
    route (same or another). Applies the first improving move; returns True if one."""
    for a, ra in enumerate(routes):
        for seg_len in range(1, max_seg + 1):
            for i in range(len(ra) - seg_len + 1):
                seg = ra[i : i + seg_len]
                rest = ra[:i] + ra[i + seg_len :]
                if rest and not route_feasible(inst, rest):
                    continue  # pragma: no cover - removal never breaks time windows
                base = route_distance(inst, ra) - route_distance(inst, rest)
                for b, rb in enumerate(routes):
                    target = rest if a == b else rb
                    old_b = 0.0 if a == b else route_distance(inst, rb)
                    for pos in range(len(target) + 1):
                        for s in (seg, seg[::-1]):
                            cand = target[:pos] + s + target[pos:]
                            gain = base - (route_distance(inst, cand) - old_b)
                            if gain > EPS and route_feasible(inst, cand):
                                if a == b:
                                    routes[a] = cand
                                else:
                                    routes[a], routes[b] = rest, cand
                                return True
    return False


def local_search(inst: Instance, start: Solution, max_iter: int = 10_000) -> Solution:
    """Alternate 2-opt on each route and inter/intra or-opt until no move improves."""
    routes = [list(r) for r in start.routes]
    for _ in range(max_iter):
        changed = False
        for k, r in enumerate(routes):
            routes[k], imp = two_opt(inst, r)
            changed |= imp
        changed |= or_opt(inst, routes)
        routes = [r for r in routes if r]
        if not changed:
            break
    return Solution(routes, list(start.unserved))
