# VRP with time windows and capacity: formulation

## Sets and data

- Nodes V = {0, 1, …, n}; node 0 is the depot, C = {1, …, n} the customers.
- K: identical vehicles, |K| ≤ K_max, capacity Q [kg].
- d_ij: road distance [km] = haversine(i, j) · δ, with detour factor δ = 1.3
  (assumption: road network is about 30% longer than the great circle).
- t_ij = d_ij / s · 60: travel time [min] at constant speed s [km/h].
- q_i: demand [kg]; [a_i, b_i]: time window [min]; σ_i: service time [min].

Haversine on a sphere of radius R = 6371.0088 km:

    h = sin²(Δφ/2) + cos φ_i · cos φ_j · sin²(Δλ/2)
    d = 2 R · asin(√h)

## Decision variables

- x_ijk ∈ {0, 1}: vehicle k drives from i to j.
- T_ik ≥ 0: service start time of vehicle k at node i [min].

## Model

    minimise   Σ_k Σ_i Σ_j d_ij · x_ijk

subject to

1. each customer visited once: Σ_k Σ_j x_ijk = 1 for i ∈ C
2. flow conservation: Σ_i x_ihk = Σ_j x_hjk for all h, k
3. each used vehicle starts and ends at the depot: Σ_j x_0jk ≤ 1
4. capacity: Σ_i q_i Σ_j x_ijk ≤ Q for all k
5. time propagation: T_jk ≥ T_ik + σ_i + t_ij − M(1 − x_ijk)
6. time windows: a_i ≤ T_ik ≤ b_i (arriving early means waiting until a_i)
7. return to depot before b_0

## Heuristics implemented

**Baseline, nearest neighbour.** Start a vehicle at the depot; repeatedly append
the closest unvisited customer whose addition keeps the route feasible
(capacity, windows, return to depot). When no customer fits, close the route and
open the next vehicle. Customers that fit nowhere are reported as unserved.

**Improvement, local search** (first improvement, repeated until no move helps):

- *2-opt* (intra-route): reverse a segment i..j when the reversed route is
  shorter and still feasible. Reversal matters with time windows, so every
  candidate is re-checked.
- *or-opt* (intra- and inter-route): remove a chain of 1 to 3 consecutive
  customers and reinsert it, in either orientation, at the best position of any
  route. Inter-route moves can empty a route, which removes a vehicle.

Every accepted move keeps the solution feasible, so the improved solution is
never worse than the baseline. Neither heuristic proves optimality.
