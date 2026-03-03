#  HCI System based on Computer Vision and UDP Telemetry

This project features a Human-Computer Interaction (**Human-Computer Interaction**) interface that enables system control through real-time hand gesture recognition. Using Python (MediaPipe, OpenCV, etc.), the system tracks hand landmarks to simulate mouse functions such as clicking, scrolling, and cursor movement.

Processed data, including Cartesian coordinates and gesture IDs, is transmitted to an external server or MATLAB via the UDP protocol (Port 5005). This telemetric connection allows for real-time performance monitoring and kinematic motion analysis within the MATLAB environment, providing a solid foundation for optimizing recognition algorithms.

**IMPORTANT** - To view the English version of the code, please access the project files: **main_english.py**(mouse control) and **gesture_tracker.m**(MATLAB)




#  Sistem HCI bazat pe Computer Vision și Telemetrie UDP

Acest proiect reprezintă o interfață om-calculator (**Human-Computer Interaction**) care permite controlul sistemului prin gesturi ale mâinii capturate în timp real. 
Utilizând Python (MediaPipe, OpenCV, etc.), sistemul recunoaște poziția reperelor (landmarks) de la nivelul mâinii pentru 
a simula funcții de mouse (click, scroll, mișcare).
Datele procesate (coordonate carteziene și ID-ul gestului) sunt transmise către un server extern sau către MATLAB prin protocolul UDP (Port 5005). 
Această conexiune permite monitorizarea performanței sistemului în timp real și analiza cinematică a mișcărilor în mediul MATLAB, 
oferind o bază solidă pentru optimizarea algoritmilor de recunoaștere.
