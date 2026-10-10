function build_simulink_1rc()
%BUILD_SIMULINK_1RC Programmatically builds a transparent 1-RC model.
%
% States:
% SOC[k+1] = SOC[k] - dt/(3600*Q_Ah) * I[k]
% V1[k+1]  = alpha*V1[k] + R1*(1-alpha)*I[k]
%
% The generated model focuses on state dynamics. OCV and terminal-voltage
% reconstruction are kept in MATLAB in this first Simulink artifact so every
% block remains easy to inspect in an interview.

model = 'battery_1rc_generated';
if bdIsLoaded(model)
    close_system(model, 0);
end

new_system(model);
open_system(model);

dt = 1.0;
Q_Ah = 3.0;
R1 = 0.010;
C1 = 2400.0;
alpha = exp(-dt/(R1*C1));

add_block('simulink/Sources/In1', [model '/Current_A'], ...
    'Position', [30 90 60 110]);

add_block('simulink/Math Operations/Gain', [model '/SOC_Input_Gain'], ...
    'Gain', num2str(-dt/(3600*Q_Ah), 16), ...
    'Position', [100 40 190 70]);

add_block('simulink/Discrete/Unit Delay', [model '/SOC_z1'], ...
    'InitialCondition', '0.85', ...
    'SampleTime', num2str(dt), ...
    'Position', [280 30 330 70]);

add_block('simulink/Math Operations/Sum', [model '/SOC_Sum'], ...
    'Inputs', '++', ...
    'Position', [220 35 245 65]);

add_line(model, 'Current_A/1', 'SOC_Input_Gain/1');
add_line(model, 'SOC_Input_Gain/1', 'SOC_Sum/2');
add_line(model, 'SOC_z1/1', 'SOC_Sum/1');
add_line(model, 'SOC_Sum/1', 'SOC_z1/1');

add_block('simulink/Math Operations/Gain', [model '/V1_Input_Gain'], ...
    'Gain', num2str(R1*(1-alpha), 16), ...
    'Position', [100 135 190 165]);

add_block('simulink/Math Operations/Gain', [model '/V1_State_Gain'], ...
    'Gain', num2str(alpha, 16), ...
    'Position', [360 135 440 165]);

add_block('simulink/Discrete/Unit Delay', [model '/V1_z1'], ...
    'InitialCondition', '0', ...
    'SampleTime', num2str(dt), ...
    'Position', [280 125 330 165]);

add_block('simulink/Math Operations/Sum', [model '/V1_Sum'], ...
    'Inputs', '++', ...
    'Position', [220 130 245 160]);

add_line(model, 'Current_A/1', 'V1_Input_Gain/1');
add_line(model, 'V1_Input_Gain/1', 'V1_Sum/2');
add_line(model, 'V1_z1/1', 'V1_State_Gain/1');
add_line(model, 'V1_State_Gain/1', 'V1_Sum/1');
add_line(model, 'V1_Sum/1', 'V1_z1/1');

add_block('simulink/Sinks/Out1', [model '/SOC'], ...
    'Position', [480 40 510 60]);
add_block('simulink/Sinks/Out1', [model '/V1_V'], ...
    'Position', [480 135 510 155]);

add_line(model, 'SOC_z1/1', 'SOC/1');
add_line(model, 'V1_z1/1', 'V1_V/1');

set_param(model, 'SolverType', 'Fixed-step');
set_param(model, 'Solver', 'FixedStepDiscrete');
set_param(model, 'FixedStep', num2str(dt));

save_system(model, fullfile(pwd, [model '.slx']));
open_system(model);
end
