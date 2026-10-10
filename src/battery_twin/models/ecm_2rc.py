from dataclasses import dataclass

import numpy as np

from .ocv import SyntheticOCV


@dataclass(frozen=True)
class ECM2RCParameters:
    capacity_ah: float
    r0_ohm: float
    r1_ohm: float
    c1_farad: float
    r2_ohm: float
    c2_farad: float

    def __post_init__(self) -> None:
        positive = (
            self.capacity_ah > 0
            and self.r1_ohm > 0
            and self.c1_farad > 0
            and self.r2_ohm > 0
            and self.c2_farad > 0
        )
        if not positive or self.r0_ohm < 0:
            raise ValueError("Invalid 2-RC parameters")

    @property
    def capacity_c(self) -> float:
        return self.capacity_ah * 3600.0

    @property
    def tau1_s(self) -> float:
        return self.r1_ohm * self.c1_farad

    @property
    def tau2_s(self) -> float:
        return self.r2_ohm * self.c2_farad


@dataclass
class ECM2RCState:
    soc: float
    v1_v: float
    v2_v: float


class ECM2RC:
    """2-RC Thevenin ECM with exact ZOH discretization."""

    def __init__(
        self,
        parameters: ECM2RCParameters,
        dt_s: float,
        ocv: SyntheticOCV | None = None,
    ) -> None:
        if dt_s <= 0:
            raise ValueError("dt_s must be > 0")
        self.p = parameters
        self.dt_s = dt_s
        self.ocv = ocv or SyntheticOCV()
        self.alpha1 = float(np.exp(-dt_s / self.p.tau1_s))
        self.alpha2 = float(np.exp(-dt_s / self.p.tau2_s))

    def step(self, state: ECM2RCState, current_a: float) -> ECM2RCState:
        soc_next = state.soc - self.dt_s * current_a / self.p.capacity_c
        v1_next = (
            self.alpha1 * state.v1_v
            + self.p.r1_ohm * (1.0 - self.alpha1) * current_a
        )
        v2_next = (
            self.alpha2 * state.v2_v
            + self.p.r2_ohm * (1.0 - self.alpha2) * current_a
        )
        return ECM2RCState(
            soc=float(np.clip(soc_next, 0.0, 1.0)),
            v1_v=float(v1_next),
            v2_v=float(v2_next),
        )

    def terminal_voltage(self, state: ECM2RCState, current_a: float) -> float:
        return float(
            self.ocv.voltage(state.soc)
            - current_a * self.p.r0_ohm
            - state.v1_v
            - state.v2_v
        )
