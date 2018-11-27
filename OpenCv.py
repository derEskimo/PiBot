import cv2
import numpy as np

vc = cv2.VideoCapture(0)

face_cascade = cv2.CascadeClassifier('OpenCV/data/haarcascades/haarcascade_frontalface_default.xml')

def gen():
    """Video streaming generator function."""
    while True:
        retval, frame = vc.read()

        if retval:
            #image_processing(frame)
            frame = cv2.imencode('.jpg', frame)[1].tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def image_processing(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #Facerecognition
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    #Show distance and speed


    return img