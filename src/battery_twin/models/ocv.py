from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SyntheticOCV:
    """
    Smooth synthetic OCV-SOC relation used for algorithm development.

    This is deliberately NOT claimed to represent a specific production cell.
    The derivative is analytic, which makes EKF linearization transparent.
    """

    def voltage(self, soc: float | np.ndarray) -> float | np.ndarray:
        s = np.asarray(soc, dtype=float)
        s = np.clip(s, 0.0, 1.0)
        v = 3.0 + 1.05 * s + 0.10 * s**2 - 0.05 * s**3
        return float(v) if np.ndim(soc) == 0 else v

    def derivative(self, soc: float | np.ndarray) -> float | np.ndarray:
        s = np.asarray(soc, dtype=float)
        s = np.clip(s, 0.0, 1.0)
        dv = 1.05 + 0.20 * s - 0.15 * s**2
        return float(dv) if np.ndim(soc) == 0 else dv
