% --- INITIAL CONFIGURATION ---
clear; clc; close all;

% Define the port configured in Python to send data
localPort = 5005;

% Create the UDP receiver object (available in newer MATLAB versions)
try
    udpReceiver = udpport("LocalPort", localPort);
    fprintf('MATLAB started and listening on port %d...\n', localPort);
catch
    error('Error: Port %d is already occupied or MATLAB lacks permissions.', localPort);
end

% --- GRAPHICAL CONFIGURATION (INTERFACE) ---
fig = figure('Name', 'Gesture Trajectory Monitor', 'Color', [0.1 0.1 0.1]);
ax = axes('Parent', fig, 'Color', [0.15 0.15 0.15], 'XColor', 'w', 'YColor', 'w');
hold on;
grid on;

% Set limits (MediaPipe sends values between 0 and 1)
axis([0 1 0 1]);
title('Real-Time Finger Trajectory', 'Color', 'w');
xlabel('X Coordinate (Screen)', 'Color', 'w');
ylabel('Y Coordinate (Screen)', 'Color', 'w');

% Create the current position object (a bright red circle)
hCurrentPoint = plot(0, 0, 'ro', 'MarkerSize', 12, 'MarkerFaceColor', 'r', 'LineWidth', 2);

% Create a "trail" object left by the finger
hTrail = animatedline('Color', [0 0.7 1], 'LineWidth', 1.5, 'MaximumNumPoints', 50);

% --- DATA RECEPTION LOOP ---
fprintf('Move your finger in front of the camera to see the data...\n');

% Run as long as the graphic window is open
while ishandle(fig)
    % Check if data packets have arrived from Python
    if udpReceiver.NumBytesAvailable > 0
        % Read received data as a string (e.g., "0.1234,0.5678")
        rawData = read(udpReceiver, udpReceiver.NumBytesAvailable, "string");
        
        % Split the text using the comma as a separator
        parts = strsplit(rawData, ',');
        
        if length(parts) == 2
            % Convert text to numbers
            x = str2double(parts(1));
            y = 1 - str2double(parts(2)); % Invert Y because 0 is Top in video coordinates
            
            % Update the red point position
            set(hCurrentPoint, 'XData', x, 'YData', y);
            
            % Add the new point to the finger's "trail"
            addpoints(hTrail, x, y);
            
            % Force MATLAB to redraw immediately
            drawnow limitrate;
        end
    end
    
    % Small pause to prevent CPU overloading
    pause(0.01);
end

% --- RESOURCE CLEANUP ---
clear udpReceiver;
fprintf('UDP connection closed.\n');