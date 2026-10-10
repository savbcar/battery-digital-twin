# Aggressive Technical Interview — Project 1

Use this only after you can derive the equations yourself.

## Battery physics

1. Define SOC without using the word "percentage".
2. Why is terminal voltage not a direct SOC sensor?
3. What physical behavior does R0 reproduce?
4. Why is it dangerous to claim R1 is literally "charge-transfer resistance"?
5. What is the meaning of tau = R*C?
6. Sketch terminal voltage after a discharge-current step and after the current is removed.
7. At constant current, prove that V1 tends to I*R1.

## Discretization

8. Derive SOC[k+1] from dSOC/dt = -I/Q.
9. Where does the factor 3600 come from?
10. Derive the exact ZOH RC update.
11. Why did you prefer exact ZOH over forward Euler?
12. What breaks if the sample interval becomes comparable to dynamics you omitted?

## State space

13. Write the complete 2-RC state vector.
14. Write F and B from memory.
15. Write the nonlinear voltage measurement equation.
16. Which part of this model is nonlinear?
17. Is the state-transition model itself nonlinear in this implementation?

## EKF

18. Derive prediction x- and P-.
19. What is the innovation?
20. Derive H.
21. Why does H contain dOCV/dSOC?
22. What happens where dOCV/dSOC is very small?
23. Derive K.
24. What does a large K mean physically?
25. Explain Q without saying "tuning matrix".
26. Explain R without saying "sensor noise" only.
27. What happens if Q is much too small?
28. What happens if Q is much too large?
29. What happens if R is too small?
30. What happens if R is too large?
31. Why use the Joseph covariance update?
32. Name at least six EKF divergence mechanisms.

## Validation

33. Define RMSE and MAE.
34. Why report both?
35. Why is maximum error important?
36. Why is steady-state error useful?
37. How did you define convergence time?
38. Why is synthetic data useful?
39. Why is synthetic-only validation insufficient for production claims?
40. Why is a low voltage RMSE not sufficient evidence of low SOC error?

## Sensitivity

41. Predict the effect of capacity underestimation before showing the plot.
42. Predict the effect of R0 mismatch during current pulses.
43. How should increasing voltage noise affect EKF tuning?
44. Why can bad initial SOC still converge?
45. When might it fail to converge?
46. What is the effect of sample time?
47. Why do two RC branches not automatically make the model "more physical"?

## Software engineering

48. Why separate plant, sensors and estimator?
49. What physics invariants do the unit tests enforce?
50. Why deterministic random seeds?
51. What does CI protect against?
52. Why log run configuration and metrics in SQL?
53. What does Docker add here?
54. What would you change before deploying to an embedded BMS?

## Production gap

55. Explain temperature dependence.
56. Explain hysteresis.
57. Explain SOH/capacity fade.
58. Explain current-sensor bias.
59. Explain cell-to-cell variation in a pack.
60. What would ISO 26262 / production validation change about your development process?

If you cannot answer a question precisely, go back to `docs/ENGINEERING_NOTES.md`
and the implementation. Do not memorize slogans.
