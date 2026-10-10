from dataclasses import dataclass

import numpy as np


@dataclass
class CoulombCounter:
    capacity_ah: float
    dt_s: float
    soc: float

    def step(self, current_a: float) -> float:
        self.soc -= self.dt_s * current_a / (3600.0 * self.capacity_ah)
        self.soc = float(np.clip(self.soc, 0.0, 1.0))
        return self.soc
