import cv2  # Library for video processing
import mediapipe as mp  # AI engine for hand detection
import pyautogui  # Library for mouse control
import math  # For mathematical calculations (click distance)
import numpy as np # For value clamping (jitter prevention)
import socket

# --- INITIAL CONFIGURATION ---
pyautogui.FAILSAFE = False  # Prevents cursor from stopping at edges

# Import necessary modules from MediaPipe (stable method)
from mediapipe.python.solutions import hands as mp_hands
from mediapipe.python.solutions import drawing_utils as mp_draw

# Initialize the AI detector
hand_detector = mp_hands.Hands(
    static_image_mode=False, 
    max_num_hands=1, 
    min_detection_confidence=0.7
)

# Open the webcam
webcam = cv2.VideoCapture(0)

# Get the laptop monitor resolution
monitor_width, monitor_height = pyautogui.size()

# Parameters for the control area (Virtual Touchpad)
area_margin = 100  # Margin pixels in the camera window

print("Complete System: Left Click (Thumb+Index) | Right Click (Middle+Index)")

# --- MAIN LOOP ---

MATLAB_IP = "127.0.0.1"
MATLAB_PORT = 5005
udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while webcam.isOpened():
    # 1. Read frame from camera
    success, frame_image = webcam.read()
    if not success:
        break

    # 2. Mirror the image and get video window dimensions
    frame_image = cv2.flip(frame_image, 1)
    f_height, f_width, _ = frame_image.shape

    # 3. Draw the "Virtual Touchpad" (blue rectangle)
    cv2.rectangle(frame_image, (area_margin, area_margin), 
                  (f_width - area_margin, f_height - area_margin), (255, 0, 0), 2)

    # 4. Color conversion for AI
    rgb_image = cv2.cvtColor(frame_image, cv2.COLOR_BGR2RGB)
    results = hand_detector.process(rgb_image)

    # 5. If AI detects a hand
    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            # Draw the hand skeleton
            mp_draw.draw_landmarks(frame_image, landmarks, mp_hands.HAND_CONNECTIONS)

            # Extract necessary fingertips
            thumb = landmarks.landmark[4]
            index_finger = landmarks.landmark[8]
            middle_finger = landmarks.landmark[12]

            # --- MAPPING AND STABILIZATION LOGIC ---
            x_cam = int(index_finger.x * f_width)
            y_cam = int(index_finger.y * f_height)

            # Clamp coordinates inside the rectangle
            x_clamped = np.clip(x_cam, area_margin, f_width - area_margin)
            y_clamped = np.clip(y_cam, area_margin, f_height - area_margin)

            # Map to the full monitor screen
            x_monitor = int((x_clamped - area_margin) * monitor_width / (f_width - 2 * area_margin))
            y_monitor = int((y_clamped - area_margin) * monitor_height / (f_height - 2 * area_margin))

            matlab_message = f"{index_finger.x:.4f},{index_finger.y:.4f}"
            udp_server.sendto(matlab_message.encode(), (MATLAB_IP, MATLAB_PORT))

            # --- SCROLL OR MOUSE MODE ---
            # If the middle finger is significantly higher than the index, activate scroll
            if middle_finger.y < index_finger.y - 0.1:
                cv2.putText(frame_image, "MODE: SCROLL", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                if y_clamped < f_height // 2:
                    pyautogui.scroll(40)
                else:
                    pyautogui.scroll(-40)
            else:
                cv2.putText(frame_image, "MODE: MOUSE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                pyautogui.moveTo(x_monitor, y_monitor, _pause=False)

            # --- CLICK LOGIC ---
            
            # Distance for LEFT CLICK (Thumb + Index Finger)
            left_click_dist = math.hypot(index_finger.x - thumb.x, index_finger.y - thumb.y)
            
            # Distance for RIGHT CLICK (Index + Middle Finger)
            right_click_dist = math.hypot(index_finger.x - middle_finger.x, index_finger.y - middle_finger.y)

            # Execute Left Click
            if left_click_dist < 0.05:
                pyautogui.click(button='left')
                cv2.circle(frame_image, (x_cam, y_cam), 20, (0, 255, 255), cv2.FILLED)
                pyautogui.sleep(0.2)

            # Execute Right Click
            elif right_click_dist < 0.04: # Slightly smaller threshold for joined fingers
                pyautogui.click(button='right')
                cv2.circle(frame_image, (x_cam, y_cam), 20, (0, 0, 255), cv2.FILLED) # Red circle for right click
                pyautogui.sleep(0.3)

    # 6. Display the window
    cv2.imshow("Mouse Control Final - SCS", frame_image)

    if cv2.waitKey(1) & 0xFF == 27: # ESC key to exit
        break

webcam.release()
cv2.destroyAllWindows()