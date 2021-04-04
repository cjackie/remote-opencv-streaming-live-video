import cv2
import numpy
import socket
import struct
import threading
from io import BytesIO
from datetime import datetime


class Streamer(threading.Thread):

    def __init__(self, hostname, port):
        threading.Thread.__init__(self)

        self.hostname = hostname
        self.port = port
        self.running = False
        self.streaming = False
        self.jpeg = None
        self.face_cascade = cv2.CascadeClassifier(
                        'model/haarcascades/haarcascade_frontalface_default.xml')

    def run(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket created')

        s.bind((self.hostname, self.port))
        print('Socket bind complete')

        payload_size = struct.calcsize("L")

        s.listen(10)
        print('Socket now listening')

        self.running = True

        while self.running:

            print('Start listening for connections...')

            conn, addr = s.accept()
            print("New connection accepted.")

            while True:

                data = conn.recv(payload_size)

                if data:
                    # Read frame size
                    msg_size = struct.unpack("L", data)[0]

                    # Read the payload (the actual frame)
                    start_time = datetime.now()                    
                    data = b''
                    while len(data) < msg_size:
                        missing_data = conn.recv(msg_size - len(data))
                        if missing_data:
                            data += missing_data
                        else:
                            # Connection interrupted
                            self.streaming = False
                            break
                    print("Took %.3f (ms) for receiving the image %d KB." % 
                        ((datetime.now() - start_time).total_seconds() * 1000, len(data) // 1024))

                    # Skip building frame since streaming ended
                    if self.jpeg is not None and not self.streaming:
                        continue

                    start_time = datetime.now()              
                    # Convert the byte array to a 'jpeg' format
                    memfile = BytesIO()
                    memfile.write(data)
                    memfile.seek(0)
                    image = numpy.load(memfile)["frame"]

                    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(image, 1.3, 5)
                    for (x, y, w, h) in faces:
                        image = cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)

                    ret, jpeg = cv2.imencode('.jpg', image)
                    self.jpeg = jpeg

                    print("Took %.3f (ms) for processsing the image." % 
                        ((datetime.now() - start_time).total_seconds() * 1000))

                    self.streaming = True
                else:
                    conn.close()
                    print('Closing connection...')
                    self.running = False
                    self.streaming = False
                    self.jpeg = None
                    break

        print('Exit thread.')

    def stop(self):
        self.running = False

    def get_jpeg(self):
        return self.jpeg.tobytes()
