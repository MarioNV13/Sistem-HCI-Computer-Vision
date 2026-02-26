import cv2  # Biblioteca pentru procesare video
import mediapipe as mp  # Motorul de IA pentru detectarea mainii
import pyautogui  # Biblioteca pentru controlul mouse-ului
import math  # Pentru calcule matematice (distanta click)
import numpy as np # Pentru limitarea valorilor (prevenirea tremuratului)
import socket

# --- CONFIGURARE INITIALA ---
pyautogui.FAILSAFE = False  # Previne oprirea cursorului la margini

# Importam modulele necesare din MediaPipe (metoda stabila)
from mediapipe.python.solutions import hands as mp_maini
from mediapipe.python.solutions import drawing_utils as mp_desen

# Initializam detectorul IA
detector_mana = mp_maini.Hands(
    static_image_mode=False, 
    max_num_hands=1, 
    min_detection_confidence=0.7
)

# Deschidem camera web
camera_web = cv2.VideoCapture(0)

# Aflam rezolutia monitorului laptopului
latime_monitor, inaltime_monitor = pyautogui.size()

# Parametri pentru zona de control (Touchpad Virtual)
margine_zona = 100  # Pixeli de margine in fereastra camerei

print("Sistem Complet: Click Stanga (Mare+Aratator) | Click Dreapta (Mijlociu+Aratator)")

# --- BUCALA PRINCIPALA ---

IP_MATLAB = "127.0.0.1"
PORT_MATLAB = 5005
server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while camera_web.isOpened():
    # 1. Citim cadrul de la camera
    succes, imagine_cadru = camera_web.read()
    if not succes:
        break

    # 2. Oglindim imaginea si aflam dimensiunile ferestrei video
    imagine_cadru = cv2.flip(imagine_cadru, 1)
    inaltime_f, latime_f, _ = imagine_cadru.shape

    # 3. Desenam "Touchpad-ul Virtual" (dreptunghi albastru)
    cv2.rectangle(imagine_cadru, (margine_zona, margine_zona), 
                  (latime_f - margine_zona, inaltime_f - margine_zona), (255, 0, 0), 2)

    # 4. Conversie culori pentru IA
    imagine_rgb = cv2.cvtColor(imagine_cadru, cv2.COLOR_BGR2RGB)
    rezultate = detector_mana.process(imagine_rgb)

    # 5. Daca IA detecteaza mana
    if rezultate.multi_hand_landmarks:
        for repere in rezultate.multi_hand_landmarks:
            # Desenam scheletul mainii
            mp_desen.draw_landmarks(imagine_cadru, repere, mp_maini.HAND_CONNECTIONS)

            # Extragem varfurile degetelor necesare
            deget_mare = repere.landmark[4]
            deget_aratator = repere.landmark[8]
            deget_mijlociu = repere.landmark[12]

            # --- LOGICA DE MAPARE SI STABILIZARE ---
            x_cam = int(deget_aratator.x * latime_f)
            y_cam = int(deget_aratator.y * inaltime_f)

            # Limitarea coordonatelor in interiorul dreptunghiului
            x_limitat = np.clip(x_cam, margine_zona, latime_f - margine_zona)
            y_limitat = np.clip(y_cam, margine_zona, inaltime_f - margine_zona)

            # Mapare pe tot ecranul monitorului
            x_monitor = int((x_limitat - margine_zona) * latime_monitor / (latime_f - 2 * margine_zona))
            y_monitor = int((y_limitat - margine_zona) * inaltime_monitor / (inaltime_f - 2 * margine_zona))

            mesaj_matlab = f"{deget_aratator.x:.4f},{deget_aratator.y:.4f}"
            server_udp.sendto(mesaj_matlab.encode(), (IP_MATLAB, PORT_MATLAB))

            # --- MOD SCROLL SAU MOUSE ---
            # Daca degetul mijlociu este mult mai sus decat palma, activam scroll (verificam incheietura pentru referinta daca e nevoie, dar ramanem la logica simpla)
            # In acest cod, consideram scroll daca degetele sunt departate vertical
            if deget_mijlociu.y < deget_aratator.y - 0.1:
                cv2.putText(imagine_cadru, "MOD: SCROLL", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                if y_limitat < inaltime_f // 2:
                    pyautogui.scroll(40)
                else:
                    pyautogui.scroll(-40)
            else:
                cv2.putText(imagine_cadru, "MOD: MOUSE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                pyautogui.moveTo(x_monitor, y_monitor, _pause=False)

            # --- LOGICA DE CLICK ---
            
            # Distanta pentru CLICK STANGA (Deget Mare + Aratator)
            distanta_stanga = math.hypot(deget_aratator.x - deget_mare.x, deget_aratator.y - deget_mare.y)
            
            # Distanta pentru CLICK DREAPTA (Deget Aratator + Mijlociu)
            distanta_dreapta = math.hypot(deget_aratator.x - deget_mijlociu.x, deget_aratator.y - deget_mijlociu.y)

            # Executie Click Stanga
            if distanta_stanga < 0.05:
                pyautogui.click(button='left')
                cv2.circle(imagine_cadru, (x_cam, y_cam), 20, (0, 255, 255), cv2.FILLED)
                pyautogui.sleep(0.2)

            # Executie Click Dreapta
            elif distanta_dreapta < 0.04: # Prag putin mai mic pentru degete lipite
                pyautogui.click(button='right')
                cv2.circle(imagine_cadru, (x_cam, y_cam), 20, (0, 0, 255), cv2.FILLED) # Cerc rosu pentru dreapta
                pyautogui.sleep(0.3)

    # 6. Afisarea ferestrei
    cv2.imshow("Control Mouse Final - SCS", imagine_cadru)

    if cv2.waitKey(1) & 0xFF == 27:
        break

camera_web.release()
cv2.destroyAllWindows()