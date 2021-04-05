import cv2
import numpy
import socket
import struct
import threading
from io import BytesIO
from datetime import datetime
from udp_packages import UdpPacketsHandler, UdpPacket

class Streamer(threading.Thread):
    MAX_UDP_PACKAGE_SIZE = 65535
    
    def __init__(self, hostname, port):
        threading.Thread.__init__(self)

        self.hostname = hostname
        self.port = port
        self.streaming = False
        self.jpeg = None
        self.face_cascade = cv2.CascadeClassifier(
                        'model/haarcascades/haarcascade_frontalface_default.xml')

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('Socket created')

        s.bind((self.hostname, self.port))
        print('Socket bind complete')

        udp_handler = UdpPacketsHandler()
        start_time = datetime.now()
        while True:
            data = s.recv(Streamer.MAX_UDP_PACKAGE_SIZE)
            if data == bytes("start", "ascii"):
                self.streaming = True
                continue
            elif data == bytes("end", "ascii"):
                self.streaming = False
                continue

            # Processes the package. If the package completes an image, data will not be None.
            image_data = udp_handler.process_packet(UdpPacket.decode(data))
            if image_data:
                # Successfully joins packages and gets an image
                print("Took %.3f (ms) for receiving the image %d KB with UDP." %
                      ((datetime.now() - start_time).total_seconds() * 1000, len(image_data) // 1024))
                
                start_time = datetime.now()              
                # Convert the byte array to a 'jpeg' format
                memfile = BytesIO()
                memfile.write(image_data)
                memfile.seek(0)
                image = numpy.load(memfile)["frame"]

                # Classfication
                faces = self.face_cascade.detectMultiScale(image, 1.3, 5)
                for (x, y, w, h) in faces:
                    image = cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)

                ret, jpeg = cv2.imencode('.jpg', image)
                self.jpeg = jpeg

                print("Took %.3f (ms) for processsing the image." % 
                    ((datetime.now() - start_time).total_seconds() * 1000))

                # Reset the time
                start_time = datetime.now()

        print('Exit thread.')

    def get_jpeg(self):
        return self.jpeg.tobytes()

streamer = Streamer('10.0.0.220', 8081)
streamer.start()
def get_streamer():
    return streamer
