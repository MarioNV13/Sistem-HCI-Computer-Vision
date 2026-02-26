import cv2  # Biblioteca pentru captura și procesarea imaginilor video
import mediapipe as mp  # Motorul de Inteligență Artificială pentru detectarea mâinii
import pyautogui  # Biblioteca ce permite controlul mouse-ului din cod
import math  # Utilizată pentru calcule matematice (distanța dintre degete)

# --- CONFIGURARE INIȚIALĂ ---

# Dezactivăm protecția care blochează mouse-ul în colțurile ecranului
pyautogui.FAILSAFE = False 

# Importăm modulele necesare din MediaPipe (metoda stabilă)
from mediapipe.python.solutions import hands as mp_maini
from mediapipe.python.solutions import drawing_utils as mp_desen

# Inițializăm detectorul IA pentru o singură mână
detector_mana = mp_maini.Hands(
    static_image_mode=False, 
    max_num_hands=1, 
    min_detection_confidence=0.7, 
    min_tracking_confidence=0.5
)

# Deschidem camera web a laptopului
camera_web = cv2.VideoCapture(0)

# Aflăm rezoluția monitorului tău (ex: 1920x1080)
latime_monitor, inaltime_monitor = pyautogui.size()

# Variabile pentru "netezirea" mișcării (ca să nu tremure cursorul)
coordonata_veche_x, coordonata_veche_y = 0, 0
factor_netezire = 5 

print("Sistemul este activ! Mișcă degetul arătător și apropie-l de cel mare pentru CLICK.")

# --- BUCALA PRINCIPALĂ ---

while camera_web.isOpened():
    # 1. Citim cadrul de la camera web
    succes, imagine_cadru = camera_web.read()
    if not succes:
        break

    # 2. Oglindim imaginea pentru ca mișcările să fie naturale (stânga-dreapta)
    imagine_cadru = cv2.flip(imagine_cadru, 1)
    inaltime_cam, latime_cam, _ = imagine_cadru.shape

    # 3. Conversie culori: MediaPipe necesită formatul RGB
    imagine_rgb = cv2.cvtColor(imagine_cadru, cv2.COLOR_BGR2RGB)

    # 4. IA procesează imaginea și caută punctele mâinii
    rezultate = detector_mana.process(imagine_rgb)

    # 5. Dacă a fost detectată o mână
    if rezultate.multi_hand_landmarks:
        for repere_mana in rezultate.multi_hand_landmarks:
            # Desenăm punctele și conexiunile mâinii pe imagine
            mp_desen.draw_landmarks(imagine_cadru, repere_mana, mp_maini.HAND_CONNECTIONS)

            # Extragem coordonatele pentru degetul arătător (ID 8) și degetul mare (ID 4)
            varf_aratator = repere_mana.landmark[8]
            varf_deget_mare = repere_mana.landmark[4]

            # --- LOGICA DE MIȘCARE ---
            # Mapăm poziția degetului pe rezoluția monitorului
            tinta_x = int(varf_aratator.x * latime_monitor)
            tinta_y = int(varf_aratator.y * inaltime_monitor)

            # Aplicăm formula de netezire pentru un cursor stabil
            ecran_x = coordonata_veche_x + (tinta_x - coordonata_veche_x) / factor_netezire
            ecran_y = coordonata_veche_y + (tinta_y - coordonata_veche_y) / factor_netezire

            # Mișcăm efectiv mouse-ul la noile coordonate
            pyautogui.moveTo(ecran_x, ecran_y, _pause=False)
            
            # Actualizăm coordonatele vechi pentru cadrul următor
            coordonata_veche_x, coordonata_veche_y = ecran_x, ecran_y

            # --- LOGICA DE CLICK ---
            # Calculăm distanța matematică dintre vârful arătătorului și cel al degetului mare
            distanta_click = math.hypot(varf_aratator.x - varf_deget_mare.x, varf_aratator.y - varf_deget_mare.y)

            # Dacă distanța este sub pragul de 0.05 (degetele se ating), executăm click
            if distanta_click < 0.05:
                pyautogui.click()
                # Desenăm un cerc galben pe ecranul camerei ca feedback vizual pentru click
                cv2.circle(imagine_cadru, (int(varf_aratator.x * latime_cam), int(varf_aratator.y * inaltime_cam)), 20, (0, 255, 255), cv2.FILLED)
                # O mică pauză pentru a evita click-urile multiple accidentale
                pyautogui.sleep(0.1)

    # 6. Afișăm fereastra video de control
    cv2.imshow("Control Mouse prin Gesturi", imagine_cadru)

    # 7. Închidem programul la apăsarea tastei ESC (cod 27)
    if cv2.waitKey(1) & 0xFF == 27:
        break

# --- CURĂȚENIE FINALĂ ---
camera_web.release()  # Oprim accesul la cameră
cv2.destroyAllWindows()  # Închidem ferestrele video