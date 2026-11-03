# Fuel model

`route_optimizer.fuel` estimates fuel per route from the forces a vehicle must
overcome at constant speed on a flat road. It gives a lower bound for
comparing routes, not a calibrated consumption figure.

## 1. Forces

At constant speed v on level ground, the engine supplies a tractive force equal
to the resisting forces:

    F = Crr · m · g  +  ½ · ρ · Cd · A · v²

| Symbol | Meaning | Unit | Default (assumption) |
|---|---|---|---|
| F | tractive force at the wheels | N = kg·m/s² | computed |
| Crr | rolling resistance coefficient | dimensionless | 0.008 (truck tyres on asphalt) |
| m | vehicle mass = curb mass + payload on board | kg | curb 3,500 |
| g | standard gravity | m/s² | 9.80665 |
| ρ | air density | kg/m³ | 1.2 (about 20 °C, sea level) |
| Cd | aerodynamic drag coefficient | dimensionless | 0.6 (box body) |
| A | frontal area | m² | 6.0 |
| v | speed | m/s (input in km/h, v = km/h / 3.6) | 40 km/h |
| η | tank-to-wheel efficiency | dimensionless | 0.30 |
| LHV | lower heating value of diesel | MJ/L | 36.0 |

Unit check: Crr·m·g is kg·m/s² = N; ½·ρ·Cd·A·v² is (kg/m³)·m²·(m²/s²) = kg·m/s² = N.

## 2. Energy and fuel per kilometre

Work over 1 km is force times distance:

    E_wheel = F · 1000 m   [J/km]  =  F / 1000   [MJ/km]
    fuel    = E_wheel / (η · LHV)   [L/km]

## 3. Payload along a route

A delivery vehicle leaves the depot carrying the sum of the route's demand and
sheds each customer's demand at the stop. Leg k is driven at mass
m_k = m_curb + remaining payload, so

    route fuel = Σ_k d_k · fuel(m_k, v)       [L]

with d_k the leg distance in km. Visiting heavy drops early therefore saves a
little fuel, which the rolling term captures; the aerodynamic term depends only
on speed.

## 4. Hand-computed validation

m = 3,500 + 1,200 = 4,700 kg at 40 km/h (v = 11.111 m/s):

1. rolling: 0.008 · 4,700 · 9.80665 = 368.73 N
2. drag: 0.5 · 1.2 · 0.6 · 6.0 · 11.111² = 266.67 N
3. F = 635.40 N, E_wheel = 0.6354 MJ/km
4. fuel = 0.6354 / (0.30 · 36.0) = 0.0588 L/km = 5.88 L/100 km

Empty (3,500 kg): 5.01 L/100 km. `tests/test_geo_fuel.py` asserts the same
formula at 54 km/h and the load-shedding sum on a one-stop route.

## 5. Assumptions and limits

- Flat road, constant cruise speed, no wind. Acceleration after stops, braking,
  idling, grades, auxiliaries and cold starts are excluded, so real consumption of
  a delivery truck in city traffic is typically several times higher. Treat
  results as a relative comparison between routes, not as absolute litres.
- Coefficients are generic textbook-order values, not measurements of a
  specific vehicle.
- Speed is one constant for the whole network (40 km/h default).
