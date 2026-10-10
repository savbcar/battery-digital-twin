function out = ekf_soc_2rc(current_A, voltage_V, dt_s, initial_soc, p)
%EKF_SOC_2RC Manual EKF, state x = [SOC; V1; V2].

n = numel(current_A);

a1 = exp(-dt_s/(p.R1*p.C1));
a2 = exp(-dt_s/(p.R2*p.C2));

F = diag([1, a1, a2]);
B = [-dt_s/p.Q_C;
     p.R1*(1-a1);
     p.R2*(1-a2)];

Q = diag([2e-8, 2e-6, 1e-6]);
R = 1e-4;
P = diag([2.5e-3, 4e-4, 4e-4]);

x = [initial_soc; 0; 0];

X = zeros(n,3);
innovation = zeros(n,1);

for k = 1:n
    if k > 1
        x = F*x + B*current_A(k-1);
        x(1) = min(max(x(1),0),1);
        P = F*P*F' + Q;
    end

    [ocv, docv] = ocv_from_soc(x(1));
    zhat = ocv - current_A(k)*p.R0 - x(2) - x(3);
    H = [docv, -1, -1];

    y = voltage_V(k) - zhat;
    S = H*P*H' + R;
    K = P*H'/S;

    x = x + K*y;
    x(1) = min(max(x(1),0),1);

    I3 = eye(3);
    P = (I3-K*H)*P*(I3-K*H)' + K*R*K';
    P = 0.5*(P+P');

    X(k,:) = x';
    innovation(k) = y;
end

out.soc = X(:,1);
out.v1 = X(:,2);
out.v2 = X(:,3);
out.innovation = innovation;
end
