import cv2
import threading
import numpy
import time

class VideoCamera(threading.Thread):
    def __init__(self, path_CascadeClassifier):

        super().__init__()
        self.path_CascadeClassifier = path_CascadeClassifier
        self.status_run = True
        self.frame = None
        self.bbox = None
        self.face_detector = cv2.CascadeClassifier(self.path_CascadeClassifier)
        self.video = cv2.VideoCapture(0)

    def generator_frame(self):
        while self.status_run:
            yield self.get_frame(), []

    def __del__(self):
        self.video.release()

    def get_frame(self):
        '''
        отдает изображения с камеры
        :return:
        '''
        return self.frame

    def getBbox(self):
        return self.bbox


    def getFace(self):
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(self.frame, (x, y), (x + w, y + h), (255, 0, 0), 2)


    def run(self):
        self.oldTime = time.time()

        while self.status_run:
            success, frame = self.video.read()
            if not success is None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.frame = numpy.copy(frame)
                self.getFace()


