import cv2  # Biblioteca pentru procesare video
import mediapipe as mp  # Motorul de IA pentru detectarea mainii
import pyautogui  # Biblioteca pentru controlul mouse-ului
import math  # Pentru calcule matematice (distanta click)

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

# Aflam rezolutia monitorului
latime_monitor, inaltime_monitor = pyautogui.size()

# Parametri pentru zona de control (Touchpad Virtual)
margine_zona = 100  # Pixeli de margine in fereastra camerei

print("Sistem Complet! Foloseste zona albastra ca pe un Touchpad.")

# --- BUCALA PRINCIPALA ---

while camera_web.isOpened():
    # 1. Citim cadrul de la camera
    succes, imagine_cadru = camera_web.read()
    if not succes:
        break

    # 2. Oglindim imaginea si aflam dimensiunile ferestrei
    imagine_cadru = cv2.flip(imagine_cadru, 1)
    inaltime_f, latime_f, _ = imagine_cadru.shape

    # 3. Desenam "Touchpad-ul Virtual" (un dreptunghi albastru)
    # Acest dreptunghi ajuta utilizatorul sa stie unde sa miste mana
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

            # Extragem varfurile degetelor: Mare (4), Aratator (8), Mijlociu (12)
            deget_mare = repere.landmark[4]
            deget_aratator = repere.landmark[8]
            deget_mijlociu = repere.landmark[12]

            # --- LOGICA DE MAPARE (Touchpad -> Monitor) ---
            # Transformam coordonatele degetului in pixeli in interiorul ferestrei camerei
            x_cam = int(deget_aratator.x * latime_f)
            y_cam = int(deget_aratator.y * inaltime_f)

            # Mapam doar zona din interiorul dreptunghiului albastru pe tot monitorul
            # Aceasta metoda ofera o precizie mult mai mare
            x_monitor = int((x_cam - margine_zona) * latime_monitor / (latime_f - 2 * margine_zona))
            y_monitor = int((y_cam - margine_zona) * inaltime_monitor / (inaltime_f - 2 * margine_zona))

            # --- VERIFICARE MOD: SCROLL sau MOUSE ---
            # Daca degetul mijlociu este ridicat (y mai mic decat la aratator) -> SCROLL
            if deget_mijlociu.y < deget_aratator.y:
                cv2.putText(imagine_cadru, "MOD: SCROLL", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                # Daca mana e in jumatatea de sus a zonei, scroll up, altfel scroll down
                if y_cam < inaltime_f // 2:
                    pyautogui.scroll(30)
                else:
                    pyautogui.scroll(-30)
            else:
                # Mod miscare cursor
                cv2.putText(imagine_cadru, "MOD: MOUSE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                pyautogui.moveTo(x_monitor, y_monitor, _pause=False)

            # --- LOGICA DE CLICK ---
            # Distanta intre degetul mare si cel aratator
            distanta_click = math.hypot(deget_aratator.x - deget_mare.x, deget_aratator.y - deget_mare.y)
            if distanta_click < 0.05:
                pyautogui.click()
                cv2.circle(imagine_cadru, (x_cam, y_cam), 20, (0, 255, 255), cv2.FILLED)
                pyautogui.sleep(0.2) # Previne click-ul dublu accidental

    # 6. Afisarea ferestrei finale
    cv2.imshow("Interfata Control Gesturi SCS", imagine_cadru)

    # Iesire la tasta ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Inchidere resurse
camera_web.release()
cv2.destroyAllWindows()