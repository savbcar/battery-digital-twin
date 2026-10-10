clear; clc; close all;

rng(42);

p = battery_params();
dt = 1.0;
duration = 1800;
t = (0:dt:duration)';
n = numel(t);

I = zeros(n,1);
I(t>=60 & t<180) = 2;
I(t>=240 & t<360) = 5;
I(t>=360 & t<420) = -2;
I(t>=420 & t<540) = 3;

levels = [-3 -1.5 0 1 2.5 4 6 8];
for k = find(t>=600,1):15:n
    value = levels(randi(numel(levels)));
    I(k:min(k+14,n)) = value;
end

truth = simulate_2rc(I, dt, 0.85, p);

voltage_measured = truth.voltage + 0.008*randn(n,1);
current_measured = I + 0.05*randn(n,1);

est = ekf_soc_2rc(current_measured, voltage_measured, dt, 0.70, p);

soc_error = est.soc - truth.soc;
soc_rmse_pct = 100*sqrt(mean(soc_error.^2));
fprintf('SOC RMSE = %.3f %%\n', soc_rmse_pct);

figure;
plot(t, 100*truth.soc, 'LineWidth', 1.5); hold on;
plot(t, 100*est.soc, '--', 'LineWidth', 1.5);
xlabel('Time [s]'); ylabel('SOC [%]');
legend('True','EKF'); grid on;
title('MATLAB 2-RC EKF SOC Estimation');

figure;
plot(t, truth.voltage, 'LineWidth', 1.2); hold on;
plot(t, voltage_measured, '.');
xlabel('Time [s]'); ylabel('Voltage [V]');
legend('True','Measured'); grid on;
title('Battery Terminal Voltage');
