% MATLAB Script: Support Reactions for Roadside Advertisement Hoarding
% Calculated for Point A (Base of the pole)

%% 1. Input Data
h = 2;              % Height of the pole (m)
W = 600;            % Weight of the structure (N)
F_wind = 363.68;    % Wind force (N) - acting horizontally at 0 degrees

% Tensions and their angles (referenced from +x axis)
T1 = 1401.09;      theta_T1 = 140; % Angle theta 2
T2 = 9000;          theta_T2 = 30;  % Angle theta 1
T  = 9706.26;       theta_T  = 198; % Angle theta 4

%% 2. Resolve Forces into X and Y Components
% Using cosd and sind for degrees
T1x = T1 * cosd(theta_T1);
T1y = T1 * sind(theta_T1);

T2x = T2 * cosd(theta_T2);
T2y = T2 * sind(theta_T2);

Tx = T * cosd(theta_T);
Ty = T * sind(theta_T);

% Wind is purely horizontal (+x)
Fwx = F_wind;
Fwy = 0;

%% 3. Apply Equilibrium Equations (Sum of Forces = 0)
% Sum of Horizontal Forces: HA + T1x + T2x + Tx + Fwx = 0
HA = -(T1x + T2x + Tx + Fwx);

% Sum of Vertical Forces: VA + T1y + T2y + Ty - W = 0
VA = -(T1y + T2y + Ty - W);

%% 4. Apply Moment Equilibrium at Point A (Sum of Moments = 0)
% Moment arm for forces at the top is 'h'. 
% Only horizontal components create a moment about the base A.
% Counter-Clockwise is positive.
% MA + (Sum of horizontal forces * height) = 0
total_Fx_top = T1x + T2x + Tx + Fwx;
MA = -(total_Fx_top * h);

%% 5. Display Results
fprintf('--- Support Reactions at Point A ---\n');
fprintf('Horizontal Reaction (HA): %.2f N\n', HA);
fprintf('Vertical Reaction (VA):   %.2f N\n', VA);
fprintf('Moment Reaction (MA):     %.2f N-m\n', MA);

% Simple visualization of force components
bar([T1x, T2x, Tx, Fwx; T1y, T2y, Ty, -W]');
xticklabels({'T1', 'T2', 'T', 'Wind/Weight'});
legend('X-Component', 'Y-Component');
title('Force Components Acting on the Pole');
ylabel('Force (N)');grid on;