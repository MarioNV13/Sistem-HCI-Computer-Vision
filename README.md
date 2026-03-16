# 🖐️ Vision-Based HCI System with UDP Telemetry

> **A real-time Human-Computer Interaction interface that maps hand gestures to system commands using Computer Vision and streams data via UDP for kinematic analysis.**

## 🌟 Overview
This project demonstrates a multi-platform approach to gesture recognition. It uses **Python** for high-speed image processing and hand landmark detection, then streams coordinates to **MATLAB** via **UDP** for real-time trajectory plotting and performance monitoring.

## 🚀 Key Features
* **Real-time Hand Tracking:** Uses MediaPipe and OpenCV to detect 21 hand landmarks at 30+ FPS.
* **Virtual Input Simulation:** Implements Left/Right Click, Cursor Movement, and Scrolling using `pyautogui`.
* **UDP Telemetry:** Low-latency data transmission (Port 5005) between Python and MATLAB.
* **Live Visualization:** MATLAB script for real-time plotting of the finger's Cartesian path.

## 🛠️ Tech Stack
* **Python:** OpenCV, MediaPipe, NumPy, Socket.
* **MATLAB:** UDP Port communication, Animated Lines (Live Plotting).

## 📈 Project Evolution & Technical Challenges

### 🔍 Challenge 1: Environment Compatibility (MediaPipe vs. Python Versions)
One of the primary hurdles was configuring the **MediaPipe** library within the VS Code environment. I encountered significant compatibility issues where the library failed to initialize due to version mismatches between the global Python interpreter and the local virtual environment. 
* **Solution:** I performed extensive debugging of the environment variables and eventually transitioned to a specific Python 3.9 interpreter, ensuring all dependencies (OpenCV, Protobuf) were correctly mapped.

### ⚡ Challenge 2: Jittery Cursor Movement
Initially, the mouse cursor was highly unstable due to the raw sensitivity of hand landmark tracking.
* **Solution:** I implemented a **stabilization logic** using `numpy.clip` and coordinate clamping within a "Virtual Touchpad" zone. This filtered out minor hand tremors, resulting in a smooth, professional user experience.

### 🌐 Challenge 3: Cross-Platform Communication (UDP)
Synchronizing data between Python (Emitter) and MATLAB (Receiver) required precise timing to avoid packet loss.
* **Solution:** I developed a robust UDP telemetry protocol on Port 5005, optimizing the data string format for low-latency transmission.
