import cv2
import mediapipe as mp
import numpy as np
import os

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)

ruta_modelos = r'C:\Users\Lightning\Documents\Proyecto_Python\CSV_Abecedario'

# Cargar modelos de letras
def cargar_modelos():
    modelos = {}
    for archivo in os.listdir(ruta_modelos):
        if archivo.endswith(".csv"):
            letra = archivo.split('_')[0]  
            ruta_archivo = os.path.join(ruta_modelos, archivo)
            modelos[letra] = np.loadtxt(ruta_archivo, delimiter=',', usecols=range(1, 64))  
    return modelos

modelos = cargar_modelos()


def reconocer_letra(landmarks, modelos, umbral=0.275):
    letra_reconocida, distancia_minima = None, float('inf')
    
    for letra, modelo in modelos.items():
        distancia = np.min(np.linalg.norm(modelo - landmarks, axis=1))
        if distancia < distancia_minima:
            distancia_minima, letra_reconocida = distancia, letra

    return letra_reconocida if distancia_minima < umbral else None

# Variables de letra

palabra = ""  
letra_detectada = None  # Letra reconocida en tiempo real

# Captura en tiempo real
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    letra_detectada = None  

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]).flatten()
            letra_detectada = reconocer_letra(landmarks, modelos)

    # Mostrar palabra
    cv2.putText(frame, f'Palabra: {palabra}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f'Letra detectada: {letra_detectada or ""}', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    key = cv2.waitKey(1) & 0xFF

    # Si presiona espacio, agrega la letra detectada
    if key == ord(' ') and letra_detectada:
        palabra += letra_detectada  # Agregar la letra a la palabra

    # Salir con ESC
    if key == 27:
        break

    # Mostrar el video
    cv2.imshow("Hand Tracking", frame)
    
# Liberar Recursos
cap.release()
cv2.destroyAllWindows()
