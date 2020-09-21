import cv2
import os
import time
import queue
import pickle
from processing_faceId import processing_faceid
import threading
from amg88 import amg88
import RPi.GPIO as GPIO
from mlx90614 import MLX90614
from smbus2 import SMBus
import numpy


class camera(threading.Thread):
    '''
    Клас для получения данных с камеры RGB
    '''
    def __init__(self):
        super().__init__()
        self.cam = cv2.VideoCapture(0)
        self.frame = None

    def getFrame(self):
        return self.frame

    def run(self):
        while True:
            ret, img = self.cam.read()
            if ret:
                self.frame = img


pathProject = '/home/pi/project/termoBox/expiriments'
k = 1
path_cvm_model = os.path.join(pathProject, 'svm_model_{}.pk'.format(k))
path_knn_model = os.path.join(pathProject, 'knn_model_{}.pk'.format(k))

model_cvm = pickle.load(open(path_cvm_model, 'rb'))
model_knn = pickle.load(open(path_knn_model, 'rb'))

queue_recognition = queue.Queue()
processing_recognition = processing_faceid(queue_recognition, model_cvm, model_knn)

cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

font = cv2.FONT_HERSHEY_SIMPLEX

face_detector = cv2.CascadeClassifier('/home/pi/project/termoBox/app_thermometer/rc/haarcascade_frontalface_default.xml')
oldTime = time.time()
x = y = w = h = 0
time_clear = time.time()
time_clear_text = time.time()

teplovizor = amg88()
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pirometr = MLX90614(SMBus(1))

video = camera()
video.start()
text = ''
text_2 = ''
flag_show_temp = True

def processing(t_teplovizor):
    '''
    Считывает значения с пирометра и выдает ответ на экран
    :param t_teplovizor:
    :return: температуру пирометра и температуру тепловизора
    '''
    time_out = time.time()
    while time.time() - time_out <= 5:
        input_state = GPIO.input(18)
        if input_state == False:
            print('Button Pressed')
            tempPir = []
            for _ in range(3):
                tempPir.append(pirometr.get_object_1())
                time.sleep(0.2)
            return round(numpy.max(tempPir), 1), t_teplovizor
    return -1, t_teplovizor

def valid(tempPir, t_teplovizor):
    '''
    Решения о состоянии здоровья
    :param tempPir:
    :param t_teplovizor:
    :return: текст сообщения
    '''
    if t_teplovizor >= 37.2 or tempPir >= 37.2:
        if tempPir == -1:
            return 'See a doctor t1: {}'.format(t_teplovizor)
        else:
            return 'See a doctor t1: {} t2: '.format(t_teplovizor, tempPir)
    else:
        if tempPir == -1:
            return 'Things are good t1: {}'.format(t_teplovizor)
        else:
            return 'Things are good t1:{} t2:{}'.format(t_teplovizor, tempPir)


while True:
    # success, frame = video.read()
    # if not success is None:
    frame = video.getFrame()
    if not frame is None:
        #frame = cv2.resize(frame, (1080, 1920))
        #frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        frame = frame[:, 185:455]

        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(frame, text, (5, 100), font, 1, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, text_2, (5, 200), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

        if time.time() - oldTime > 0.3 and flag_show_temp:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:

                if w >= 150 and h >= 150:

                    cv2.putText(frame, "Raise your hand", (5, 200), font, 1, (0, 0, 255), 1, cv2.LINE_AA)
                    cv2.imshow("window", frame)

                    fase_RGB_200_200 = frame[y:y + w, x:x + h]

                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    text = 'Wait for recognition'

                    time_recognition = time.time()
                    dict_res = processing_recognition.predict_freme(fase_RGB_200_200)
                    print("time_recognition {}".format(time.time() - time_recognition))

                    if not dict_res is None:
                        print("dict_res", dict_res)

                        t_teplovizor = teplovizor.getMaxTemp()
                        text = "Hello"
                        tempPir, t_teplovizor = processing(t_teplovizor)
                        text_2 = valid(tempPir, t_teplovizor)

                        time_clear_text = time.time()
                        flag_show_temp = False

                    else:
                        print("dict_res_not", dict_res)

                        t_teplovizor = teplovizor.getMaxTemp()
                        text = "no recognition"

                        tempPir, t_teplovizor = processing(t_teplovizor)
                        text_2 = valid(tempPir, t_teplovizor)

                        time_clear_text = time.time()
                        flag_show_temp = False

                    print("time_recognition + pull {}".format(time.time() - time_recognition))

            oldTime = time.time()

        if time.time() - time_clear > 1:
            x = y = w = h = 0
            time_clear = time.time()

        if time.time() - time_clear_text > 4:
            text = ''
            text_2 = ''
            tempPir = t_teplovizor = -1
            flag_show_temp = True
            time_clear_text = time.time()


        cv2.imshow("window", frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        cv2.destroyAllWindows()
        break