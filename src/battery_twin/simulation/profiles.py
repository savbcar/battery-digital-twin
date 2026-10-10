import numpy as np
from numpy.typing import NDArray


def dynamic_current_profile(
    duration_s: int,
    dt_s: float,
    seed: int = 42,
) -> NDArray[np.float64]:
    """
    Deterministic WLTP-like synthetic current profile.

    It is not a WLTP certification trace. It intentionally contains rests,
    discharge pulses, regenerative-charge events and piecewise-random loads.
    Positive current = discharge; negative current = charge.
    """
    n = int(duration_s / dt_s) + 1
    rng = np.random.default_rng(seed)
    current = np.zeros(n, dtype=float)

    # Start with repeatable pulse/rest sections.
    def put(start: int, end: int, value: float) -> None:
        i0 = int(start / dt_s)
        i1 = min(int(end / dt_s), n)
        current[i0:i1] = value

    put(60, 180, 2.0)
    put(180, 240, 0.0)
    put(240, 360, 5.0)
    put(360, 420, -2.0)
    put(420, 540, 3.0)
    put(540, 600, 0.0)

    # Piecewise-random section after 600 s.
    start_idx = int(600 / dt_s)
    block = max(1, int(15 / dt_s))
    levels = np.array([-3.0, -1.5, 0.0, 1.0, 2.5, 4.0, 6.0, 8.0])
    probs = np.array([0.05, 0.07, 0.15, 0.13, 0.20, 0.18, 0.14, 0.08])

    for i in range(start_idx, n, block):
        value = float(rng.choice(levels, p=probs))
        current[i : min(i + block, n)] = value

    return current
