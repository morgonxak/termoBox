import cv2
import threading
import numpy
from app_thermometer.moduls.Seek_termal import Thermal
import time

class VideoCamera(threading.Thread):
    def __init__(self, path_CascadeClassifier, irCamera):
        super().__init__()
        self.path_CascadeClassifier = path_CascadeClassifier
        self.irCamera = irCamera
        self.status_run = True
        self.frame = None
        self.bbox = None
        self.status_ir_camera = False
        self.old_time_run_ir_camera = time.time()

        self.irCamera.initialize()
        self.irCamera.start()
        self.temp = -1

    def init(self):
        self.face_detector = cv2.CascadeClassifier(self.path_CascadeClassifier)
        self.video = cv2.VideoCapture(0)


    def __del__(self):
        self.video.release()

    def get_frame(self):
        return self.frame

    def getBbox(self):
        return self.bbox

    def runIrCamera(self):

        time.sleep(5)
        self.irCamera.status_get_frame = True
        time.sleep(1)


    def stopIrCamera(self):
        self.irCamera.status_get_frame = False

    def getFace(self):
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(gray, 1.3, 5)

        if len(faces) != 0:
            self.old_time_run_ir_camera = time.time()
            if not self.status_ir_camera:
                self.runIrCamera()
            self.status_ir_camera = True

        self.bbox = numpy.copy(faces)
        for (x, y, w, h) in faces:
            cv2.rectangle(self.frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            #if self.status_ir_camera:
                self.temp = self.irCamera.getMaxTemp(x, y, w, h)
                #print("temp=", self.temp)
            else:
                self.temp = -1


    def get_frame_web(self):
        '''
        Для отображения на страници
        :return:
        '''
        ret, jpeg = cv2.imencode('.jpg', self.frame)

        return jpeg.tobytes()

    def run(self):
        while self.status_run:
            success, frame = self.video.read()
            if not success is None:
                self.frame = numpy.copy(frame)
                self.getFace()

                if time.time() - self.old_time_run_ir_camera >= 40:
                    self.stopIrCamera()
                    self.status_ir_camera = False
