"""Great-circle distances."""

import math

EARTH_RADIUS_KM = 6371.0088  # mean Earth radius (IUGG), km


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def distance_matrix(points: list[tuple[float, float]], detour: float = 1.0) -> list[list[float]]:
    """Symmetric matrix of haversine km, scaled by a road detour factor (>= 1)."""
    if detour < 1.0:
        raise ValueError("detour factor must be >= 1")
    n = len(points)
    m = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = haversine_km(*points[i], *points[j]) * detour
            m[i][j] = m[j][i] = d
    return m
