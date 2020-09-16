import cv2
import threading
import numpy
import time
import os

class VideoCamera(threading.Thread):
    def __init__(self, path_CascadeClassifier, irCamera, termo):
        super().__init__()
        self.path_CascadeClassifier = path_CascadeClassifier
        self.irCamera = irCamera
        self.status_run = True
        self.frame = None
        self.bbox = None
        self.status_ir_camera = False
        self.old_time_run_ir_camera = time.time()
        self.termo = termo

        # self.irCamera.initialize()
        # self.irCamera.start()
        self.temp = -1
        self.tempC_WEB = None
        self.imageRGB_web = None
        self.slagFace = False
        self.text_lcd = ''
        self.tempPir = None
        self.tima_pir = time.time()

        self.slagFace =False
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

    def get_temp(self):
        T_text_path = r'/home/pi/ProjectMain/tMAXT.txt'
        T_image_path = r'/home/pi/ProjectMain/Thermal_image.png'
        count = 0
        temp, T_img = None, None
        while count <= 3:
            temp = -100
            try:
                if os.path.exists(T_image_path):
                    if os.path.exists(T_text_path):
                        f = open(T_text_path, 'r')
                        temp = float(f.read())
                        f.close()

                        if temp != -100:
                            if temp <= 32.5:
                                temp = temp + 4.3 + abs(32.5 - temp) / 1.23076923
                            else:
                                temp = temp + 4.3
                            print("на тепловизоре макс.: {}".format(temp))
                        else:
                            continue

                        T_img = cv2.imread(T_image_path, cv2.IMREAD_GRAYSCALE)
                        T_img = cv2.rotate(T_img, cv2.ROTATE_90_CLOCKWISE)  # rotateImage(Tt_img, 270)
                        T_img = T_img.astype(numpy.uint8)
                        T_img = cv2.cvtColor(T_img, cv2.COLOR_GRAY2RGB)
                        T_img = cv2.applyColorMap(T_img, cv2.COLORMAP_JET)


                        return temp, T_img

                else:
                    count += 1
                    continue
            except BaseException as e:
                count += 1
                continue

    def stopIrCamera(self):
        self.irCamera.status_get_frame = False

    def get_temp_pir(self):
        return self.termo.get_object_1()

    def Temperature_measurements(self):

        prev_temp = self.get_temp_pir()
        i = 0
        is_begining = True

        cur_temp = self.get_temp_pir()
        while True:
            cur_temp = self.get_temp_pir()
            if cur_temp - prev_temp > 0.6 and cur_temp > 24.00:
                is_begining = False
                lcd_rus.clear()
                time.sleep(0.1)
                lcd_rus.pull_lcd_text(1, "Начинаю измерение")
                self.text_lcd = "Начинаю измерение"
                i = 0
                start_temp = prev_temp
                time.sleep(0.4)
                max_t = cur_temp
                cur_temp = self.get_temp_pir()
                while (abs(cur_temp - prev_temp) > 0.1):
                    time.sleep(0.4)
                    cur_temp = self.get_temp_pir()
                    prev_temp = cur_temp
                    max_t = max(cur_temp, max_t)
                if abs(cur_temp - start_temp) > 1:
                    exact_t = max_t
                    if max_t <= 32.5:
                        max_t = max_t + 4.3 + abs(32.5 - max_t) / 1.23076923
                    else:
                        max_t = max_t + 4.3

                    if max_t >= 37.0:
                        pass
                        # text_with_warning("СТОП!", "  " + f"темпер.: {max_t:.1f}" + "\x99C")
                        lcd_rus.pull_lcd_r(round(max_t, 1))
                        lcd_rus.pull_lcd_text(1, "СТОП!")
                        self.text_lcd = 'СТОП!'
                        return round(max_t, 1)
                    else:
                        pass
                        # text_with_signal("Ваша температура", "  " + f"{max_t:.1f}" + "\x99C")
                        lcd_rus.pull_lcd_r(round(max_t, 1))
                        round(max_t, 1)

                    # time.sleep(1)
                    # lcd_rus.clear()
                    # # sleep(0.1)
                    # # lcd_rus.pull_lcd_l(round(max_t, 1))
                else:
                    lcd_rus.clear()
                    time.sleep(0.1)
                    lcd_rus.pull_lcd_text(1, "Готов измерять")
                    self.text_lcd = "Готов измерять"
            prev_temp = cur_temp
            time.sleep(0.2)
            i += 1
            if i == 5 and not is_begining:
                lcd_rus.clear()
                lcd_rus.pull_lcd_text(1, "Готов измерять")
                self.text_lcd = "Готов измерять"

    def getFace(self):
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(gray, 1.3, 5)
        flag = True
        lcd_rus.pull_lcd_l('')

        for (x, y, w, h) in faces:
            cv2.rectangle(self.frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            self.oldTime = time.time()
            self.timeUpdate_temp = time.time()

            if flag:
                if self.text_lcd != "Найдено лицо" :
                    #lcd_rus.pull_lcd_text(1, "Найдено лицо")
                    self.text_lcd = "Найдено лицо"
                temp, T_img = self.get_temp()

                self.tempC_WEB = temp
                self.imageRGB_web = T_img

                lcd_rus.pull_lcd_l(round(temp, 1))
                time.sleep(0.2)
                self.slagFace = True
                flag = False
                #Пирометр


    def get_frame_web(self):
        '''
        Для отображения на страници
        :return:
        '''
        ret, jpeg = cv2.imencode('.jpg', self.frame)
        return jpeg.tobytes()

    def get_IR_web(self):
        if not self.imageRGB_web is None:
            ret, jpeg = cv2.imencode('.jpg', self.imageRGB_web)
            return jpeg.tobytes()
        return None

    def get_temp_web(self):

        mode = self.slagFace
        if mode:
            t1 = round(self.tempC_WEB, 1)

            t2 = round(self.termo.get_object_1(), 1)

            return round(t1, 1), round(t2, 1), mode
        else:
            return 0, 0, 0


    def run(self):
        self.oldTime = time.time()
        lcd_rus.pull_lcd_text(1, "Готов измерять")
        while self.status_run:
            success, frame = self.video.read()
            if not success is None:
                self.frame = numpy.copy(frame)
                self.getFace()

            if self.slagFace:
                if time.time() - self.oldTime > 5:
                    self.slagFace = False
                    # lcd_rus.clear()
                    # time.sleep(0.1)
                    # lcd_rus.pull_lcd_text(1, "Готов измерять")
                    # self.text_lcd = "Готов измерять"



