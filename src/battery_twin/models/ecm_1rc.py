from dataclasses import dataclass

import numpy as np

from .ocv import SyntheticOCV


@dataclass(frozen=True)
class ECM1RCParameters:
    capacity_ah: float
    r0_ohm: float
    r1_ohm: float
    c1_farad: float

    def __post_init__(self) -> None:
        if self.capacity_ah <= 0:
            raise ValueError("capacity_ah must be > 0")
        if self.r0_ohm < 0 or self.r1_ohm <= 0 or self.c1_farad <= 0:
            raise ValueError("ECM resistances/capacitance are invalid")

    @property
    def capacity_c(self) -> float:
        return self.capacity_ah * 3600.0

    @property
    def tau1_s(self) -> float:
        return self.r1_ohm * self.c1_farad


@dataclass
class ECM1RCState:
    soc: float
    v1_v: float


class ECM1RC:
    """1-RC Thevenin ECM. Positive current means discharge."""

    def __init__(
        self,
        parameters: ECM1RCParameters,
        dt_s: float,
        ocv: SyntheticOCV | None = None,
    ) -> None:
        if dt_s <= 0:
            raise ValueError("dt_s must be > 0")
        self.p = parameters
        self.dt_s = dt_s
        self.ocv = ocv or SyntheticOCV()
        self.alpha1 = float(np.exp(-dt_s / self.p.tau1_s))

    def step(self, state: ECM1RCState, current_a: float) -> ECM1RCState:
        soc_next = state.soc - self.dt_s * current_a / self.p.capacity_c
        v1_next = (
            self.alpha1 * state.v1_v
            + self.p.r1_ohm * (1.0 - self.alpha1) * current_a
        )
        return ECM1RCState(
            soc=float(np.clip(soc_next, 0.0, 1.0)),
            v1_v=float(v1_next),
        )

    def terminal_voltage(self, state: ECM1RCState, current_a: float) -> float:
        return float(
            self.ocv.voltage(state.soc)
            - current_a * self.p.r0_ohm
            - state.v1_v
        )
