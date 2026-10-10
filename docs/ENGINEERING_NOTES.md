# Engineering Notes

## Sign convention

Positive current means discharge.

Therefore

dSOC/dt = -I / Q

and charging current is negative.

## 1-RC continuous model

dSOC/dt = -I / Q

dV1/dt = -V1/(R1 C1) + I/C1

Vt = OCV(SOC) - I R0 - V1

Under zero-order hold current input:

SOC[k+1] = SOC[k] - dt I[k] / Q

alpha1 = exp(-dt/(R1 C1))

V1[k+1] = alpha1 V1[k] + R1(1-alpha1) I[k]

## 2-RC extension

Add:

dV2/dt = -V2/(R2 C2) + I/C2

Vt = OCV(SOC) - I R0 - V1 - V2

The two RC branches approximate two characteristic polarization time scales.

## EKF state

x = [SOC, V1, V2]^T

Prediction:

x_k^- = F x_{k-1}^+ + B I_{k-1}

P_k^- = F P_{k-1}^+ F^T + Q

Measurement:

z_k = OCV(SOC_k) - I_k R0 - V1_k - V2_k + v_k

H_k = [dOCV/dSOC, -1, -1]

Innovation:

y_k = z_k - h(x_k^-, I_k)

Innovation covariance:

S_k = H_k P_k^- H_k^T + R

Kalman gain:

K_k = P_k^- H_k^T S_k^-1

Correction:

x_k^+ = x_k^- + K_k y_k

Covariance uses the Joseph form for improved numerical robustness.

## What Q and R mean

Q is process-noise covariance: uncertainty in the state-transition model.
Examples include capacity error, parameter drift, unmodelled temperature dependence,
hysteresis and omitted electrochemical dynamics.

R is measurement-noise covariance. Here it is the variance of terminal-voltage
measurement noise.

Larger Q makes the estimator less confident in the model and generally more
responsive to measurement corrections.

Larger R makes it less confident in the voltage measurement and generally more
dependent on model prediction.

Both are engineering tuning quantities, not arbitrary magic numbers. They should
be connected to model residuals, sensor characterization and validation data.

## Production limitations

This project is intentionally not a production BMS. Missing production features
include temperature-dependent parameters, cell-to-cell variation, hysteresis,
SOH/capacity co-estimation, parameter adaptation, current-sensor bias estimation,
fault handling, observability analysis over flat OCV regions, fixed-point/embedded
implementation, safety mechanisms and extensive validation against measured data.
