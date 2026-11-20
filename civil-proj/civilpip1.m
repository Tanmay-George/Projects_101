% Project-1: Analysis of Roadside Advertisement Hoarding
% Student: Tanmay Jethro George (2BTPHY-D)
% This script solves for T, T1, Resultant, and Support Reactions HA, VA, MA.

clear; clc;

%% 1. Input Known Values
T2 = 9000;          % Magnitude of Tension T2 (N)
F_wind = 363.68;    % Magnitude of Wind Force (N)
W = 600;            % Magnitude of Weight W (N)
h = 2;              % Height of the pole from ground (m)

% Angles in degrees (measured from the positive x-axis)
theta1 = 30;        % Angle for T2
theta2 = 140;       % Angle for T1
theta4 = 198;       % Angle for T

%% 2. Find Unknown Forces (T1 and T) using Substitution Method
% Standard angles for Wind (0 deg) and Weight (270 deg)
rw = deg2rad(0);
rW = deg2rad(270);

% Calculate known horizontal (Cx) and vertical (Cy) sums
Cx = T2*cosd(theta1) + F_wind*cos(rw) + W*cos(rW);
Cy = T2*sind(theta1) + F_wind*sin(rw) + W*sin(rW);

% Convert unknown angles to radians for precision
r2 = deg2rad(theta2); 
r4 = deg2rad(theta4); 

% Solving the system of equations derived from Sum Fx = 0 and Sum Fy = 0
T1 = (Cy*cos(r4) - Cx*sin(r4)) / (cos(r2)*sin(r4) - sin(r2)*cos(r4));
T = -(Cx + T1*cos(r2)) / cos(r4);

%% 3. Calculate Resultant and Direction
Rx = T1*cos(r2) + T*cos(r4) + Cx;
Ry = T1*sin(r2) + T*sin(r4) + Cy;

Resultant = sqrt(Rx^2 + Ry^2);
Alpha = rad2deg(atan2(Ry, Rx));
if Alpha < 0; Alpha = Alpha + 360; end

%% 4. Calculate Support Reactions at Point A (Base)
% HA (Horizontal Reaction): Counteracts the sum of all external horizontal forces
HA = -(T2*cosd(theta1) + T1*cosd(theta2) + T*cosd(theta4) + F_wind);

% VA (Vertical Reaction): Counteracts the sum of all external vertical forces
% Note: Weight is included here as it acts on the structure
VA = -(T2*sind(theta1) + T1*sind(theta2) + T*sind(theta4) - W);

% MA (Moment Reaction): Counteracts the torque at the base
% Calculated as: -(Total Horizontal Force at Top * Height)
Fx_top = T2*cosd(theta1) + T1*cosd(theta2) + T*cosd(theta4) + F_wind;
MA = -(Fx_top * h);

%% 5. Display Results
fprintf('\n--- Step 1: Force Analysis ---\n');
fprintf('Calculated Tension T1: %.2f N\n', T1);
fprintf('Calculated Tension T:  %.2f N\n', T);
fprintf('Resultant Magnitude:   %.4f N\n', Resultant);
fprintf('Inclination (Alpha):   %.2f degrees\n', Alpha);

fprintf('\n--- Step 2: Support Reactions at Base A ---\n');
fprintf('Horizontal Reaction (HA): %8.2f N\n', HA);
fprintf('Vertical Reaction   (VA): %8.2f N\n', VA);
fprintf('Moment Reaction     (MA): %8.2f Nm\n', MA);