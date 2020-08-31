from app_thermometer import app
import threading
import time
import cv2
import numpy
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
        return self.camera_IR.getFrame()  #208, 156

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


    def stop_devices(self):
        pass

    def crop(self, frame_RGB, IR_frame):
        '''
        Обрезает изображения по лицу человека todo Допилить обрезку
        :param frame_RGB:
        :return:
        '''

        faces = self.camera_RGB.getBbox()
        print(faces)
        if faces is None: return 0

        maxTemp = self.camera_IR.getMaxTemp(faces)
        print("*"*20)
        print(maxTemp)
        print("*" * 20)

        return 1


    def get_temp_web(self):

        tempPir = self.get_temp_pir()
        temp_IR = self.camera_IR.getTempCenterPoint()
        if temp_IR is None:
            temp_IR = 0

        if temp_IR is None:
            temp_IR = 0

        return round(temp_IR, 1), round(tempPir, 1)

    def run(self):
        print("Start processing threading")

        print('Режим ожидания', '')
        lcd_rus.pull_lcd_text(0, 'Режим ожидания')
        while self.status_run:


            i = 0
            count_measurements_ir = 0
            temp_people = []
            temp_people_pir = []

            flag = True
            while i <= 10 and self.camera_RGB.status_ir_camera:
                print('Идет измерения')
                if flag:
                    lcd_rus.pull_lcd_text(0, 'Идет измерения')
                    flag = False


                temp_IR = self.camera_RGB.temp
                if not temp_IR is None:
                    print("i={} temp_IR {}".format(i, temp_IR))
                    if temp_IR != -1:
                        t2 = round(temp_IR, 1)
                        temp_people.append(t2)

                        lcd_rus.pull_lcd_l(t2)
                        i += 1
                        time.sleep(1)

            if len(temp_people) != 0:

                print(numpy.max(temp_people), "-", "Поднесите руку")

                lcd_rus.pull_lcd_text(0, numpy.max(temp_people))
                time.sleep(0.2)
                # lcd_rus.pull_lcd_r('')
                time.sleep(0.2)
                lcd_rus.pull_lcd_text(1, "Поднесите руку")
                time.sleep(1)

                Flag = True
                oldTime = time.time()

                while count_measurements_ir <= 20:
                    #Считываем значения температур у пирометра

                    tempPir = self.get_temp_pir()
                    if not tempPir is None:
                        t1 = round(tempPir, 1)
                        print("t1=", t1)
                        lcd_rus.pull_lcd_r(t1)
                        temp_people_pir.append(t1)
                        count_measurements_ir +=1
                        time.sleep(0.4)


            if len(temp_people) != 0 and len(temp_people_pir) != 0:
                maxT_people = numpy.max(temp_people)
                maxT_pir = numpy.max(temp_people_pir)

                if maxT_people >= 37.9 or maxT_pir >= 37.9:
                    res = "Стой"
                else:
                    res = "Иди"

                print("Out LCD", maxT_people, maxT_pir, res)
                lcd_rus.pull_lcd_l(maxT_people)
                time.sleep(0.1)
                lcd_rus.pull_lcd_r(maxT_pir)
                time.sleep(0.1)
                lcd_rus.pull_lcd_text(1, res)
                lcd_rus.clear()
                time.sleep(5)

        print("Stop processing threading")
        self.stop_devices()