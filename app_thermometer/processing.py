import threading
import time
import cv2
from app_thermometer.moduls.lcd_i2c_rus import lcd_rus
from app_thermometer.moduls.measurements.mlx90614 import MLX90614
from app_thermometer.moduls.camera import VideoCamera
from app_thermometer.moduls.Seek_termal import Thermal
from time import sleep

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

        #tempPir = self.get_temp_pir()
        temp_IR = self.camera_IR.getTempCenterPoint()
        if temp_IR is None:
            temp_IR = 0


        return round(temp_IR, 1)



    def run(self):
        print("Start processing threading")

        print('Режим ожидания', '')
        lcd_rus.pull_lcd_text(1, 'Режим ожидания')

        prev_temp = self.get_temp_pir()
        is_begining = True
        i = 0
        while True:
            cur_temp = self.get_temp_pir()

            if cur_temp - prev_temp > 0.6 and cur_temp > 24.00:
                is_begining = False

                lcd_rus.pull_lcd_text(1, "Начинаю измерение")
                i = 0
                start_temp = prev_temp
                sleep(0.4)
                max_t = cur_temp
                cur_temp = self.get_temp_pir()
                while (abs(cur_temp - prev_temp) > 0.1):
                    sleep(0.4)
                    cur_temp = self.get_temp_pir()
                    prev_temp = cur_temp
                    max_t = max(cur_temp, max_t)
                if abs(cur_temp - start_temp) > 1:

                    if max_t <= 32.5:
                        max_t = max_t + 4.3 + abs(32.5 - max_t) / 1.23076923
                    else:
                        max_t = max_t + 4.3

                    if max_t >= 37.0:
                        lcd_rus.pull_lcd_r(round(max_t, 1))
                        lcd_rus.pull_lcd_text(1, "СТОП!")
                        time.sleep(7)
                    else:

                        lcd_rus.pull_lcd_r(round(max_t, 1))
                        lcd_rus.pull_lcd_text(1, "Проходи")
                        time.sleep(7)

                    sleep(1)
                    #lcd_rus.clear()
                    sleep(0.1)
                    lcd_rus.pull_lcd_l(round(max_t, 1))
                else:
                    # lcd_rus.clear()
                    sleep(0.1)
                    lcd_rus.pull_lcd_text(1, "Готов измерять")
            prev_temp = cur_temp
            sleep(0.2)
            i += 1
            if i == 5 and not is_begining:
                # lcd_rus.clear()
                lcd_rus.pull_lcd_text(1, "Готов измерять")

