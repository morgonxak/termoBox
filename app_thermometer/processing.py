from app_thermometer import app
import threading
import time
import cv2
from app_thermometer.moduls.lcd_i2c_rus import lcd_rus
from app_thermometer.moduls.mlx90614 import MLX90614
from app_thermometer.moduls.camera import VideoCamera
from app_thermometer.moduls.Seek_termal import Thermal

class processing(threading.Thread):
    def __init__(self, lcd, termoPoint:MLX90614, camera_RGB:VideoCamera, camera_IR:Thermal, path_CascadeClassifier):
        super().__init__()
        self.status_run = True
        self.lcd = lcd
        self.termoPoint = termoPoint
        self.camera_RGB = camera_RGB
        self.camera_IR = camera_IR

        self.face_detector = cv2.CascadeClassifier(path_CascadeClassifier)

    def getFrame_IR(self):
        '''
        Получаем тепмо изображение
        :return:
        '''
        return self.camera_IR.getFrame()

    def getFrame_RGB(self):
        '''
        Получения изображения с RGB камеры
        :return:
        '''
        return self.camera_RGB.get_frame()

    def getCenterPoint_IR(self):
        return self.camera_IR.getTempCenterPoint()

    def get_temp_pir(self):
        if not self.termoPoint is None:
            return self.termoPoint.get_object_1()
        else:
            return None

    def pull_lcd(self, temp1, temp2, verdict=None):
        lcd_rus.pull_lcd(temp1, temp2, verdict)

    def stop_devices(self):
        pass

    def crop(self, frame_RGB):
        '''
        Обрезает изображения по лицу человека todo Допилить обрезку
        :param frame_RGB:
        :return:
        '''
        gray = cv2.cvtColor(frame_RGB, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame_RGB, (x, y), (x + w, y + h), (255, 0, 0), 2)

        frame_IR = self.getFrame_IR()


    def run(self):
        print("Start processing threading")
        while self.status_run:
            IR_frame = self.getFrame_IR()
            RGB_frame = self.getFrame_RGB()
            tempPir = self.get_temp_pir()
            temp_IR = self.camera_IR.getTempCenterPoint()

            print("getFrame_IR", type(IR_frame))
            print("camera_RGB", type(RGB_frame))
            print("get_termoPoint", type(tempPir), tempPir)
            print("get_temp_IR_centr", type(temp_IR), temp_IR)

            if not tempPir is None:
                t1 = round(tempPir, 1)
            else:
                t1 = 0

            if not temp_IR is None:
                t2 = round(temp_IR, 1)
            else:
                t2 = 0

            print("Out LCD", t1, t2)
            self.pull_lcd(t1, t2)

            time.sleep(0.5)

        print("Stop processing threading")
        self.stop_devices()