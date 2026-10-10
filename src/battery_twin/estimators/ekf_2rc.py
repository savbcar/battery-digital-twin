from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from battery_twin.models.ecm_2rc import ECM2RCParameters
from battery_twin.models.ocv import SyntheticOCV


@dataclass(frozen=True)
class EKFConfig:
    q_soc: float = 2e-8
    q_v1: float = 2e-6
    q_v2: float = 1e-6
    r_voltage: float = 1e-4
    p0_soc: float = 2.5e-3
    p0_v1: float = 4e-4
    p0_v2: float = 4e-4


class EKF2RC:
    """
    Extended Kalman Filter for x = [SOC, V1, V2]^T.

    Nonlinearity enters through OCV(SOC) in the measurement equation.
    """

    def __init__(
        self,
        parameters: ECM2RCParameters,
        dt_s: float,
        initial_soc: float,
        config: EKFConfig | None = None,
        ocv: SyntheticOCV | None = None,
    ) -> None:
        self.p = parameters
        self.dt_s = dt_s
        self.cfg = config or EKFConfig()
        self.ocv = ocv or SyntheticOCV()

        self.a1 = float(np.exp(-dt_s / self.p.tau1_s))
        self.a2 = float(np.exp(-dt_s / self.p.tau2_s))

        self.x: NDArray[np.float64] = np.array(
            [initial_soc, 0.0, 0.0], dtype=float
        )

        self.P: NDArray[np.float64] = np.diag(
            [self.cfg.p0_soc, self.cfg.p0_v1, self.cfg.p0_v2]
        ).astype(float)

        self.Q: NDArray[np.float64] = np.diag(
            [self.cfg.q_soc, self.cfg.q_v1, self.cfg.q_v2]
        ).astype(float)

        self.R = float(self.cfg.r_voltage)

        self.F: NDArray[np.float64] = np.diag(
            [1.0, self.a1, self.a2]
        ).astype(float)

        self.B: NDArray[np.float64] = np.array(
            [
                -dt_s / self.p.capacity_c,
                self.p.r1_ohm * (1.0 - self.a1),
                self.p.r2_ohm * (1.0 - self.a2),
            ],
            dtype=float,
        )

    def predict(self, current_a: float) -> None:
        self.x = self.F @ self.x + self.B * current_a
        self.x[0] = np.clip(self.x[0], 0.0, 1.0)
        self.P = self.F @ self.P @ self.F.T + self.Q

    def measurement_function(self, current_a: float) -> float:
        soc, v1, v2 = self.x
        return float(
            self.ocv.voltage(soc)
            - current_a * self.p.r0_ohm
            - v1
            - v2
        )

    def measurement_jacobian(self) -> NDArray[np.float64]:
        soc = float(self.x[0])
        return np.array(
            [[self.ocv.derivative(soc), -1.0, -1.0]],
            dtype=float,
        )

    def update(self, voltage_v: float, current_a: float) -> tuple[float, float]:
        H = self.measurement_jacobian()
        z_hat = self.measurement_function(current_a)
        innovation = float(voltage_v - z_hat)

        S = float((H @ self.P @ H.T)[0, 0] + self.R)
        K = (self.P @ H.T) / S

        self.x = self.x + K[:, 0] * innovation
        self.x[0] = np.clip(self.x[0], 0.0, 1.0)

        identity = np.eye(3)
        ikh = identity - K @ H

        # Joseph stabilized covariance update.
        self.P = ikh @ self.P @ ikh.T + (K @ K.T) * self.R
        self.P = 0.5 * (self.P + self.P.T)

        return innovation, S

    @property
    def soc(self) -> float:
        return float(self.x[0])
