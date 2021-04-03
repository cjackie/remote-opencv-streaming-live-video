import cv2
import numpy as np

# Capture frame
cap = cv2.VideoCapture(0)

windowNotSet = True
while cap.isOpened():
    ret, image = cap.read()
    if ret == 0:
        break

    [h, w] = image.shape[:2]
    image = cv2.flip(image, 1)

    face_cascade = cv2.CascadeClassifier(
        'model/haarcascades/haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        image = cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)

    if windowNotSet is True:
        cv2.namedWindow("tensorflow based (%d, %d)" %
                        (w, h), cv2.WINDOW_NORMAL)
        windowNotSet = False

    image = cv2.resize(image, (500, 300))
    cv2.imshow("tensorflow based", image)
    k = cv2.waitKey(1) & 0xff
    if k == ord('q') or k == 27:
        break

cap.release()
