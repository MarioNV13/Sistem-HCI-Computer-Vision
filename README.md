#  Sistem HCI bazat pe Computer Vision și Telemetrie UDP

Acest proiect reprezintă o interfață om-calculator (##Human-Computer Interaction##) care permite controlul sistemului prin gesturi ale mâinii capturate în timp real. 
Utilizând Python (MediaPipe, OpenCV, etc.), sistemul recunoaște poziția reperelor (landmarks) de la nivelul mâinii pentru 
a simula funcții de mouse (click, scroll, mișcare).
Datele procesate (coordonate carteziene și ID-ul gestului) sunt transmise către un server extern sau către MATLAB prin protocolul UDP (Port 5005). 
Această conexiune permite monitorizarea performanței sistemului în timp real și analiza cinematică a mișcărilor în mediul MATLAB, 
oferind o bază solidă pentru optimizarea algoritmilor de recunoaștere.
