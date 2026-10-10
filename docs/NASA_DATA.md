# Public-data extension

The repository baseline deliberately uses synthetic data because that provides
known ground-truth SOC and exact repeatability for estimator verification.

A measured-data extension should then be used to test model mismatch and
real-sensor behavior.

Recommended public source:

NASA Open Data Portal — Li-ion Battery Aging Datasets
https://data.nasa.gov/dataset/li-ion-battery-aging-datasets

The dataset contains measured charge/discharge experiments from commercial
18650 lithium-ion cells collected on a custom battery prognostics testbed.

Important engineering warning:
Do not treat the dataset's measured current integral as perfect "true SOC"
without documenting the reference definition, sign convention, capacity used,
cycle boundaries and sensor assumptions.

Suggested workflow:
1. Obtain the dataset from NASA's official source.
2. Select one discharge cycle.
3. Convert the native data to CSV.
4. Map time/current/voltage columns with `battery_twin.data.load_timeseries_csv`.
5. Verify current polarity.
6. Estimate usable capacity for that cycle.
7. Build an OCV-SOC lookup from appropriate characterization/rest data rather
   than reusing the synthetic OCV polynomial.
8. Identify R0/R1/C1/R2/C2 from pulse/relaxation behavior or optimization.
9. Run the EKF.
10. Report measured-voltage residuals and clearly distinguish reference SOC
    from directly measured quantities.
