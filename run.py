#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 13:10:45 2020

@author: admin
"""


import cv2
import time
import threading
import numpy 
import logging ## лог

#from multiprocessing.pool import ThreadPool
from multiprocessing import Process , Queue #,Pool 
#import tkinter as tk
import sys
from sys import platform
# True False
if_test_wimdovs = False # тест на винде?
if platform == "linux" or platform == "linux2":
    if_test_wimdovs = False
else:
    if_test_wimdovs = True

if if_test_wimdovs:
    face_detector = cv2.CascadeClassifier(r'C:\Users\Admin\Desktop\python\haarcascade_frontalface_default.xml')
    led_red_pin = 23
    led_green_pin = 24
else:
    import RPi.GPIO as GPIO
    from app_thermometer import face_detector, processing_recognition, teplovizor, dataBase, pirometr, valid, led_red_pin, led_green_pin, on_buzer


def Id_to_face(fase_RGB_200_200, return_Id_to_face): # поиск по фото
    id_person = -1
    if not if_test_wimdovs:
        id_person = processing_recognition.predict_freme(fase_RGB_200_200)
    #if return_Id_to_face.get() == -1 :
    return_Id_to_face.put(id_person)





"""
def led_off(led_pin,on = False): # выкл свет 
    #print("{}, {}".format(led_pin,on)) 
    if on == True:
        if if_test_wimdovs:
            print("{} GPIO.LOW {}".format(led_pin,on))
        else:
            GPIO.output(led_pin, GPIO.LOW) # выкл HIGH
            #print("{} GPIO.LOW {}".format(led_pin,on))
    else:
        if if_test_wimdovs:
            print("{} GPIO.HIGH {}".format(led_pin,on))
        else:
            GPIO.output(led_pin, GPIO.HIGH) # выкл LOW
            #print("{} GPIO.HIGH {}".format(led_pin,on))
        
def led_all_off(on = False): # выкл свет  
    led_off(led_red_pin,on)
    led_off(led_green_pin,on)      

def led_red(on): # вкл/выкл свет
    led_off(led_red_pin,on)  

def led_green(on): # вкл/выкл свет
    led_off(led_green_pin,on) 


def led_mig(led_pin, on = True): # вкл/выкл свет
    led_off(led_pin,on)  
    led_off(led_pin,not on)      

def led_all_mig(saze = 1, on = True): # вкл/выкл свет
    for i in range(1, saze):
        led_mig(led_red_pin,on)  
        led_mig(led_green_pin,on)   

def led_red_mig(saze = 1, on = True): # вкл/выкл red свет
    for i in range(1, saze):
        led_mig(led_red_pin,on)   

def led_green_mig(saze = 1, on = True): # вкл/выкл green свет
    for i in range(1, saze):
        led_mig(led_green_pin,on)     

"""




def Str_ID(id_person):# текст на  id
    if id_person == None:
        temp_text =  "Не распознан"
    elif id_person == -1:
        temp_text = "Подойдите ближе для распознования" #"" #
    else :
        temp_text = "Привет, {}".format(dataBase.get_people_name_by_person_id(id_person))
    return temp_text

def if_valid_min(tempPir, t_teplovizor):
    if t_teplovizor == 0 or tempPir == 0:
        #return False, 'Нет всей информации по температуре. '
        return False
    teplmin = round(numpy.max([t_teplovizor, tempPir]), 1)
    #print("teplmin {}".format(teplmin))
    if 29 < teplmin:
        #led_green(False)
        #led_red(True)
        #return True, 'Обратитесь к врачу: {}'.format(teplmin)
        return True
    else:
        #return False, 'Все хорошо,проходите: {}'.format(t_teplovizor)
        return False
    
def if_valid(tempPir, t_teplovizor):
    '''
    Решения о состоянии здоровья
    :param tempPir:
    :param t_teplovizor:
    :return: текст сообщения
    '''
    if t_teplovizor == 0 or tempPir == 0:
        #return False, 'Нет всей информации по температуре. '
        return False, 0    

    teplmax = round(numpy.max([t_teplovizor, tempPir]), 1)
    teplmin = round(numpy.min([t_teplovizor, tempPir]), 1)
    if teplmax >= 37.2 :    
        #led_green(False)
        #led_red(True)
        #return True, 'Обратитесь к врачу: {}'.format(teplmax)
        return True, teplmax
    elif 29 > teplmin:
        #led_green(False)
        #led_red(True)
        #return True, 'Обратитесь к врачу: {}'.format(teplmin)
        return True, teplmin
    else:
        #return False, 'Все хорошо,проходите: {}'.format(t_teplovizor)
        return False, t_teplovizor







def valid(tempPir, t_teplovizor):
    global all_led
    '''
    Решения о состоянии здоровья
    :param tempPir:
    :param t_teplovizor:
    :return: текст сообщения
    '''
    temt_if,t_teplo = if_valid(tempPir, t_teplovizor)
    
    #print("t_teplovizor {} tempPir {} if {}".format(t_teplovizor, tempPir, temt_if))
    
    temt_str = ""
    if t_teplo == 0: 
        temt_str = 'Нет всей информации по температуре. '
    else:
        #all_led.led_mig(all_led.led_namber("red"),True)
        
        
        #led_green(False)
        #led_red(True)
        if temt_if:
            temt_str = 'Обратитесь к врачу: {}'.format(t_teplo)
            all_led.led_on_time(all_led.led_namber("red"),0.5)
        else:
            temt_str = 'Все хорошо,проходите: {}'.format(t_teplo)
            all_led.led_on_time(all_led.led_namber("red"),0.5)
            all_led.led_on_time(all_led.led_namber("green"),0.5)

    return temt_if, temt_str
    
      
def valid_text(tempPir, t_teplovizor):
    iff, text = valid(tempPir, t_teplovizor)
    return text    

def valid_var(tempPir, t_teplovizor):
    temt_if,t_teplo = if_valid(tempPir, t_teplovizor)
    return temt_if    

def teplo(temp_tepl_Raw=0, temp_tepl=0, tempPir=0): # цифры на  tepl
    temp_tepl_Raw = temp_tepl = tempPir = 0
    try:
        temp_tepl_Raw, temp_tepl = teplovizor.getMaxTemp()
        temp_tepl+=3
        if GPIO.input(18) == False:#у нас есть отжатая кнопа?  
            tempPir = round(pirometr.get_object_1(),1)
            tempPir+=3
        #else:
            #led_red(False)
        
    except: # Queue.Empty
        pass
    #print("temp_tepl {} tempPir {} temp_tepl_Raw {}".format(temp_tepl, tempPir, temp_tepl_Raw))
                        
    return temp_tepl_Raw, temp_tepl, tempPir

def Str_teplo(temp_tepl_Raw=0, temp_tepl=0, tempPir=0):# текст на  tepl
    temp_text_telo = "Ваша температура {}".format(temp_tepl)  
    #if (32 < tempPir < 45):
    if tempPir != 0 :   
        temp_text_Pir = "Ваша температура по руке {}".format(tempPir)
    else : 
        temp_text_Pir = "Поднесите руку"
    temp_text_tepl = valid_text(temp_tepl, tempPir)
    return temp_text_telo, temp_text_Pir, temp_text_tepl

def faces_x_y(frame, x , y , w , h): # ф-я для поиска границ
    x = y = w = h = 0
    x1 = y1 = w1 = h1 = 0
    if not frame is None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
        for (x1 , y1 , w1 , h1) in faces:
            x , y , w , h = x1 , y1 , w1 , h1 
            break
            
    return x , y , w , h

def text_separator(text, saze = 20):# делим строку над подстроки стараясь по размерм. (уберает 2е пробелы)
    """
    text -  текст
    saze - мах размер
    """
    list = []
    if len(text) <= saze:
        list.append(text.strip())  
    else:
        text_temp = ""
        text_temp_end = 0
        saze_temp = 0
        for w in text.split():#пройтись по каждому слову
            if text_temp != "" and saze_temp + len(w) > saze:
                list.append(text_temp.strip())     
                text_temp = ""
                saze_temp = 0
                text_temp_end = 0
                
            if text_temp == "" and len(w) > saze:
                list.append(w.strip()) 
                text_temp_end = 0
                text_temp = ""
                saze_temp = 0 
            else:
                if saze_temp + len(w)  <= saze:
                    saze_temp += len(w) 
                    text_temp += w
                    text_temp_end = 1 
                else:    
                    list.append(text_temp.strip()) 
                    text_temp_end = 0
                    saze_temp = len(w)
                    text_temp = w 
                    
                    text_temp_end = 1
    
                if saze_temp != 0 and saze_temp <= saze-1:
                    saze_temp += 1
                    text_temp += " "
        if text_temp_end == 1 :
            list.append(text_temp.strip())
    return list
    

def cv2_putTex_rectangle(frame, text, x, y , distance_lines, cv2_FONT, fontScale, color_text, thickness,  color_font, lineType): # вывод текста с фоном
    x1,y1 = x, y
    w1 = h1 =0
    if text !=" ":       
        [(text_width, text_height), baseline] = cv2.getTextSize(text, cv2_FONT, fontScale, thickness)
        if text_width != 0 and text_height != 0:
            dist = int (distance_lines/2)
            cv2.rectangle(frame, (x-dist, y+dist), (x+text_width+dist, y-text_height-dist), color_font, -1)
            cv2.putText(frame, text, (x, y), cv2_FONT, fontScale, color_text, thickness, lineType)
            x1, y1, w1, h1 = x, y, text_width , text_height + distance_lines
    return x1, y1, w1, h1
 
def cv2_text_separator_putTex_rectangle(frame, text, x, y, cv2_FONT, fontScale, color_text, thickness,  color_font, lineType, direction=0): # вывод текста с фоном с направлением 1- вверх, 0 - вниз
    if text !=" ":
        list_text = text_separator(text, 20) # делим строку над подстроки стараясь по размерм. (уберает 2е пробелы)   
        saze_list = len(list_text) 
        [(text_width, text_height), baseline] = cv2.getTextSize(list_text[0], cv2_FONT, fontScale, thickness)
        
        d=0
        x1=y1=w1=h1=0
        x1 = x
        distance_lines = text_height
        if direction == 1: #вверх 
            d=-1 
            y1 = y-text_height*(saze_list) 
        elif direction == 0:  # вниз
            y1 = y +distance_lines *2
            d=1
        i=0
        for _text in list_text:#пройтись по каждому слову
            #cv2_putTex_rectangle(frame, _text, x, y+d*(text_height*((saze_list)-i)+10), cv2_FONT, fontScale, color_text, thickness,  color_font, lineType) # вывод текста с фоном
            x1,y1,w1,h1 = cv2_putTex_rectangle(frame, _text, x1, y1+d*(h1),distance_lines, cv2_FONT, fontScale, color_text, thickness,  color_font, lineType) # вывод текста с фоном
            i+=1

def cv2_putText_flag_id_on(flag_id_on, q_w, q_h, r_w, thickness=4):##вывод v/x на экран
    if flag_id_on: #если нашли человека
        cv2.putText(frame, "V", (q_w, q_h), cv2.FONT_HERSHEY_SIMPLEX, r_w, (0, 255, 0), thickness, cv2.LINE_AA)
    else:
        cv2.putText(frame, "X", (q_w, q_h), cv2.FONT_HERSHEY_SIMPLEX, r_w, (0, 0, 255), thickness, cv2.LINE_AA) 


def cv2_rectangle_min_W_H(height, width):# размер минимальных границ
    w = h = 0
    if height + width != 0:
        d=3# КОФИЦИЕНТ НА МИН ДЛИНУ РАСПОЗНАНИЯ
        w = h = round(numpy.max([height/d, width/d]), 0) 
    if w <= 2 or h <= 2:
        w = h = 150
    return w, h

def cv2_height_width(frame, height=0, width=0):# размер скрина
    #height, width = 626, 537 #зармеры экрана
    if height + width == 0:
        height = numpy.size(frame, 0)
        width = numpy.size(frame, 1)
    return height, width

def cv2_putText_x_y(frame, id_person, temp_tepl_Raw, temp_tepl, tempPir, x, y, w, h): # вывод имя и текста на экран
    if x + w + y + h > 0:
        color_text =(0, 114, 255) #(33, 47, 252) #(255, 150, 0) # цвет text
        id_person1 = id_person
        color_font = (255, 0, 0)
        if id_person1 ==-1: id_person1 =  None
        
        temp_text_telo, temp_text_Pir, temp_text_tepl = Str_teplo(temp_tepl_Raw, temp_tepl, tempPir)# получаем текст на тепл
        
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)#вывод квадр
        
        r_w = w/400
        FONT_ = cv2.FONT_HERSHEY_COMPLEX
        
        #TStr_ID1  = Str_ID(id_person1)
        #if TStr_ID2 !=" ": TStr_ID1 = " "
        #if TStr_ID2 !=" ":
            #cv2.rectangle(frame, (0, x, y-10), (30, 30*len(TStr_ID1)), (255, 255, 255), -1)
    
            #cv2.putText(frame, TStr_ID1, (x, y-10), cv2.FONT_HERSHEY_COMPLEX , r_w, (color_text), 2)
            #cv2_putTex_rectangle(frame, TStr_ID1, x, y-10, cv2.FONT_HERSHEY_COMPLEX , r_w, color_text, 2, color_font, 2)
        cv2_text_separator_putTex_rectangle(frame, Str_ID(id_person1), x, y, FONT_ , r_w, color_text, 2, color_font, 2,1)
        
        cv2_text_separator_putTex_rectangle(frame, temp_text_tepl, x, y + h ,  FONT_ , r_w, color_text, 2, color_font, 2,0)   
        """
        if len(temp_text_tepl) > 20:
            temp_text_tepl1 = temp_text_tepl[:20] 
            temp_text_tepl2 = temp_text_tepl[20:]
            
            
            cv2_putTex_rectangle(frame, temp_text_tepl1, x, y + h + 30, cv2.FONT_HERSHEY_COMPLEX , r_w, color_text, 2, color_font, 2)
            cv2_putTex_rectangle(frame, temp_text_tepl2, x, y + h + 60, cv2.FONT_HERSHEY_COMPLEX , r_w, color_text, 2, color_font, 2)
            #cv2.putText(frame, temp_text_tepl1, (x, y + h + 30), cv2.FONT_HERSHEY_COMPLEX , r_w, (color_text), 2)
            #cv2.putText(frame, temp_text_tepl2, (x, y + h + 60), cv2.FONT_HERSHEY_COMPLEX , r_w, (color_text), 2)
        else:
            #cv2.putText(frame, temp_text_tepl, (x, y + h + 30), cv2.FONT_HERSHEY_COMPLEX , r_w, (color_text), 2)
            cv2_putTex_rectangle(frame, temp_text_tepl, x, y + h + 30, cv2.FONT_HERSHEY_COMPLEX , r_w, color_text, 2, color_font, 2)
        """
    
def cv2_putText_x_y_time_out_(frame, id_person, temp_tepl_Raw, temp_tepl, tempPir, x, y, w, h, time_out_, if_save_time):  # вывод знака и  таймера + cv2_putText_x_y
    if x + w + y + h >0 and time_out_ > 0:

        r_w = w/200#w/(23) #w/23 / 21.5
        q_h =y+60 #int(y+(h/2 + r_w*(10.5))) #y+h-10
        q_w =x+10 #int(x+(w/2 - r_w*(9.7)))
        if  1.0 < time_out_ and (not if_save_time): # выводим время
            cv2.putText(frame, "{}".format(int(time_out_)), (q_w, q_h), cv2.FONT_HERSHEY_SIMPLEX, r_w, (0, 255, 0), thickness_fase, cv2.LINE_AA)
        elif time_out_ <= 1.0 or (if_save_time): # выводим распазнание # 0.5 <
            cv2_putText_flag_id_on(flag_id_on, q_w, q_h, r_w, thickness_fase)#вывод v/x на экран
    
        cv2_putText_x_y(frame, id_person, temp_tepl_Raw, temp_tepl, tempPir, x, y, w, h)


def clearQueue(q): # обнуление очереди (чтоб без матов(часть костыля #1))
    try:
        while True:
            q.get_nowait()
    except: # Queue.Empty
        pass
def maximizeContrast(imgGrayscale):
    """
    width, height2,w,w= cv2.getWindowImageRect('window')
    height = numpy.size(imgGrayscale, 0)
    width = numpy.size(imgGrayscale, 1)
    #print (cv2.getWindowImageRect('window'))
    
    
    imgGrayscale1222 = numpy.copy(imgGrayscale)
    
    for i1, item1 in enumerate(imgGrayscale1222):
        for i2, item2 in enumerate(item1):
            for i3, item3 in enumerate(item2):
                print (item3) #=255
                
                
    """
    """
    coll = numpy.array([255, 255, 255])
    print ("0")
    
    srt_1 = numpy.full((height2-height, width,3), 255)
    
    print(width, height2,w,w)
    print(numpy.size(imgGrayscale, 0) ,numpy.size(imgGrayscale, 1), numpy.size(imgGrayscale, 2), imgGrayscale[0][0][0])
    print(numpy.size(srt_1, 0) ,numpy.size(srt_1, 1), numpy.size(srt_1, 2), srt_1[0][0][0])
    
    #srt_ = numpy.full(width, coll)
    #print ("1")
    #srt_2 = numpy.full(height,srt_)
    print ("2")
    #del srt_
    imgGrayscale2 = numpy.vstack(imgGrayscale, srt_1)
    print ("3")
    del srt_1
    del imgGrayscale
    print ("4")
    imgGrayscale =imgGrayscale2
    print ("5")
    """
    return imgGrayscale



def frame_image(If_Test_Foto, ret , frame, image): # или скрин или фото от If_Test_Foto
    del frame #переменная под фрейм с камеры
    frame = None #переменная под фрейм с камеры
    if not If_Test_Foto :
        ret , frame = cap.read()               
        if not frame is None:
            frame = cv2.flip(frame,1) # ореентация камеры
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE) 
            frame = maximizeContrast(frame )
            #frame = frame = [:, 185:455]
        else: 
            logging.error("except: frame is None")                       
            raise Exception("frame is None")
    else:
        frame = numpy.copy((image))
    return frame 
    
         







class Thread_all(threading.Thread):
    
    def __init__(self):
        super().__init__()
        self.daemon = True
        
        self.if_active = False
        self.if_ran = False
        self.if_on = False
        
        self.if_Ok = False
        
        self.temp_tepl_Raw = 0
        self.t_teplovizor = 0
        self.tempPir = 0
        
    def teplo_teplo(self):
        self.temp_tepl_Raw, self.t_teplovizor, self.tempPir = teplo(self.temp_tepl_Raw, self.t_teplovizor, self.tempPir)
    def teplo(self):
        
        return self.temp_tepl_Raw, self.t_teplovizor, self.tempPir
    def if_valid_min(self):
        return if_valid_min(self.tempPir, self.t_teplovizor)
    def if_valid(self):
        return if_valid(self.tempPir, self.t_teplovizor)
    def valid(self):
        return valid(self.tempPir, self.t_teplovizor)
    def valid_text(self):
        return valid_text(self.tempPir, self.t_teplovizor) 
    def valid_var(self):
        return valid_var(self.tempPir, self.t_teplovizor)
    
    def Ok_Open(self): ## ф-я на действие при сраб.
        return 0
    def If_Ok_Open(self):
        if not self.if_Ok:
            self.if_Ok = True
    def on_of(self,iff = None):
        if iff == None: 
            self.if_active = not self.if_active 
        else:
            self.if_active = iff
        return self.if_active 
        
    
    def run(self):
        self.if_on = True
        t = time.time()
        self.if_active = True
        
        while self.if_active:
            #print(self.temp_tepl_Raw, self.t_teplovizor, self.tempPir)
            if time.time()-t >= 0.1:
                t = time.time()
                self.teplo_teplo()
                if self.if_Ok:
                    self.if_Ok = False
                    self.Ok_Open()
        self.if_on = False








class led_Thread(threading.Thread):
    def __init__(self, if_test_wimdovs):
        super().__init__()
        self.if_test_wimdovs = if_test_wimdovs
        self.if_active = False 
        self.daemon = True
        
        self.led_pin_text = ["red", "green"] #название
        self.led_pin = [23, 24] #пин
        self.led_pin_ct = [False, False] #состояние
        self.led_pin_if = [False, False] #режим
        self.led_pin_mig = [False, False] #мигание
        self.led_pin_time = [0.0 , 0.0] #время активности
        """
        self.led_pin_text = [] #название
        self.led_pin = [] #пин
        self.led_pin_ct = [] #состояние
        self.led_pin_if = [] #режим
        self.led_pin_mig = [] #мигание
        self.led_pin_time = [] #время активности
        
        self.led_add("red",23)
        self.led_add("green",24)
        
        
        GPIO.setmode(GPIO.BCM)
        for i, val in enumerate(self.led_pin):
            GPIO.setup(val, GPIO.OUT)
            GPIO.output(val, GPIO.HIGH)
            self.led_(i,False)
        
        """
        
        
    def led_reg(self, nled_pin=None):
        try:
            if nled_pin != None:
                if isinstance(nled_pin, int):
                    GPIO.setup(self.led_pin[nled_pin], GPIO.OUT)
                    GPIO.output(self.led_pin[nled_pin], GPIO.HIGH)
                    self.led_(nled_pin,False)
                else:
                    print("led_reg tip error")
                    return -1
            else:
                for i, val in enumerate(self.led_pin):
                    GPIO.setup(val, GPIO.OUT)
                    GPIO.output(val, GPIO.HIGH)
                    self.led_(i,False)
        except: 
            print("led_reg error")
            return -2
        return 0
        
    def led_add(self, Name : str, pin: int):
        self.led_pin_text.append(Name)
        self.led_pin.append(pin)
        self.led_pin_ct.append(False)
        self.led_pin_if.append(False)
        self.led_pin_mig.append(False)
        self.led_pin_time.append(0.0)
        
        
    
    def led_(self, nled_pin, on = False):
        if self.led_pin_ct[nled_pin] != on:
            if on == True:
                if if_test_wimdovs:
                    print("{} GPIO.LOW {}".format(self.led_pin[nled_pin] ,on))
                else:
                    GPIO.output(self.led_pin[nled_pin] , GPIO.LOW) # выкл HIGH
                    #print("{} GPIO.LOW {}".format(led_pin,on))
            else:
                if if_test_wimdovs:
                    print("{} GPIO.HIGH {}".format(self.led_pin[nled_pin] ,on))
                else:
                    GPIO.output(self.led_pin[nled_pin] , GPIO.HIGH) # выкл LOW
                    #print("{} GPIO.HIGH {}".format(led_pin,on))
            self.led_pin_ct[nled_pin] = on
            
    def led_mig(self, nled_pin, on):
        
        #print("led_mig")
        if self.led_pin_mig[nled_pin] != on:
            for i, val in enumerate(self.led_pin):
                if nled_pin == i:
                    #print("led_mig" , i)
                    self.led_pin_mig[i] = on
                else:
                    self.led_pin_mig[i] = False
                
                
    def led_sost(self, nled_pin):
        return self.led_pin_if[nled_pin] or self.led_pin_time[nled_pin] != 0.0
        
    def led_all_one(self, nled_pin, on):
        
        for i, val in enumerate(self.led_pin):
            if nled_pin == i:
            
                self.led_(i,on)
                self.led_on_off(i,on)
            else:
                if self.led_sost(i): # если активен
                    self.led_(i,False)
                    self.led_on_off(i,False)    
    
    def led_all(self, on = False): # выкл свет  
        for i, val in enumerate(self.led_pin):
            self.led_(i,on)
            self.led_on_off(i,on)
            
    def led_on_time(self, nled_pin, tim):
        self.led_pin_if[nled_pin] = False
        self.led_pin_time[nled_pin] = time.time()+tim
        
    def led_on_off(self, nled_pin, on):
        self.led_pin_time[nled_pin] = 0.0
        self.led_pin_if[nled_pin] = on
        
        
        
    def led_n(self, led_pin :int):
        #print("led_n int")
        return self.led_pin.index(led_pin)
    
    
    def led_n(self, led_pin :str):
        #print("led_n str")
        return self.led_pin_text.index(led_pin)
        
    
        
    def led_namber(self, led_pin = None):
        #print(led_pin)
        try:
            if isinstance(led_pin, str):
                return self.led_pin_text.index(led_pin)
            elif isinstance(led_pin, int):
                return self.led_pin.index(led_pin)
        except: 
            print("led_namber tip error")
            return -1
        #print("led_namber")
        #return self.led_n(led_pin)
        
    def Stop(self):
        self.if_active = False 
        
    def run(self):
        self.if_on = True
        t = time.time()
        self.if_active = True 
        #print("1")
        while self.if_active:
            for i, val in enumerate(self.led_pin):
                
                
                time_ = self.led_pin_time[i] - time.time() 
                if time_ > 0 or self.led_pin_if[i]:
                    #print("1 2")
                    self.led_(i,True)
                elif time_ <= 0 and self.led_pin_time[i] != 0.0: 
                    self.led_on_off(i,False)
                    t=time.time() 
                    while time.time() - t<0.5:
                        None
                elif self.led_pin_mig[i]:
                    self.led_all_one(i,True)
                    for number in range(2):# колво мигов
                        for number in range(0,1):
                            #print(number == 0)
                            self.led_on_off(i,number == 0)
                            t=time.time() 
                            while time.time() - t<1:
                                None
                        #self.led_on_off(i,False)
                        #t=time.time() 
                        #while time.time() - t<1:
                        #    None
                    self.led_mig(i, False)
                else:
                    #print("1 4")
                    self.led_(i,False)
                    
                
        self.led_all(False)
        self.if_on = False
     





# True False
If_Test_Foto = False # тест по фото
If_Test_print_reset = False # вывод состояний ресетов
For_bz = 0 # счёсик для кол-во перезапусков
height, width = 0, 0 # размер экрана
thickness_fase = 4 # размер символов в квадрате

cap = None
if not If_Test_Foto :
    cap = cv2.VideoCapture(0) # подкл к камере 
    #height, width, channels = img.shape
font = cv2.FONT_HERSHEY_COMPLEX # фон
if not if_test_wimdovs:
    cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN) 
    cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
image = None   
if If_Test_Foto :
    image = cv2.imread("./Test.jpg")    
frame = None #переменная под фрейм с камеры
ret = False # фрейм прочитан корректно?
frame = frame_image(If_Test_Foto, ret , frame, image)# или скрин или фото

height, width = cv2_height_width(frame, height ,width )# размер скрина
min_w, min_h = cv2_rectangle_min_W_H(height ,width)
x = y = w = h = 0


if __name__ == "__main__":
    # без обнуления
    return_Id_to_face = Queue() #очередь для сняти инфы с потока     
    time_out = 6 # таймер на определение человека
    flag_disease = False  # на решение по темпер
    time_ = 0 # продолжительность скана лица
    Active = True # актив прогр
    color = (255, 255, 255) # цвет задника
    time_Sql = 0
    # с особым обнулением
    id_hread =  None #для потока
    if_null_hread = False #  (можно ли обнулить именно id_hread )
    
    # с обнулением
    time_temp1 = time.time() #начало сканирования лица #для шага в программе
    fase_RGB_200_200 = None # под скрин лица
    flag_id_on = False # найден ли id
    return_Id_to_face.put(-1) # для сняия с потока инф(чтоб без матов(часть костыля #1))
    f_save_time = False # ускорение вывода
    if_save = True # было ли сохранение (можно ли сохранить )
    id_person = -1 # переменная под персонал
    frame = None #переменная под фрейм с камеры
    ret = False # фрейм прочитан корректно?
    if_null = True #  (можно ли обнулить)
    if_on = False # при выполнении проверки на всё
    if_on_fase = False # найден ли id
    ime_out_ = 0
    all_Thr = Thread_all()
    
    all_led = led_Thread(if_test_wimdovs)
    #all_Thr.daemon = True
    all_Thr.start()
    all_led.start()
    while(Active):
        #temp_tepl_Raw, temp_tepl, tempPir = teplo()# получаем тепло 
        temp_tepl_Raw, temp_tepl, tempPir = all_Thr.teplo()
        
        
        #print(height, width)
        
        
        


        
        
        
        
        
        
        
        
        time_ = time.time() - time_temp1        
        if if_null: # обнуление
            time_out_ = 0
            #logging.info("Reset {}".format( time.time()))
            #led_all_off() # выкл свет  time_out = time_out_const # таймер на определение человека
            all_led.led_all(False)
            if_save_time = False # ускорение вывода
            time_temp1 = time.time() #начало сканирования лица
            del fase_RGB_200_200 # под скрин лица
            fase_RGB_200_200 = None # под скрин лица
            flag_id_on = False # найден ли id
            return_Id_to_face.put(-1) # для сняия с потока инф (чтоб без матов(часть костыля #1))
            if_save = True # было ли сохранение (можно ли сохранить )
            id_person = -1 # переменная под персонал
            ret = False # фрейм прочитан корректно?
            if_null = False #  (можно ли обнулить)
            if_on = False # при выполнении проверки на всё
        if if_null_hread: # возможно косяки...
            if not id_hread is None: # сущ ли процесс
                if id_hread.is_alive():# заверш ли процесс
                    if_null_hread = True #  (можно ли обнулить именно id_hread )# возможно косяки...
                    if If_Test_print_reset:print("1 id_hread")  
                if not id_hread.is_alive():    
                    id_hread.close()
                    if If_Test_print_reset:print("1 id_hread 1")  
                    id_hread = None
                    if_null_hread = False
        try:
            frame = frame_image(If_Test_Foto, ret , frame, image) # или скрин или фото
            x, y, w, h  = faces_x_y(frame, x , y, w, h)
            
            
            
            
            if x + y + w + h != 0 and (min_w <=w or min_h <=h ) and not if_null_hread:
                if If_Test_print_reset:print("next")
                if not flag_id_on:
                    if id_hread is None:#если процесс не сущ
                        fase_RGB_200_200 = numpy.copy((frame)[y:y + w, x:x + h]) 
                        clearQueue(return_Id_to_face) # обнуление очереди( костыль #1)
                        id_hread = Process(target=Id_to_face, args=(fase_RGB_200_200,return_Id_to_face))#, daemon=True
                        id_hread.start()#запуск потока по поиску в бд      
                time_out_ = time_out-time_
                
                if not flag_id_on and  1.5 < time_out_ :
                    if not id_hread is None: # сущ ли процесс
                        if not id_hread.is_alive(): # заверш ли процесс
                            try:
                                id_person_temp = return_Id_to_face.get() # вытаскиваем ID
                                if If_Test_print_reset:print("id_person_temp {}".format(id_person_temp))
                            except:
                                logging.error("except: return_Id_to_face.get() {}".format( time.time()))
                                if If_Test_print_reset:print("except: return_Id_to_face.get()")
                                id_person_temp = -1
                                id_hread.terminate()
                            if id_person == -1: id_person = None
                            if id_person is None: id_person = id_person_temp
                            if If_Test_print_reset:print("id_person {}".format(id_person))
                            if id_person is None or id_person == -1: # если нет id, то попытка ещё раз его получить с нового фрейма
                                if If_Test_print_reset:print("2 id_hread") 
                                #id_hread.terminate()
                                id_hread.close()
                                id_hread = None
                                if If_Test_print_reset:print("2 id_hread 1") 
                flag_id_on = flag_id_on or (not (id_person is None or id_person == -1))# найден ли id
                
                
                #if (not (id_person is None or id_person == -1)) and ((32 < tempPir < 45) and (32 < temp_tepl < 45) and 1.0 < time_out_):
                if (not (id_person is None or id_person == -1)): 
                    if (not valid_var(temp_tepl, tempPir) and 1.0 < time_out_):
                        if_save_time = True # ускорение вывода
                    
                if  0.5 < time_out_ and (not if_save_time): # выводим время
                    pass 
                elif 0.1 < time_out_ <= 0.5 or (if_save_time):  # сохраняем   
                    if_save_time = False
                    For_bz += 1 
                    logging.info("For_bz = {} |time:{}".format(For_bz, time.time()))
                    #print("1")   
                    
                    if  if_save  : 
                        #if ((32 < tempPir < 45) and (32 < temp_tepl < 45)): # защита от нелюдей
                        
                        #######flag_disease = valid_var(temp_tepl, tempPir) 
                        
                        #print("temp_tepl {} tempPir {} {}".format(temp_tepl, tempPir, flag_disease))
                        #if (not flag_disease): # защита от нелюдей
                        #print(if_valid_min(temp_tepl, tempPir))
                        if if_valid_min(temp_tepl, tempPir):
                            #print("1 0")   
                            if_save = False
                            #print("on_buzer")
                            #flag_disease = valid_var(temp_tepl, tempPir) 
                            
                            #print("1 0 1")
                            flag_disease = valid_var(temp_tepl, tempPir) 
                            if If_Test_print_reset:print("on {} log {}".format(flag_disease, id_person))
                            
                            #if flag_id_on:
                            #print("1 0")
                            logging.info("dataBase id_person= {} |flag_disease: {}".format(id_person, flag_disease))
                            
                            #print("1 1")   
                            on_buzer(True)
                            
                            #print("1 2")
                            
                            if time.time() - time_Sql > 1 : # чтоб небыло повторов
                                time_Sql = time.time()
                                print("dataBase.push_data_log") 
                                dataBase.push_data_log(flag_disease, fase_RGB_200_200,  person_id=id_person, temp_pirom=tempPir, temp_teplovizor=temp_tepl, raw_pirom=temp_tepl_Raw)
                            
                            
                            #print("1 3")
                            if (not flag_disease) and flag_id_on: # если человек и температ, то действие
                                if_on = True # при выполнении проверки на всё
                            else:      
                                logging.info("off id_person= {} |time:{}".format(id_person, time.time()))
                                #all_led.led_on_time(all_led.led_namber("red"),0.5)
                                all_led.led_mig(all_led.led_namber("red"),True)
                                
                                #led_green(False)
                                #led_red(True)
                        else: 
                            #all_led.led_on_time(all_led.led_namber("red"),0.5)
                            all_led.led_mig(all_led.led_namber("red"),True)
                            #led_green(False)
                            #led_red(True)
                        if  not if_save  :
                            if_null = True
                            if If_Test_print_reset:print("reset not if_save")  
                else: 
                    if_null = True
                    if If_Test_print_reset:print("reset time_out_ < 0.1")  
                cv2_putText_x_y_time_out_(frame, id_person, temp_tepl_Raw, temp_tepl, tempPir, x, y, w, h, time_out_, if_save_time)     
            else: 
                if_null = True
                if If_Test_print_reset:print("reset x-y-h-w")  
                
            cv2.imshow('window', frame)
        except: 
            if_null = True
            if If_Test_print_reset:print("reset except")    
            logging.error("except: except {}".format( time.time()))
            
        if if_on:# если человек и температ, то действие
            logging.info("on id_person= {} :{}".format(id_person, time.time()))
            print("on")
            all_Thr.If_Ok_Open()
            if_on = False # при выполнении проверки на всё
            #all_led.led_on_time(all_led.led_namber("green"),0.5)
            all_led.led_mig(all_led.led_namber("green"),True)
            #led_red(False)
            #led_green(True)

            #  действие
            #time.sleep(2)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            if not id_hread is None:
                if id_hread.is_alive():
                    #id_hread.join()
                    id_hread.terminate()
                id_hread.close()
            cv2.destroyAllWindows()
            #led_all_off() # выкл свет
            Active = False
            #break
    if not If_Test_Foto :
        cap.release()

