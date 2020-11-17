import cv2
import os
import time
import pickle
from app_thermometer.moduls.processing_faceId import processing_faceid
import threading
from app_thermometer.moduls.amg88 import amg88
import RPi.GPIO as GPIO
from app_thermometer.moduls.mlx90614 import MLX90614
from smbus2 import SMBus
import numpy
from app_thermometer.moduls.dataBase import BD


tip_bd = 1
# dict_connect_settings = os.path.join('.','rc','database')
# dict_connect_settings =     pathDataBase = os.path.join('.','rc','database').
dict_connect_settings = './rc/database.bd'

# path_haarcascade = '/home/pi/project/termoBox/app_thermometer/rc/haarcascade_frontalface_default.xml'
# pathProject = '/home/pi/project/termoBox/expiriments'
path_haarcascade = os.path.abspath(
    os.path.join(os.getcwd(), './app_thermometer/rc/haarcascade_frontalface_default.xml'))
pathProject = os.path.abspath(os.path.join(os.getcwd(), './rc'))

face_detector = cv2.CascadeClassifier(path_haarcascade)


processing_recognition = processing_faceid(pathProject)
##########################

dataBase = BD(dict_connect_settings)

########################################
# Buzer
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
pinBuzer = 25
GPIO.setup(pinBuzer, GPIO.OUT)
#######################
p = GPIO.PWM(pinBuzer, 1000)  # channel=12 frequency=50Hz


def on_buzer(mode):
    '''
    РАбота с пещалкой
    :param mode: True - ПРоходит  False - НЕ пройдет

    :return:
    '''
    global p
    print("mode {}".format(mode))
    if mode:
        p.start(0)
        p.ChangeDutyCycle(50)
        time.sleep(0.3)
        p.ChangeDutyCycle(0)
    else:
        for _ in range(2):
            p.ChangeDutyCycle(50)
            time.sleep(1)
            p.ChangeDutyCycle(0)
            time.sleep(0.5)


##################################

import cv2
from multiprocessing import Process, Queue
import numpy
import logging  ## лог


class x_y_w_h_object(object):
    def __init__(self):
        self.x = self.y = self.w = self.h = 0

    def set_(self, x=0, y=0, w=0, h=0):
        self.x, self.y, self.w, self.h = x, y, w, h

    def set_(self, x=(0, 0, 0, 0)):
        self.x, self.y, self.w, self.h = x

    def if_(self, min_=None):
        temp = (self.x + self.y + self.w + self.h != 0)

        if not min_ is None:
            temp = temp and (min_ <= self.w or min_ <= self.h)
        return temp

    def get_(self):
        return self.x, self.y, self.w, self.h

    '''   
    def get_gran(self):
        with self as im:
            return y:y + w, x:x + h        
    '''


class frame_Thread(threading.Thread):  # работа с камерой

    def __init__(self, If_Test_Foto=False):
        '''
        If_Test_Foto: вывод на экран фото(True) или вывод на экран видео с камеры(False)
        '''
        super().__init__()
        
        # установки
        self.If_Test_Foto = If_Test_Foto
        self.if_active = False  # активация pin_Thread
        # self.daemon = True  # для отключения потока при остановке программы

        self.ROTATE_CLOCKWISE = cv2.ROTATE_90_CLOCKWISE

        self.time = 0.3  # шаг повторения по времени
        self.out_in = False  # для чтения с потока
        self.cap = None  # переменная для подключения к камере
        self.image = None
        if not self.If_Test_Foto:
            self.cap = cv2.VideoCapture(0)  # подключение к камере
        else:
            self.image = cv2.imread(os.path.abspath("./Test.jpg"))

        self.frame = None  # переменная под фрейм с камеры
        self.ret = False  # фрейм прочитан корректно?
        if 0 == self.frame_image():  # получение кодра или фото
            self.height, self.width = 0, 0  # размер кадра
            self.height, self.width = self.height_width_size()  # размер кадра
            self.min_w_h = self.min_w_h_size()  # размер минимальных границ для выделения
        else:
            print("frame_Thread.frame_image return -1")
            logging.error("frame_Thread.frame_image return -1")
            raise Exception("frame_Thread.frame_image return -1")

        del self.frame
        self.frame = None  # переменная под фрейм с камеры
        self.return_Id_to_face = Queue()  # очередь для снятия инфы с потока

        self.frame_delay_time = 0  # время задержки на пропажу выделения

        self.id_hread = None  # для потока
        # self.if_null_hread = False #  (можно ли обнулить именно id_hread )
        self.x_y_w_h = x_y_w_h_object()
        self.x_y_w_h_temp = x_y_w_h_object()
        self.frame_delay_if = True  # задержано ли выделение
        # self.frame_time_out = 5# время задержки на пропажу выделения
        self.fase_RGB_200_200 = None  # под скрин лица

        self.time_temp1 = 0
        self.frame_delay = 0  # задержка на пропажу выделения

        self.flag_id_on = False  # найден ли id
        self.id_person = None  # переменная под персонал

        # для вывода
        self.frame_out = None  # кадр
        self.x_y_w_h_out = x_y_w_h_object()  # положение лица
        self.frame_delay_if_out = True  # отсутствие задержки
        self.id_person_out = None  # id_person
        self.fase_RGB_200_200_out = None  # лицо

        # обнуление
        self.zeroing()  # обнуление переменных

    def ___in_out___(self):

        self.out_in = False 
        #self.frame_out.delete()
        #self.fase_RGB_200_200_out.delete()
        #self.frame_out= None 
        #self.frame_out = numpy.copy(self.frame) # кадр self.frame.copy()
        if not(self.frame_out == self.frame).all():
            self.frame_out = (self.frame) if not self.frame is None else self.frame_out # кадр
            self.x_y_w_h_out.set_(self.x_y_w_h.get_())#положение лица
            self.frame_delay_if_out = self.frame_delay_if #наличие задержки 
            self.id_person_out = self.id_person # id_person
            
            #self.fase_RGB_200_200_out = None
            #self.fase_RGB_200_200_out = numpy.copy(self.fase_RGB_200_200) # лицо self.fase_RGB_200_200.copy()
            self.fase_RGB_200_200_out = (self.frame) if not self.fase_RGB_200_200 is None else self.fase_RGB_200_200_out  # лицо
        
    def next_(self):
        self.out_in = True

    def out(self):
        # while self.out_in: None #???????????????
        #print("!!! {}".format( type(self.frame))).copy().copy()
        return self.frame_out if not self.frame_out is None else None, self.x_y_w_h_out, self.frame_delay_if_out, self.id_person_out, self.fase_RGB_200_200_out if not self.fase_RGB_200_200_out is None else None  ##.get_()

    def Stop_(self):
        '''
        остановка цикла потока
        '''
        self.if_active = False

    def run(self):
        print("Активация потока frame_Thread")
        self.if_active = True
        while self.if_active:
            self.if_on = True
            t = 0
            if time.time() - t >= self.time:
                t = time.time()
                time_ = t - self.time_temp1  # time.time()
                self.frame_image()  # или скрин или фото
                self.x_y_w_h_temp.set_(self.faces_x_y())

                if self.x_y_w_h_temp.if_(self.min_w_h):
                    self.x_y_w_h.set_(self.x_y_w_h_temp.get_())
                    self.frame_delay = t
                    self.frame_delay_if = True
                    # self.frame_delay_time = self.frame_time_out-time_
                # elif (0 <= (t - self.frame_delay) <= self.frame_delay_time ):
                else:
                    self.frame_delay_if = False
                # else:
                #    self.x_y_w_h.set_(self.x_y_w_h_temp.get_())
                #    self.frame_delay_if = True
                #    #self.time_temp1 = time.time() #XXXXXXXXXXXXXXXX убрать при использовании  zeroing()

                #print(t - self.frame_delay)
                #print(self.frame_delay_time)
                #print(self.x_y_w_h.get_())
                if self.x_y_w_h.if_(self.min_w_h): # and not self.if_null_hread:
                    x , y , w, h = self.x_y_w_h.get_() 
                    #cv2.rectangle(self.frame, (x, y), (x + w, y + h), (255, 0, 0), 2)#вывод квадр
                    #print("self.hread()1 {}".format( self.id_person))
                    self.hread()
                    #print("self.hread()2 {}".format( self.id_person))
                #self.frame = self.frame_orientation(self.frame)
                if self.out_in: 
                    self.out_in = False       
                    self.___in_out___()
        self.hread(True)
        if not self.If_Test_Foto:
            self.cap.release()
        self.if_on = False

    def hread(self, if_zeroing=False):
        def clearQueue():  # обнуление очереди
            try:
                while True:
                    self.return_Id_to_face.get_nowait()
            except:  # Queue.Empty
                pass


        if not if_zeroing:   
            #if not(self.id_person is None or self.id_person == -1)
            if self.id_hread is None :# and self.id_person is None:# не существует ли процесс 
                if self.frame_delay_if and not self.frame is None:

                    x , y , w, h = self.x_y_w_h.get_() 
                    self.fase_RGB_200_200 = numpy.copy((self.frame)[y:y + w, x:x + h]) #self.numpy_copy() #numpy.copy((self.frame)[y:y + w, x:x + h]) 
                    #self.fase_RGB_200_200 = (self.frame[y:y + w, x:x + h]).copy() #self.numpy_copy() #numpy.copy((self.frame)[y:y + w, x:x + h]) 
                    clearQueue() # обнуление очереди
                    #self.id_hread = Process(target=self.Id_to_face, args=(self.fase_RGB_200_200,self.return_Id_to_face))#, daemon=True
                    self.id_hread = Process(target=self.Id_to_face)#, daemon=True
                    self.id_hread.start()#запуск потока по поиску в бд  
            elif not self.id_hread is None : # существует ли процесс 
                if not self.id_hread.is_alive(): # завершён ли процесс        

                    try:
                        id_person_temp = self.return_Id_to_face.get()  # вытаскиваем ID
                    except:
                        logging.info("except: return_Id_to_face.get() {}".format(time.time()))
                        id_person_temp = -1
                    try:
                        self.id_hread.terminate()
                    except:
                        logging.info("except: frame_Thread.hread.terminate {}".format(time.time()))
                    if self.id_person == -1: self.id_person = None
                    if self.id_person is None: self.id_person = id_person_temp
                    if self.id_person is None or self.id_person == -1:  # если нет id, то попытка ещё раз его получить с нового фрейма
                        try:
                            self.id_hread.close()
                        except:
                            logging.info("except: iframe_Thread.id_hread.close {}".format(time.time()))
                            print("Error frame_Thread.id_hread.close()")
                    self.id_hread = None
        else:
            if not self.id_hread is None:  # сущ ли процесс
                if self.id_hread.is_alive():
                    self.id_hread.terminate()
                if not self.id_hread.is_alive():
                    try:
                        self.id_hread.close()
                    except:
                        logging.info("except: iframe_Thread.id_hread.close {}".format(time.time()))
                        print("Error iframe_Thread.id_hread.close())")
                    self.id_hread = None

        
    def zeroing(self):# обнуление переменных

        self.x_y_w_h_temp.set_() # обнулять для сброса задержки экрана
        
        self.return_Id_to_face.put(-1) # для сняия с потока инф(чтоб без матов(часть костыля #1))
        self.time_temp1 = time.time() #начало сканирования 
        self.frame_delay = 0 # задержка на пропажу выделения
        self.x_y_w_h.set_() # зануляем #self.x = self.y = self.w = self.h = 0
        #self.frame = None #переменная под фрейм с камеры
        
        self.flag_id_on = False # найден ли id
        self.id_person = None # переменная под персонал
        self.frame_delay_if = True # задержано ли выделение  
        
        
        self.fase_RGB_200_200 = None # под скрин лица
            
        #self.frame_out = self.frame
        #self.x_y_w_h_out.set_() #положение лица
        #self.frame_delay_if_out = True #отсутствие задержки 
        #self.id_person_out = None # id_person    

        #self.fase_RGB_200_200_out = None  # под скрин лица
        self.hread(True)

    def frame_orientation(self, frame=None):  # ориентация кадра или фото
        if_ = frame is None
        if if_:
            frame = self.frame

        height, width = self.height_width_size(True, frame)
        if height < width:
            frame = cv2.rotate(frame, self.ROTATE_CLOCKWISE)
            if not if_:
                print("frame_orientation cv2.flip x")
                frame = cv2.flip(frame, 0)  # ореентация камеры переворот вокруг оси x
        return frame

    def frame_image(self):  # получение кадра или фото
        if not self.frame is None:  # если переменная под фрейм не пуста
            del self.frame  # удаляем её
            self.frame = None
        if not self.If_Test_Foto:
            self.ret, self.frame = self.cap.read()
            if not self.frame is None:
                self.frame = cv2.flip(self.frame, 1)  # ореентация камеры переворот вокруг оси y

                self.frame = self.frame_orientation()
                # frame = frame = [:, 185:455]
            else:
                logging.error("except: frame_Thread.frame_image/ frame is None")
                return -1
        else:
            self.frame = numpy.copy(self.image)
        return 0

    def faces_x_y(self):  # ф-я для поиска границ
        x = y = w = h = 0
        x1 = y1 = w1 = h1 = 0
        if not self.frame is None:
            gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)
            for (x1, y1, w1, h1) in faces:
                x, y, w, h = x1, y1, w1, h1
                break

        return x, y, w, h

    def height_width_size(self, if_=False, frame=None):  # размер кадра
        # height, width = 626, 537 #зармеры кадра
        if frame is None:
            frame = self.frame
        if if_:
            height = 0
            width = 0
        else:
            height = self.height
            width = self.width
        if not frame is None:
            if height + width == 0:
                height = numpy.size(frame, 0)
                width = numpy.size(frame, 1)

        return height, width

    def min_w_h_size(self):  # размер минимальных границ для выделения
        temp = 0
        if self.height + self.width != 0:
            d = 3  # КОЭФФИЦИЕНТ НА МИНИМАЛЬНУЮ ДЛИНУ РАСПОЗНАНИЯ
            temp = round(numpy.max([self.height / d, self.width / d]), 0)

        return temp

    def Id_to_face(self, if_test_wimdovs=False):  # поиск по фото
        self.id_person = -1
        # print(self.qqq)
        if not if_test_wimdovs:
            self.id_person = processing_recognition.predict_freme(self.fase_RGB_200_200)
        # if return_Id_to_face.get() == -1 :
        self.return_Id_to_face.put(self.id_person)


class pin_object(object):  # работа с gbyfvb
    def __init__(self, Name: str, pin: int, if_test_in_wind=False):
        self.text = Name  # название
        self.pin = pin  # пин
        self.ct = False  # состояние
        self.if_ = False  # режим "всегда вкл"
        self.mig = False  # мигание
        self.time = 0.0  # время активности

        self.if_test_in_wind = if_test_in_wind  #

        GPIO.setup(pin, GPIO.OUT)
        self.on()

    def on(self, on=None):
        '''
        ф-я  регистрации цвета
        Name : название цвета
        pin: номер пина
        '''
        '''
        def ____on_on____(self, if_test_in_wind:bool, pin:int, on:bool = False):
            if if_test_in_wind: 
                print("{} {} {}".format(pin , "GPIO.HIGH" if on else "GPIO.LOW" ,on))# текст действия
                #if on :
                #    print("{} GPIO.LOW {}".format(self.pin_[n_pin] ,on))
                #else:
                #    print("{} GPIO.HIGH {}".format(self.pin_[n_pin] ,on))
            else:
                #GPIO.output(self.pin_[n_pin] , GPIO_) # действие
                GPIO.output(pin , GPIO.HIGH if on else GPIO.LOW) # действие LOW HIGH
        '''
        if self.ct != on or on is None:  # проверка на разное состояние (имеющееся и требуемое)
            if on is None: on = False
            if self.if_test_in_wind:
                print("{} {} {}".format(self.pin, "GPIO.HIGH" if on else "GPIO.LOW", on))  # текст действия
            else:
                GPIO.output(self.pin, GPIO.HIGH if on else GPIO.LOW)  # действие LOW HIGH
            self.ct = on  # сохранение состаяния

    def pin_sost(self):
        '''
        проверка (долговременного) состояния пина по номеру
        n_pin: номер цвета для работы
        возвращает: логическое или меж: есть ли горением всегда и есть ли временем горения
        '''
        return self.if_ or self.time != 0.0

    def pin_on_time(self, tim):
        '''
        ф-я изменяет (временное) состояния пина под номером n_pin, на время tim
        n_pin: номер цвета для работы
        tim: ко-во времени на свечение пина
        '''

        if self.time == 0.0:
            self.if_ = False  # отключение состояния "всегда включен"
            self.time = time.time() + tim  # указание времени отключения

    def pin_on_off(self, on: bool):
        '''
        ф-я изменяет ("всегда включен") состояния пина под номером n_pin, на время on
        n_pin: номер цвета для работы
        on: действие вкл(True)/выкл(False)
        '''
        self.time = 0.0  # уберает время отключения
        self.if_ = on  # изменяет состояния "всегда включен"


class pin_Thread(threading.Thread):  # работа со пином
    def __init__(self, if_test_in_wind=False):
        '''
        if_test_in_wind: вывод на экран(True) или действие(False)
        '''
        super().__init__()
        # установки
        self.if_test_in_wind = if_test_in_wind  # вывод на экран(True) или действие(False)
        self.if_active = False  # активация pin_Thread
        # self.daemon = True  # для отключения потока при остановке программы

        self.time = 0.3  # шаг повторения по времени
        self.mig = 0.5  # задержка мигания
        self.mig_kol_vo = 1  # кол-во миганий

        GPIO.setmode(GPIO.BCM)  # для работы с GPIO

        # переменные для работы
        self.pin_text = []  # название
        self.pin_ = []  # пин

        # self.pin_add("red",23)
        # self.pin_add("green",24)
        self.pin_add_all()  # регистрирование пинов

    def pin_add_all(self):
        '''
        ф-я стандартной регистрации списка
        '''
        self.pin_add("red", 17)
        self.pin_add("blue", 22)
        self.pin_add("green", 27)
        
        
        self.pin_add("door", 25)

    def pin_add(self, Name: str, pin: int):
        '''
        ф-я  регистрации цвета
        Name : название цвета
        pin: номер пина
        '''
        self.pin_text.append(Name)
        self.pin_.append(pin_object(Name, pin, self.if_test_in_wind))

    def pin_namber(self, pin_pin=None):
        '''
        возвращает: номер пина или по пину или по названию (всё нормально)///иначе: -1 - ошибка с типом/ -2 - ошибка в вызове
        '''
        try:
            if isinstance(pin_pin, str):
                return self.pin_text.index(pin_pin)
            elif isinstance(pin_pin, pin_object):
                return self.pin_.index(pin_pin)
            elif isinstance(pin_pin, int):
                # цикл на поиск пина в pin_object
                # el
                if 0 <= pin_pin < len(self.pin_):
                    return pin_pin
                else:
                    return -1
            else:
                print("pin_namber tip error")

                raise Exception("pin_Thread.pin_namber tip error")
                return -1
        except:
            print("pin_namber except")
            raise Exception("pin_Thread.pin_namber except")
            return -2

    """
    def _pin_(self, pin, on = False):
        '''    
        ф-я выключение пина
        pin: цвет для работы
        on: действие вкл(True)/выкл(False)
        '''
        n_pin = self.pin_namber(pin)
        if n_pin < 0: 
            print("pin_ namber error")  
            return -1
        self.pin_[n_pin].on(on)
        return 0
    """

    def pin_on_time(self, pin, time):
        '''
        ф-я изменяет (временное) состояния пина под номером n_pin, на время tim
        n_pin: номер цвета для работы
        tim: ко-во времени на свечение пина
        '''
        n_pin = self.pin_namber(pin)
        if n_pin < 0:
            print("pin_ namber error")
            return -1
        self.pin_[n_pin].pin_on_time(time)

    def pin_on_off(self, pin, on: bool):
        '''
        ф-я изменяет ("всегда включен") состояния пина под номером n_pin, на время on
        n_pin: номер цвета для работы
        on: действие вкл(True)/выкл(False)
        '''
        n_pin = self.pin_namber(pin)
        if n_pin < 0:
            print("pin_ namber error")
            return -1
        self.pin_[n_pin].pin_on_off(on)

    def pin_mig(self, pin, on: bool = False):
        '''
        ф-я изменяет состояния мигания пина под номером n_pin, остальные пины - отключаются
        pin: цвет для работы
        on: действие вкл(True)/выкл(False)
        '''
        n_pin = self.pin_namber(pin)
        if n_pin < 0:
            print("pin_ namber error")
            return -1
        if self.pin_[n_pin].mig != on:  # проверка на разное состояние (имеющееся и требуемое)
            for i, val in enumerate(self.pin_):  # проходка по всем доступным пинам
                val.mig = on if n_pin == i else False

    def pin_all_one(self, pin, on: bool = False):
        '''
        ф-я изменяет состояния пина под номером n_pin, остальные пины - отключаются
        n_pin: номер цвета для работы
        on: действие вкл(True)/выкл(False)
        '''
        n_pin = self.pin_namber(pin)
        if n_pin < 0:
            print("pin_ namber error")
            return -1
        for i, val in enumerate(self.pin_):
            val.pin_on_off(on if n_pin == i else False)
            val.on(on if n_pin == i else False)

    def pin_all(self, on: bool = False):  # вкл/выкл питание
        '''
        ф-я изменяет состояние всех пинов
        on: действие вкл(True)/выкл(False)
        '''
        for i, val in enumerate(self.pin_):
            val.on(on)
            val.pin_on_off(on)

    def pin_off(self):  # выкл питание
        '''
        ф-я изменяет состояние всех пинов
        on: действие вкл(True)/выкл(False)
        '''
        for i, val in enumerate(self.pin_):
            val.on()

    def Stop_(self):
        '''
        остановка цикла потока
        '''
        self.if_active = False

    def run(self):
        print("Активация потока pin_Thread ")
        t_if = 0
        t = time.time()
        self.if_active = True
        # print("1")
        while self.if_active:
            # print("qqq")
            self.if_on = True
            # if True:
            if time.time() - t_if >= self.time:
                t_if = time.time()
                for i, val in enumerate(self.pin_):

                    time_ = val.time - time.time()
                    if time_ > 0 or val.if_:  # если состояния "всегда включен" или состояния "время" , то вкл пин
                        # print("1 1")
                        val.on(True)
                    elif time_ <= 0 and val.time != 0.0:  # если состояния "время" и оно кончилось, то отключение состояния "время" и  то выкл пин
                        # print("1 2")
                        val.pin_on_off(False)
                        val.on(False)
                    elif val.mig:  # если состояния "мигание"
                        # print("1 3")
                        """
                        print(val.text)
                        print(val.pin)
                        print(val.ct)
                        print(val.if_)
                        print(val.mig)
                        print(val.time)
                        """
                        for number in range(2 * self.mig_kol_vo):  # колво мигов * (вкл+выкл)
                            for number in range(0, 1):  # проходим 2 состояния (вкл, выкл)
                                # print(number == 0)
                                val.on(number == 0)  #
                                t = time.time()
                                while time.time() - t < self.mig:  # self.mig - задержка мигания //1
                                    None
                        val.mig = False
                    else:  # иначе отключение
                        # print("1 4")
                        val.on(False)
        self.pin_off()
        self.if_on = False


class teplo_Thread(threading.Thread):  # работа с температурами

    def __init__(self, dataBase:BD):
        super().__init__()
        # настройка
        self.dataBase = dataBase
        self.daemon = True # для отключения потока при остановке программы
        GPIO.setmode(GPIO.BCM) # для работы с GPIO
        GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP) # подключение дачика растояния
        self.teplovizor = amg88() # подключение верхнего тепловизора 
        self.pirometr = MLX90614(SMBus(1)) # подключение нижнего тепловизора
        #границы допустимого
        self.___min___ = 0.0 #20
        self.___max___ = 39.2
        #\/попытки обработки 
        
         
        self.out_last_tepl = 33.2
        self.out_last_pir = 33.2
        #с кофициэнтами 
        self.threshold_pir_cof = 0
        self.threshold_teplovizor_cof = 0
        #по  прогнозам 1х  10 в бд
        self.if_bd_10 = False
        
        
        #/\попытки обработки 

        # управление
        self.time = 0.3  # шаг повторения по времени
        self.if_active = False  # активация считывания с тепловизора
        self.if_ran = False  # состояние Thread
        # данные
        self.temp_tepl_arr = None
        self.temp_tepl_Raw = 0  # рабочая переменая для teplovizor
        self.t_teplovizor = 0  # рабочая переменая для перещитаного teplovizor
        self.tempPir = 0  # рабочая переменая для pirometr
        self.inputPir = 1  # рабочая переменая наличия руки (дачик растояния) /0 - есть рука / 1 - нет руки
        # темповые данные
        self.next_temp_tepl_Raw = 0 # темповая  переменая для teplovizor ()
        self.next_t_teplovizor = 0 # темповая переменая для перещитаного teplovizor
        self.next_tempPir = 0 # темповая переменая для pirometr
        self.next_inputPir = 1 # темповая переменая наличия руки (дачик растояния)
        self.next_tepl_arr = None

        #ok
        self.ok_temp_tepl_Raw = 0 # темповая  переменая для teplovizor ()
        self.ok_t_teplovizor = 0 # темповая переменая для перещитаного teplovizor
        self.ok_tempPir = 0 # темповая переменая для pirometr
        self.ok_inputPir = 1 # темповая переменая наличия руки (дачик растояния)        
        
    def ___teplo___(self): 
        '''
        получает и возвращает данные с модумей
        '''
        temp_tepl_Raw = temp_tepl = tempPir = 0

        inputPir = 1 
        try:
            temp_tepl_Raw, temp_tepl = self.teplovizor.getMaxTemp()
        except:  # Queue.Empty
            print("error: teplo_Thread.___teplo___ (tepl)")
            pass
        try:
            inputPir = 0 #GinputPir = GPIO.input(18) # ОТКЛЮЧЁН ДАЧИК РАСТОЯНИЯ!!!!!
            tempPir = round(self.pirometr.get_object_1(), 1)
            # if GPIO.input(18) == False:#у нас есть отжатая кнопа?
            #    tempPir = round(self.pirometr.get_object_1(),1)
        except:  # Queue.Empty
            print("error: teplo_Thread.___teplo___ (Pir)")
            pass
        # print("temp_tepl {} tempPir {} temp_tepl_Raw {}".format(temp_tepl, tempPir, temp_tepl_Raw))
        return temp_tepl_Raw, temp_tepl, tempPir, inputPir

    def teplo_teplo(self):
        '''
        сохраняет данные с модумей
        '''
        self.next_temp_tepl_Raw, self.next_t_teplovizor, self.next_tempPir, self.next_inputPir = self.___teplo___()
        self.next_tepl_arr = self.teplovizor.getreturnMaxrix() 

    def next_(self,out_last_tepl = 33.2, out_last_pir = 33.2):
        '''
        переводит темповые переменные в рабочие
        '''

        self.temp_tepl_Raw, self.t_teplovizor, self.tempPir, self.inputPir = self.if_ok(self.next_temp_tepl_Raw, self.next_t_teplovizor, self.next_tempPir, self.next_inputPir) 
        #self.temp_tepl_Raw, self.t_teplovizor, self.tempPir, self.inputPir = self.next_temp_tepl_Raw, self.next_t_teplovizor, self.next_tempPir, self.next_inputPir 
        if not self.temp_tepl_arr is None:
            del self.temp_tepl_arr
        self.temp_tepl_arr = None

        try:
            self.temp_tepl_arr = numpy.copy(self.next_tepl_arr)
        except:
            print("Error teplo_Thread.next_ getMaxrix")
            self.temp_tepl_arr = numpy.array([self.temp_tepl_Raw, self.temp_tepl_Raw])

        #self.temp_tepl_arr = numpy.copy(self.next_tepl_arr) #self.teplovizor.getreturnMaxrix() #numpy.array([self.temp_tepl_Raw,self.temp_tepl_Raw])    
        data_time, self.threshold_pir_cof, self.threshold_teplovizor_cof = self.dataBase.get_calibration_threshold()
        '''
        self.out_last_tepl = out_last_tepl
        self.out_last_pir = out_last_pir
        '''
        # бд 10 первых
        self.if_bd_10, out_last_tepl, out_last_pir = dataBase.get_agv_10_calibration_threshold() 
        if self.if_bd_10:
            print("Калибровочные данные:", out_last_tepl, out_last_pir)                                                                                
            self.out_last_tepl, self.out_last_pir = out_last_tepl, out_last_pir
        

    def teplo(self):
        '''
        возвращает рабочие переменные
        '''
        return self.temp_tepl_Raw, self.t_teplovizor, self.tempPir, self.inputPir

        
    def zeroing(self):    
        #ok
        self.ok_temp_tepl_Raw = 0 # темповая  переменая для teplovizor ()
        self.ok_t_teplovizor = 0 # темповая переменая для перещитаного teplovizor
        self.ok_tempPir = 0 # темповая переменая для pirometr
        self.ok_inputPir = 1 # темповая переменая наличия руки (дачик растояния)  /0 - есть рука / 1 - нет руки
       

    def ___valid_None___(self, temp_tepl_Raw, tempPir):
        '''
        если данные пустые, то берёт данные из рабочих
        '''
        if tempPir is None: tempPir = self.tempPir
        if temp_tepl_Raw is None: temp_tepl_Raw = self.temp_tepl_Raw
        return temp_tepl_Raw, tempPir

    def valid_min(self, temp_tepl_Raw=None, tempPir=None):
        '''
        ищем рабочие минимальные данные
        '''
        temp_tepl_Raw, tempPir = self.___valid_None___(temp_tepl_Raw, tempPir)

        if temp_tepl_Raw == 0 or tempPir == 0:
            return 0
        tepl = temp_tepl_Raw
        if self.inputPir == 0:
            tepl = round(numpy.min([tepl, tempPir]), 1)
        return tepl

    def valid_max(self, temp_tepl_Raw=None, tempPir=None):
        '''
        ищем рабочие максимальные данные
        '''
        temp_tepl_Raw, tempPir = self.___valid_None___(temp_tepl_Raw, tempPir)

        if temp_tepl_Raw == 0 or tempPir == 0:
            return 0
        tepl = temp_tepl_Raw

        if self.inputPir == 0:
            tepl= round(numpy.max([tepl, tempPir]), 1)
        return tepl

    def if_valid_min(self, temp_tepl_Raw=None, tempPir=None):
        '''
        вохвращает: входят ли рабочие минимальные данные в границы допустимого
        '''
        """
        tepl = self.valid_min(temp_tepl_Raw, tempPir)

        if self.___min___ <= tepl <= self.___max___:
            return True
        else:
            return False
        """
        temp_tepl_Raw, tempPir = self.___valid_None___(temp_tepl_Raw, tempPir)

        Raw = abs(temp_tepl_Raw - self.out_last_tepl) 
        Pir = abs(tempPir - self.out_last_pir) 
        #Raw = temp_tepl_Raw - self.out_last_tepl 
        #Pir = tempPir - self.out_last_pir 
        
        #коффиц
        """
        #print(Raw,Pir)
        #print(self.threshold_teplovizor_cof,self.threshold_pir_cof)
        #print(Raw - self.threshold_teplovizor_cof,Pir - self.threshold_pir_cof)
        #print("_____________")
        
        if_ = 3 <= abs (Raw - self.threshold_teplovizor_cof) and 3 <= abs (Pir - self.threshold_pir_cof)
        #print("if_valid_min {}".format(if_))
        return if_
        """
        # бд 10 первых
        threshold_teplovizor_cof = 6 #-3 #нижние коффиц расхождения
        threshold_pir_cof = 10 #-2 # нижние коффиц расхождения
        if not self.if_bd_10: 
            return True
        else:
            if_ = threshold_teplovizor_cof <= (Raw) and threshold_pir_cof <=(Pir)
            """
            print("temp_tepl_Raw {}   tempPir {}".format(temp_tepl_Raw, tempPir))
            print("out_last_tepl {}   out_last_pir {}".format(self.out_last_tepl, self.out_last_pir))
            print("Raw {}   threshold_pir_cof {}".format(Raw, Pir))
            print("if_valid_min {}".format(if_))
            print("________________")
            """
            return if_
        
        
    def if_valid_max(self, temp_tepl_Raw=None, tempPir=None):
        '''
        вохвращает: входят ли рабочие максимальные данные в границы допустимого
        '''
        """
        tepl = self.valid_max(temp_tepl_Raw, tempPir)
        if self.___min___ <= tepl <= self.___max___:
            return True
        else:
            return False
        """
        temp_tepl_Raw, tempPir = self.___valid_None___(temp_tepl_Raw, tempPir)
        Raw = abs(temp_tepl_Raw - self.out_last_tepl) 
        Pir = abs(tempPir - self.out_last_pir) 
        #Raw = temp_tepl_Raw - self.out_last_tepl 
        #Pir = tempPir - self.out_last_pir 
        #коффиц
        """
        print("Temperaturs Tepl:{} / Pir:{}".format(self.temp_tepl_Raw,self.tempPir))
        print("the temperature of the environment Tepl:{} / Pir:{}".format(self.out_last_tepl,self.out_last_pir))
        print("Coefficient Temperatur Tepl:{} / Pir:{}".format(Raw,Pir))
        print("Coefficient BD Tepl:{} / Pir:{}".format(self.threshold_teplovizor_cof,self.threshold_pir_cof))
        #print(Raw - self.threshold_teplovizor_cof,Pir - self.threshold_pir_cof) 
        print("_____________") 
        if_ = abs (Raw - self.threshold_teplovizor_cof) <= 6 and abs (Pir - self.threshold_pir_cof) <= 6
        #print("if_valid_max {}".format(if_))
        return if_ 
        """
        # бд 10 первых
        threshold_teplovizor_cof = 10 #3 #верхние коффиц расхождения
        threshold_pir_cof = 10 #2 # верхние коффиц расхождения
        
        if not self.if_bd_10: 
            print("Калибровка", temp_tepl_Raw, tempPir)                                                     
            return True
        else:
            if_ = (Raw)<= threshold_teplovizor_cof and (Pir)<=threshold_pir_cof
            print("Результат:", temp_tepl_Raw, tempPir, if_)                                                         
            """
            print("temp_tepl_Raw {}   tempPir {}".format(temp_tepl_Raw, tempPir))
            print("out_last_tepl {}   out_last_pir {}".format(self.out_last_tepl, self.out_last_pir))
            print("Raw {}   threshold_pir_cof {}".format(Raw, Pir))
            print("if_valid_max {}".format(if_))
            print("________________")
            """
            return if_
        
        
        
        
    def if_valid(self, temp_tepl_Raw=None, tempPir=None):
        '''
        вохвращает: входят ли рабочие данные в границы допустимого
        '''

        
        #print( self.if_valid_max(tempPir, temp_tepl_Raw)  )
        #print( self.if_valid_min(tempPir, temp_tepl_Raw)  )
        #print(self.if_valid_max(tempPir, temp_tepl_Raw) and self.if_valid_min(tempPir, temp_tepl_Raw) )
        
        #if_ = self.if_valid_max(temp_tepl_Raw, tempPir ) and self.if_valid_min(temp_tepl_Raw, tempPir ) 
        if_ = self.if_valid_max(temp_tepl_Raw, tempPir ) and True#self.if_valid_min(temp_tepl_Raw, tempPir ) 
        # !?!?!?!? ЧТО ЭТО!???
        #print("if_valid {}".format(if_))
        return if_

    def if_ok(self, temp_tepl_Raw,  t_teplovizor, tempPir , inputPir ): 
        '''
        self.ok_temp_tepl_Raw = 0 # темповая  переменая для teplovizor ()
        self.ok_t_teplovizor = 0 # темповая переменая для перещитаного teplovizor
        self.ok_tempPir = 0 # темповая переменая для pirometr
        self.ok_inputPir = 1 # темповая переменая наличия руки (дачик растояния) /0 - есть рука / 1 - нет руки
        '''
        
        #if self.if_valid():
        #self.ok_temp_tepl_Raw =
        #if (self.if_valid(tempPir, temp_tepl_Raw) or not self.if_valid(self.ok_t_teplovizor, self.ok_tempPir)
        if ((self.if_valid(temp_tepl_Raw, tempPir) and inputPir == 0) or (not self.if_valid(self.ok_temp_tepl_Raw, self.ok_tempPir )) and inputPir == 0) : 
            self.ok_temp_tepl_Raw,  self.ok_t_teplovizor, self.ok_tempPir , self.ok_inputPir = temp_tepl_Raw, t_teplovizor, tempPir, inputPir
        self.ok_inputPir = inputPir  
        return self.ok_temp_tepl_Raw,  self.ok_t_teplovizor, self.ok_tempPir , self.ok_inputPir

    
    def valid_led(self,*led:pin_Thread, pin_time = 0.5):
        '''
        led: получаем поток pin_Thread, для управления пинами
        pin_time: получаем время активности пина (стандартно 0.5 )
        '''
        if not led is None:
            if self.if_valid():
                all_led.pin_on_time(all_led.pin_namber("red"), pin_time)
                all_led.pin_on_time(all_led.pin_namber("green"), pin_time)
            else:
                all_led.pin_on_time(all_led.pin_namber("red"), pin_time)

    def valid_text(self):
        '''
        вохвращает: текст в зависимости от рабочих данных
        '''
        temt_str = ""
        if self.if_valid():  # если рабочие данные входят в минимальные и в максимальные границы
            temt_str = 'Все хорошо,проходите: {}'.format(self.valid_min())  # берём меньшиее денные, дабы не пугать
        elif not self.if_valid_max():  # если рабочие данные  НЕ входят в максимальные границы
            temt_str = 'Обратитесь к врачу: {}'.format(self.valid_max())


        #elif not self.if_valid_min():  # если рабочие данные  НЕ входят в минимальные границы
        #    temt_str = 'Обратитесь к врачу: {}'.format(self.valid_min())

        return temt_str

    def Str_teplo(self, tip=0):  # текст на  tepl
        '''
        вохвращает: тексты для состояний: тела , руки и общий текст (из рабочих данных)
        '''
        temp_text_telo = temp_text_Pir = temp_text_tepl = ""

        if tip == 1 or tip == 0:
            temp_text_telo = "Ваша температура тела{}".format(self.temp_tepl_Raw)
            if tip == 1:
                return temp_text_telo
        if tip == 2 or tip == 0 :       
            if self.inputPir == 0 :   
                #temp_text_Pir = "Ваша температура по руке {}".format(self.tempPir)   
                temp_text_Pir = "Получаем данные"

            else:
                temp_text_Pir = "Поднесите руку"
            if tip == 2: return temp_text_Pir
        if tip == 3 or tip == 0:
            temp_sostoianie_tepl = self.valid_text()
            if tip == 3 : return temp_sostoianie_tepl  
        
        if tip == 0 : return temp_text_telo, temp_text_Pir, temp_sostoianie_tepl
        return ""
    

    def valid_var(self):
        return self.if_valid()

    def Stop_(self):
        '''
        остановка цикла потока
        '''
        self.if_active = False

    def run(self):
        print("Активация потока teplo_Thread ")
        t = time.time()
        self.if_active = True

        while self.if_active:
            self.if_on = True
            if time.time() - t >= self.time:
                t = time.time()
                self.teplo_teplo()
        self.if_on = False


class Open_Thread(threading.Thread):

    def __init__(self):
        super().__init__()
        # self.daemon = True

        self.if_active = False
        self.if_on = False

        self.if_Ok = False
        self.time = 1

    def Ok_Open(self):  ## ф-я на действие при сраб.
        return 0

    def If_Ok_Open(self):
        if not self.if_Ok:
            self.if_Ok = True

    def on_of(self, iff=None):
        if iff is None:
            self.if_active = not self.if_active
        else:
            self.if_active = iff
        return self.if_active

    def Stop_(self):
        '''
        остановка цикла потока
        '''
        self.if_active = False

    def run(self):
        t = 0
        self.if_active = True

        while self.if_active:
            self.if_on = True
            if time.time() - t >= self.time:
                t = time.time()
                if self.if_Ok:
                    self.if_Ok = False
                    self.Ok_Open()
        self.if_on = False
