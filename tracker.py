import cv2
import mediapipe as mp

def run_tracker(data_queue, active_width):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    while cap.isOpened():
        success, img = cap.read()
        if not success:
            continue

        # Preparar imagen para PyGame (RGB y espejada)
        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        mapped_x = None
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Dibujar los landmarks sobre la imagen RGB
                mp_draw.draw_landmarks(img_rgb, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Mapear la coordenada X a la anchura de la zona de juego (60% de la pantalla)
                index_x_normalized = hand_landmarks.landmark[8].x
                mapped_x = int(index_x_normalized * active_width)
                break 

        if not data_queue.empty():
            try:
                data_queue.get_nowait()
            except:
                pass
        
        # Enviar el estado y la matriz RGB lista para renderizar
        data_queue.put((mapped_x, img_rgb))

    cap.release()