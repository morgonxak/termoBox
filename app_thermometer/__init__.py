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



"""

dict_connect_settings = './rc/database.bd'




path_haarcascade = os.path.abspath(
    os.path.join(os.getcwd(), './app_thermometer/rc/haarcascade_frontalface_default.xml'))
#Recognition
face_detector = cv2.CascadeClassifier(path_haarcascade)
pathProject = os.path.abspath(os.path.join(os.getcwd(), './rc'))


k = 1
path_cvm_model = os.path.join(pathProject, 'svm_model_{}.pk'.format(k))
path_knn_model = os.path.join(pathProject, 'knn_model_{}.pk'.format(k))



processing_recognition = processing_faceid(pathProject)
"""
##########################

teplovizor = amg88()
#pirometr = MLX90614(SMBus(1))
"""
dataBase = BD(dict_connect_settings)

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#led
led_red_pin = 23
led_green_pin = 24
pinBuzer = 25

GPIO.setup(led_red_pin, GPIO.OUT)
GPIO.setup(led_green_pin, GPIO.OUT)

GPIO.output(led_red_pin, GPIO.HIGH)
GPIO.output(led_green_pin, GPIO.HIGH)
########################################
#Buzer
GPIO.setup(pinBuzer, GPIO.OUT)
#######################
p = GPIO.PWM(pinBuzer, 1000)  # channel=12 frequency=50Hz
"""

import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

class pirometr_Class():
    def __init__(self, MLX90614, board, MCP):
        
        self.pirometr = MLX90614
        
        #GPIO.setmode(GPIO.BCM) # для работы с GPIO
        #GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP) # подключение дачика растояния
        
        self.board = board
        self.MCP = MCP
        
        
        self.spi = busio.SPI(clock=self.board.SCK, MISO=self.board.MISO, MOSI=self.board.MOSI)

        # create the cs (chip select)
        self.cs = digitalio.DigitalInOut(self.board.D5)

        # create the mcp object
        self.mcp = MCP.MCP3008(self.spi, self.cs)
        
        # create an analog input channel on pin 0
        self.chan = AnalogIn(self.mcp, self.MCP.P0)

    def get_(self):
        input_Pir = 1
        Pir = 0
        Pir_ambient = 0
        
        input_Pir = round(10* pow( ( self.chan.value * 0.0048828125),int(-1))  *100, 1)
        
        #print("input_Pir = ", input_Pir)
        
        #input_Pir  = GPIO.input(18) # ОТКЛЮЧЁН ДАЧИК РАСТОЯНИЯ!!!!!
        Pir = round(self.pirometr.get_object_1(), 1)
        Pir_ambient = round(self.pirometr.get_ambient(), 1)
        '''
        try:
            input_Pir  = GPIO.input(18) # ОТКЛЮЧЁН ДАЧИК РАСТОЯНИЯ!!!!!
            Pir = round(self.pirometr.get_object_1(), 1)
            Pir_ambient = round(self.pirometr.get_ambient(), 1)
            # if GPIO.input(18) == False:#у нас есть отжатая кнопа?
            #    tempPir = round(self.pirometr.get_object_1(),1)
            #print(inputPir, "!!!!!")
        except:  # Queue.Empty
            print("error: teplo_Thread.___teplo___ (Pir)")
            #logging.info("except: teploPir (pirometr) {}".format( time.time())) 
            #pass
            #print("temp_tepl {} tempPir {} temp_tepl_Raw {}".format(temp_tepl, tempPir, temp_tepl_Raw))
        '''
        return input_Pir, Pir, Pir_ambient

pirometr = pirometr_Class(MLX90614(SMBus(1)),board,  MCP)     
       


from pydub import AudioSegment
from pydub import playback
class Song(threading.Thread):
    def __init__(self, filename):
        """initializes the thread"""
        threading.Thread.__init__(self)
        self.daemon = True
        self.SoundFileName = filename
        #self._stopper = Event()
        self.setName('SoundThread'+filename) #
        self.song = AudioSegment.from_mp3(self.SoundFileName)
        self.start_event = threading.Event()
        #print(filename, " ", len(self.song))
        
    def len_(self):
        return len(self.song)/1000
        
    def run1(self):
        """plays a given audio file"""
        self.Active = True
        while(self.Active):
            if self.Active_play:
                playback.play(self.song)
                self.Active_play = False
            time.sleep(1)
            
    def run(self):  
        while self.start_event.wait():
            self.Active_play = True 
            self.start_event.clear()   
            playback.play(self.song)
            self.Active_play = False        
                
    def on(self):
        return self.Active_play #= True
        
    def restart(self):
        self.start_event.set()
    
    #def stop(Active_play):
    #    self.Active
    #    self._stopper.set()
        
    #@staticmethod   


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
            #print(val.text , " ",val.pin," ",val.ct," ",val.if_," ",val.mig, " ",val.time)

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

"""
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


def valid(tempPir, t_teplovizor):
    '''
    Решения о состоянии здоровья
    :param tempPir:
    :param t_teplovizor:
    :return: текст сообщения
    '''
    if t_teplovizor >= 37.2 or tempPir >= 37.2:
        GPIO.output(led_red_pin, GPIO.LOW)
        if tempPir == -1:
            return True, 'Обратитесь к врачу: {}'.format(t_teplovizor)
        else:
            return True, 'Обратитесь к врачу: {}: '.format(round(numpy.max([t_teplovizor, tempPir]), 1))
    else:
        GPIO.output(led_green_pin, GPIO.LOW)
        if tempPir == -1:
            return False, 'Все хорошо, проходите: {}'.format(t_teplovizor)
        else:
            return False, 'Все хорошо, проходите: {}'.format(round(numpy.max([t_teplovizor, tempPir]), 1))
"""