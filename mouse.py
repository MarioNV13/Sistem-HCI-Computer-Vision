import cv2  # Biblioteca pentru procesarea imaginilor de la cameră
import mediapipe as mp  # Biblioteca de IA pentru detectarea mâinii
import pyautogui  # Biblioteca pentru controlul mouse-ului

# --- CONFIGURARE INITIALA ---

# Dezactivăm funcția de siguranță (opțional) pentru a permite mouse-ului să ajungă în colțuri
pyautogui.FAILSAFE = False 

# Importăm modulele MediaPipe (metoda stabilă care a funcționat anterior)
from mediapipe.python.solutions import hands as mp_maini
from mediapipe.python.solutions import drawing_utils as mp_desen

# Inițializăm detectorul IA pentru o singură mână
detector_mana = mp_maini.Hands(
    static_image_mode=False, 
    max_num_hands=1, 
    min_detection_confidence=0.7, 
    min_tracking_confidence=0.5
)

# Deschidem camera video (0 este camera principală)
camera_web = cv2.VideoCapture(0)

# Aflăm dimensiunile monitorului tău (ex: 1920x1080)
latime_monitor, inaltime_monitor = pyautogui.size()

print("Sistemul de control a pornit! Mișcă degetul arătător pentru a controla cursorul.")

# --- BUCALA PRINCIPALĂ ---

while camera_web.isOpened():
    # 1. Citim cadrul curent de la cameră
    succes, imagine_cadru = camera_web.read()
    if not succes:
        break

    # 2. Oglindim imaginea pentru ca direcția stânga-dreapta să fie corectă
    imagine_cadru = cv2.flip(imagine_cadru, 1)

    # 3. Conversie culoare: OpenCV oferă BGR, MediaPipe are nevoie de RGB
    imagine_rgb = cv2.cvtColor(imagine_cadru, cv2.COLOR_BGR2RGB)

    # 4. Trimitem imaginea la IA pentru a procesa reperele mâinii
    rezultate = detector_mana.process(imagine_rgb)

    # 5. Dacă IA a detectat mâna în imagine
    if rezultate.multi_hand_landmarks:
        for repere_mana in rezultate.multi_hand_landmarks:
            # Desenăm scheletul mâinii pe fereastra video
            mp_desen.draw_landmarks(imagine_cadru, repere_mana, mp_maini.HAND_CONNECTIONS)

            # Identificăm vârful degetului arătător (Landmark ID 8)
            deget_aratator = repere_mana.landmark[8]

            # TRANSFORMĂM COORDONATELE (0.0 - 1.0) ÎN PIXELI PE MONITOR
            # Înmulțim poziția relativă a degetului cu rezoluția ecranului
            pozitie_mouse_x = int(deget_aratator.x * latime_monitor)
            pozitie_mouse_y = int(deget_aratator.y * inaltime_monitor)

            # COMANDĂM MIȘCAREA MOUSE-ULUI
            # Folosim _pause=False pentru ca mișcarea să fie cât mai fluidă
            pyautogui.moveTo(pozitie_mouse_x, pozitie_mouse_y, _pause=False)

    # 6. Afișăm imaginea video pentru control vizual
    cv2.imshow("Control Mouse cu Gesturi", imagine_cadru)

    # 7. Închidem programul dacă se apasă tasta ESC (cod 27)
    if cv2.waitKey(1) & 0xFF == 27:
        print("Program închis de utilizator.")
        break

# --- ELIBERARE RESURSE ---
camera_web.release()  # Eliberăm camera video
cv2.destroyAllWindows()  # Închidem ferestrele programului