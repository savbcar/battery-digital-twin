function p = battery_params()
%BATTERY_PARAMS Nominal 2-RC parameters matching the Python demo.
p.capacity_Ah = 3.0;
p.Q_C = p.capacity_Ah * 3600.0;
p.R0 = 0.012;
p.R1 = 0.010;
p.C1 = 2400.0;
p.R2 = 0.006;
p.C2 = 20000.0;
end
