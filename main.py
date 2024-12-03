import socket
import cv2
import mediapipe as mp
from PIL import Image

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '0.0.0.0'
port = 12345
server_socket.bind((host, port))
server_socket.listen(5)
print(f"Server listening on {host}:{port}...")

client_socket, client_address = server_socket.accept()
print(f"Connection established with {client_address}")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)

file_sent = False

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    finger_count = 0
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            if hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].y:
                finger_count += 1
            if hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y:
                finger_count += 1
            if hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y:
                finger_count += 1
            if hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].y:
                finger_count += 1
            if hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].y:
                finger_count += 1

        if finger_count == 0 and not file_sent:
            print("Detected zero fingers. Opening and sending file '4a.jpg'...")

            file_path = "4a.jpg"
            try:
                img = Image.open(file_path)
                img.show()
                print(f"Previewing file: {file_path}")
            except FileNotFoundError:
                print(f"File '{file_path}' not found.")

            try:
                with open(file_path, "rb") as f:
                    while chunk := f.read(1024):
                        client_socket.send(chunk)
                client_socket.send(b"EOF")
                print(f"File '{file_path}' sent successfully.")
                file_sent = True
            except FileNotFoundError:
                print(f"File '{file_path}' not found.")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
client_socket.close()
server_socket.close()
