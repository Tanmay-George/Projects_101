% Project: Static Analysis of Concurrent Forces & Support Reactions
% Written by: Tanmay Jethro George (2BTPHY-D)
% This script solves for T, T1, Resultant, and Support Reactions (HA, VA, MA)

clear; clc;

%% STEP 1: User Inputs for Knowns
T2 = 9000;          % Magnitude of Tension T2 (N)
F_wind = 363.68;    % Magnitude of Wind Force (N)
W = 600;            % Magnitude of Weight W (N)
h = 2;              % Height of the pole (m)

% Input Angles (Degrees)
theta1 = 30;        % T2 from +x axis
theta2 = 140;       % T1 from +x axis
theta4 = 198;       % T from +x axis

%% STEP 2: Trigonometry and Known Force Sums
% Standard angles for Wind (0 deg) and Weight (270 deg)
rw = deg2rad(0);
rW = deg2rad(270);

% Calculate known horizontal (Cx) and vertical (Cy) components
Cx = T2*cosd(theta1) + F_wind*cos(rw) + W*cos(rW);
Cy = T2*sind(theta1) + F_wind*sin(rw) + W*sin(rW);

% Convert unknown angles to radians for calculation
r2 = deg2rad(theta2); % Angle for T1
r4 = deg2rad(theta4); % Angle for T

%% STEP 3: Solving for Unknowns (T1 and T)
% Rearranging Sum Fx = 0 and Sum Fy = 0
T1 = (Cy*cos(r4) - Cx*sin(r4)) / (cos(r2)*sin(r4) - sin(r2)*cos(r4));
T = -(Cx + T1*cos(r2)) / cos(r4);

%% STEP 4: Resultant and Inclination Calculation
Rx = T1*cos(r2) + T*cos(r4) + Cx;
Ry = T1*sin(r2) + T*sin(r4) + Cy;

Resultant = sqrt(Rx^2 + Ry^2);
Alpha = rad2deg(atan2(Ry, Rx));
if Alpha < 0; Alpha = Alpha + 360; end

%% STEP 5: Support Reactions at Point A (Base)
% Reaction forces balance the external forces
% HA = - (Sum of all X forces)
% VA = - (Sum of all Y forces)

HA = -(T2*cosd(theta1) + T1*cosd(theta2) + T*cosd(theta4) + F_wind);
VA = -(T2*sind(theta1) + T1*sind(theta2) + T*sind(theta4) - W);

% MA = Sum of moments about A. 
% Only horizontal forces at height 'h' create a moment about the base.
% Assuming Counter-Clockwise is positive for the reaction MA.
horizontal_force_top = T2*cosd(theta1) + T1*cosd(theta2) + T*cosd(theta4) + F_wind;
MA = -(horizontal_force_top * h);

%% STEP 6: Display Final Results
fprintf('\n--- Final Engineering Analysis ---\n');
fprintf('Calculated Tension T1: %.2f N\n', T1);
fprintf('Calculated Tension T:  %.2f N\n', T);
fprintf('Resultant Magnitude:   %.4f N\n', Resultant);
fprintf('Inclination (Alpha):   %.2f degrees\n', Alpha);

fprintf('\n--- Support Reactions at Base A ---\n');
fprintf('Horizontal Reaction (HA): %.2f N\n', HA);
fprintf('Vertical Reaction   (VA): %.2f N\n', VA);
fprintf('Moment Reaction     (MA): %.2f Nm\n', MA);