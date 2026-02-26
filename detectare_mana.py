import cv2  # Biblioteca pentru controlul camerei video
import mediapipe as mp  # Biblioteca de Inteligență Artificială pentru gesturi
import time # Utilizată pentru a oferi camerei timp să pornească

# --- CONFIGURARE IA ---

# Accesăm modulele MediaPipe (Ignoră dacă VS Code le subliniază cu roșu)
# type: ignore (această linie spune editorului să nu mai afișeze erori false)
mp_maini = mp.solutions.hands 
mp_desen = mp.solutions.drawing_utils 

# Inițializăm detectorul pentru o singură mână
# min_detection_confidence=0.7 înseamnă că IA trebuie să fie 70% sigură că vede o mână
detector_mana = mp_maini.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# Deschidem camera web (0 este de obicei camera integrată a laptopului)
camera_web = cv2.VideoCapture(0)

# Verificăm dacă sistemul poate accesa camera
if not camera_web.isOpened():
    print("EROARE: Camera nu poate fi pornită. Verifică permisiunile Windows!")
    exit()

print("Sistemul pornește... Caută fereastra video pe ecran!")
time.sleep(1) # Pauză scurtă pentru inițializarea senzorului camerei

# --- BUCALA PRINCIPALĂ ---

while camera_web.isOpened():
    # 1. Citim imaginea curentă de la cameră
    succes, imagine_cadru = camera_web.read()
    if not succes:
        break

    # 2. Oglindim imaginea pentru ca mișcările să fie intuitive (stânga-dreapta)
    imagine_cadru = cv2.flip(imagine_cadru, 1)

    # 3. MediaPipe lucrează cu culori RGB, dar camera oferă formatul BGR
    imagine_rgb = cv2.cvtColor(imagine_cadru, cv2.COLOR_BGR2RGB)

    # 4. Procesăm imaginea cu IA pentru a găsi punctele mâinii
    rezultate = detector_mana.process(imagine_rgb)

    # 5. Dacă IA a detectat o mână în cadru
    if rezultate.multi_hand_landmarks:
        for repere_mana in rezultate.multi_hand_landmarks:
            # Desenăm scheletul mâinii (punctele și liniile verzi)
            mp_desen.draw_landmarks(imagine_cadru, repere_mana, mp_maini.HAND_CONNECTIONS)

            # Aflăm dimensiunile ferestrei video (lățime și înălțime în pixeli)
            inaltime_f, latime_f, _ = imagine_cadru.shape

            # Identificăm degetul arătător (punctul numărul 8 în MediaPipe)
            deget_aratator = repere_mana.landmark[8]

            # Transformăm coordonatele din procente (0-1) în pixeli reali pe ecran
            pozitie_x = int(deget_aratator.x * latime_f)
            pozitie_y = int(deget_aratator.y * inaltime_f)

            # Desenăm un cerc roz mare pe vârful degetului pentru confirmare
            cv2.circle(imagine_cadru, (pozitie_x, pozitie_y), 15, (255, 0, 255), cv2.FILLED)

    # 6. Afișăm imaginea rezultată într-o fereastră nouă
    cv2.imshow("PROIECT GESTURI - PASUL 1", imagine_cadru)

    # 7. Programul se oprește dacă apeși tasta ESC (codul 27)
    if cv2.waitKey(1) & 0xFF == 27:
        print("Program închis manual.")
        break

# --- ELIBERARE RESURSE ---
camera_web.release() # Închidem camera
cv2.destroyAllWindows() # Închidem ferestrele video