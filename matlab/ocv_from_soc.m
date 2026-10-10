function [v, dvdz] = ocv_from_soc(z)
%OCV_FROM_SOC Synthetic nonlinear OCV-SOC relationship.
% Not claimed to represent a production cell.
z = min(max(z, 0.0), 1.0);
v = 3.0 + 1.05*z + 0.10*z.^2 - 0.05*z.^3;
dvdz = 1.05 + 0.20*z - 0.15*z.^2;
end
