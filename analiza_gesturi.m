% --- CONFIGURARE INITIALA ---
clear; clc; close all;

% Definim portul pe care am configurat Python sa trimita datele
portLocal = 5005;

% Cream obiectul de receptie UDP (disponibil in versiunile noi de MATLAB)
try
    receptorUdp = udpport("LocalPort", portLocal);
    fprintf('MATLAB a pornit si asculta pe portul %d...\n', portLocal);
catch
    error('Eroare: Portul %d este deja ocupat sau MATLAB nu are permisiuni.', portLocal);
end

% --- CONFIGURARE GRAFICA (INTERFATA) ---
fig = figure('Name', 'Monitorizare Traiectorie Gesturi', 'Color', [0.1 0.1 0.1]);
ax = axes('Parent', fig, 'Color', [0.15 0.15 0.15], 'XColor', 'w', 'YColor', 'w');
hold on;
grid on;

% Setam limitele (MediaPipe trimite valori intre 0 si 1)
axis([0 1 0 1]);
title('Traiectoria Degetului in Timp Real', 'Color', 'w');
xlabel('Coordonata X (Ecran)', 'Color', 'w');
ylabel('Coordonata Y (Ecran)', 'Color', 'w');

% Cream obiectul pentru punctul curent (un cerc rosu stralucitor)
hPunctCurent = plot(0, 0, 'ro', 'MarkerSize', 12, 'MarkerFaceColor', 'r', 'LineWidth', 2);

% Cream un obiect pentru "urma" (trail) lasata de deget
hUrma = animatedline('Color', [0 0.7 1], 'LineWidth', 1.5, 'MaximumNumPoints', 50);

% --- BUCALA DE RECEPTIE DATE ---
fprintf('Misca degetul in fata camerei pentru a vedea datele...\n');

% Ruleaza cat timp fereastra grafica este deschisa
while ishandle(fig)
    % Verificam daca au sosit pachete de date de la Python
    if receptorUdp.NumBytesAvailable > 0
        % Citim datele primite sub forma de string (ex: "0.1234,0.5678")
        dateRaw = read(receptorUdp, receptorUdp.NumBytesAvailable, "string");
        
        % Despartim textul folosind virgula ca separator
        parti = strsplit(dateRaw, ',');
        
        if length(parti) == 2
            % Convertim textul in numere
            x = str2double(parti(1));
            y = 1 - str2double(parti(2)); % Inversam Y deoarece in video 0 este Sus
            
            % Actualizam pozitia punctului rosu
            set(hPunctCurent, 'XData', x, 'YData', y);
            
            % Adaugam punctul nou la "urma" degetului
            addpoints(hUrma, x, y);
            
            % Fortam MATLAB sa redeseneze imediat
            drawnow limitrate;
        end
    end
    
    % Mica pauza pentru a nu suprasolicita procesorul
    pause(0.01);
end

% --- ELIBERARE RESURSE ---
clear receptorUdp;
fprintf('Conexiunea UDP a fost inchisa.\n');