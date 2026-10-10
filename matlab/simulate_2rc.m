function T = simulate_2rc(current_A, dt_s, initial_soc, p)
%SIMULATE_2RC Exact-ZOH 2-RC battery simulation.
n = numel(current_A);
soc = zeros(n,1);
v1 = zeros(n,1);
v2 = zeros(n,1);
voltage = zeros(n,1);

soc(1) = initial_soc;

a1 = exp(-dt_s/(p.R1*p.C1));
a2 = exp(-dt_s/(p.R2*p.C2));

for k = 1:n
    ocv = ocv_from_soc(soc(k));
    voltage(k) = ocv - current_A(k)*p.R0 - v1(k) - v2(k);

    if k < n
        soc(k+1) = soc(k) - dt_s*current_A(k)/p.Q_C;
        soc(k+1) = min(max(soc(k+1), 0.0), 1.0);

        v1(k+1) = a1*v1(k) + p.R1*(1-a1)*current_A(k);
        v2(k+1) = a2*v2(k) + p.R2*(1-a2)*current_A(k);
    end
end

time_s = (0:n-1)' * dt_s;
T = table(time_s, current_A(:), soc, v1, v2, voltage);
end
