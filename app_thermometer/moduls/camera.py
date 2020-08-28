import cv2
import threading
import numpy
from app_thermometer.moduls.Seek_termal import Thermal

class VideoCamera(threading.Thread):
    def __init__(self, path_CascadeClassifier):
        super().__init__()
        self.path_CascadeClassifier = path_CascadeClassifier
        self.status_run = True
        self.frame = None

    def init(self):
        self.face_detector = cv2.CascadeClassifier(self.path_CascadeClassifier)
        self.video = cv2.VideoCapture(0)


    def __del__(self):
        self.video.release()

    def get_frame(self):
        return self.frame


    def get_frame_web(self):
        '''
        Для отображения на страници
        :return:
        '''
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(self.frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        ret, jpeg = cv2.imencode('.jpg', self.frame)

        return jpeg.tobytes()

    def run(self):
        while self.status_run:
            success, frame = self.video.read()
            if not success is None:
                self.frame = numpy.copy(frame)
