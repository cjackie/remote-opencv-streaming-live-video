import cv2
import numpy as np
import socket
import struct
from io import BytesIO
from datetime import datetime

# Capture frame
cap = cv2.VideoCapture(0)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('10.0.0.220', 8080))

print("connected")

send_delta = 1/30
last_sent = datetime.now()
while cap.isOpened():
    if (datetime.now() - last_sent).total_seconds() > send_delta:
        _, frame = cap.read()

        target_w = 400
        target_h = target_w // 16 * 10
        frame = cv2.resize(frame, (target_w, target_h))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        memfile = BytesIO()
        np.savez_compressed(memfile, frame=frame)
        memfile.seek(0)
        data = memfile.read()

        last_sent = datetime.now()
        # Send form byte array: frame size + frame content
        client_socket.sendall(struct.pack("L", len(data)) + data)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
