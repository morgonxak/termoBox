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

logging.basicConfig(filename="sample.log", level=logging.INFO)
#from multiprocessing.pool import ThreadPool
#from multiprocessing import Process , Queue #,Pool 
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
else:
    import RPi.GPIO as GPIO
    from app_thermometer import face_detector, processing_recognition, BD, dataBase, on_buzer #,teplovizor, pirometr, valid, pin_red_pin, pin_green_pin  
    from app_thermometer import x_y_w_h_object, frame_Thread, pin_Thread, teplo_Thread, Open_Thread
"""
def Str_ID(id_person):# текст на  id
    if id_person == None:
        temp_text =  "Не распознан"
    elif id_person == -1:
        temp_text = "Подойдите ближе для распознования" #"" #
    else :
        temp_text = "Привет, {}".format(dataBase.get_people_name_by_person_id(id_person))
    return temp_text
    
"""
"""
def text_separator(text, saze = 20):# делим строку над подстроки стараясь по размерм. (уберает 2е пробелы)
    '''
    text -  текст
    saze - мах размер
    '''
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
"""    
"""
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
""" 
"""
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
"""
'''
def cv2_putText_flag_id_on(flag_id_on, q_w, q_h, r_w, thickness=4):##вывод v/x на экран
    if flag_id_on: #если нашли человека
        cv2.putText(frame, "V", (q_w, q_h), cv2.FONT_HERSHEY_SIMPLEX, r_w, (0, 255, 0), thickness, cv2.LINE_AA)
    else:
        cv2.putText(frame, "X", (q_w, q_h), cv2.FONT_HERSHEY_SIMPLEX, r_w, (0, 0, 255), thickness, cv2.LINE_AA) 
'''
"""
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
        '''
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
        '''
"""  
'''  
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

'''









class cv2_out_object():
    def __init__(self, BD:BD, frame_Th:frame_Thread, teplo_Th:teplo_Thread, pin_Th:pin_Thread):
        self.dataBase = BD
        self.color_blue = (255, 0, 0) 
        self.color_green = (0, 255, 0) 
        self.color_read = (0, 0, 255) 
        self.color_orange = (0, 114, 255) 
       
        self.color_rectangle = self.color_blue
        self.color_text = self.color_orange #(33, 47, 252) #(255, 150, 0) # цвет text
        self.color_text_time = self.color_green
        self.thickness = 4 # размер символов в квадрате
        self.FONT_= cv2.FONT_HERSHEY_COMPLEX # фон
        self.lineType= 2
        
        self.frame_Th = frame_Th 
        self.teplo_Th = teplo_Th
        self.pin_Th = pin_Th
        
        
        
        self.id_person_temp = None
        self.id_person = None # переменная под персонал
        self.frame = None
        self.x_y_w_h = None
        self.frame_delay_if = True
        self.fase_RGB_200_200 = None

        self.x , self.y , self.w , self.h = 0, 0, 0, 0
        
        self.temp_tepl_Raw , self.t_teplovizor , self.tempPir , self.inputPir = 0, 0, 0, 1

        """
        self.frame = None #переменная под фрейм с камеры
        self.time = 0
        self.x , self.y , self.w , self.h = 0,0,0,0
        self.id_person = None # переменная под персонал
        """
        self.r_w = 0#w/(23) #w/23 / 21.5
        self.fontScale = 0
        
        self.next_()
    
    def next_(self):
    
        self.frame, self.x_y_w_h, self.frame_delay_if, self.id_person_temp, self.fase_RGB_200_200 = self.frame_Th.out()
        # = frame_Th.id_person
        #if self.id_person is None:
        #    if not self.fase_RGB_200_200 is None :
        self.id_person = self.id_person_temp
        
        self.x , self.y , self.w , self.h = self.x_y_w_h.get_()        
        self.temp_tepl_Raw, self.t_teplovizor, self.tempPir, self.inputPir = self.teplo_Th.teplo()
        self.r_w = self.w/200#w/(23) #w/23 / 21.5
        
        self.fontScale=self.r_w/2
    """    
    def set_(self, frame, time , x_y_w_h: x_y_w_h_object, id_person):
        self.frame = frame #переменная под фрейм с камеры
        self.time = time
        self.x , self.y , self.w , self.h = x_y_w_h.get_()
        self.id_person = id_person # переменная под персонал
        
        self.r_w = self.w/200#w/(23) #w/23 / 21.5
        
        self.fontScale=self.r_w/2
    """
    def out_rectangle(self):
        #print(self.x , self.w, self.y , self.h)
        if self.x + self.w+self.y + self.h >0: 
            cv2.rectangle(self.frame, (self.x, self.y), (self.x + self.w, self.y + self.h), self.color_rectangle, self.lineType)#вывод квадр
    
    def out_time(self, time): 
        q_h =self.y+60 #int(y+(h/2 + r_w*(10.5))) #y+h-10
        q_w =self.x+10 #int(x+(w/2 - r_w*(9.7)))
        if self.x + self.w+self.y + self.h >0: 
            cv2.putText(self.frame, "{}".format(int(time)), (q_w, q_h), cv2.FONT_HERSHEY_SIMPLEX, self.r_w, (0, 255, 0), self.thickness, cv2.LINE_AA)
    
    
               
    def out_name(self):  
        if self.x + self.w+self.y + self.h >0: 
            self.cv2_text_separator_putTex_rectangle(text=self.Str_ID(), x=self.x, y=self.y, lins_saze_text=20, fontScale=self.fontScale, direction=1, color_text = self.color_text, color_rectangle = self.color_rectangle)
        
    def out_text_if_teplo(self):  
        temp_text_Pir = self.teplo_Th.Str_teplo(2)# получаем текст на тепл
        if self.inputPir == 1:   
            self.cv2_text_separator_putTex_rectangle(text=temp_text_Pir, x=5, y=5, lins_saze_text=40, fontScale=0.99, direction=0, color_text = self.color_text, color_rectangle = self.color_rectangle)
    
    def out_text_end(self):
        '''
        выводим текст с писанием обработки
        возвращает: решениие можно ли пустить или нет
        '''
        
        x = 5
        y = self.frame_Th.height//2
        lins_saze_text=21
        fontScale=0.99
        
        if self.teplo_Th.if_valid() and self.teplo_Th.inputPir == 0:
            if not self.id_person is None:
                self.cv2_text_separator_putTex_rectangle(text="Всё хорошо, проходите", x=x, y=y, direction=0, lins_saze_text=lins_saze_text, fontScale=fontScale, color_text = self.color_text, color_rectangle = self.color_rectangle)
                return True
            else:    
                self.cv2_text_separator_putTex_rectangle(text=Str_ID(True), x=x, y=y, direction=0, lins_saze_text=lins_saze_text, fontScale=fontScale, color_text = self.color_text, color_rectangle = self.color_read )
        elif self.teplo_Th.inputPir == 1:
            self.cv2_text_separator_putTex_rectangle(text="Ошибка измерения. Рука не обнаружена.", x=x, y=y, direction=0, lins_saze_text=lins_saze_text, fontScale=fontScale, color_text = self.color_text, color_rectangle = self.color_read )
            #self.cv2_text_separator_putTex_rectangle(text="Рука не обнаружена", x=x, y=y, lins_saze_text=lins_saze_text, fontScale=fontScale, color_rectangle = self.color_read )
        elif not self.teplo_Th.if_valid():
            self.cv2_text_separator_putTex_rectangle(text="Температура не входит в границы нормы", x=x, y=y, direction=0, lins_saze_text=lins_saze_text, fontScale=fontScale, color_text = self.color_text, color_rectangle = self.color_read )
        else:
            self.cv2_text_separator_putTex_rectangle(text="Ошибка измерения.", x=x, y=y, direction=0, lins_saze_text=lins_saze_text, fontScale=fontScale, color_text = self.color_text, color_rectangle = self.color_read )
        return False
    
    def Str_ID(self, if_=False):# текст на  id
        
        if if_:
            temp_text =  "Не распознан"
            return temp_text
        #print("sddsdsd ")
        #print(self.id_person)
        if self.id_person is None or self.id_person == -1:
            temp_text =  "Не распознан"
        #elif self.id_person == -1:
        #    temp_text = "Подойдите ближе для распознования" #"" #
        else :
            temp_text = "Привет, {}".format(self.dataBase.get_people_name_by_person_id(self.id_person))
        #print(temp_text)
        return temp_text
        #  cv2_putTex_rectangle(frame, text, x, y , distance_lines, cv2_FONT=self.FONT_, fontScale, color_text, thickness,  color_font = self.color_rectangle, lineType): # вывод текста с фоном   
    def cv2_putTex_rectangle(self, text, x, y ,distance_lines, fontScale, color_rectangle, color_text): # вывод текста с фоном
        '''
        ф-я добавляет текст на изображение и фон к тексту
        text: текст
        x: начальное положение по x 
        y: начальное положение по y
        distance_lines: конец текста  
        fontScale: размер текста на выводе 
        color_rectangle: цвет фона
        color_text: цвет текста
        возвращает: расположение текста
        '''
        x1,y1 = x, y
        w1 = h1 =0
        if text !=" ":       
            [(text_width, text_height), baseline] = cv2.getTextSize(text, self.FONT_, fontScale, self.thickness)
            if text_width != 0 and text_height != 0:
                dist = int (distance_lines/2)
                cv2.rectangle(self.frame, (x-dist, y+dist), (x+text_width+dist, y-text_height-dist), color_rectangle, -1)
                cv2.putText(self.frame, text, (x, y), self.FONT_, fontScale, color_text, self.thickness, self.lineType)
                x1, y1, w1, h1 = x, y, text_width , text_height + distance_lines
        return x1, y1, w1, h1
    
        #def cv2_text_separator_putTex_rectangle(frame, text, x, y, cv2_FONT, fontScale, color_text, thickness,  color_font = self.color_rectangle, lineType, direction=0): # вывод текста с фоном с направлением 1- вверх, 0 - вниз
    def cv2_text_separator_putTex_rectangle(self , text, x, y, direction, lins_saze_text, fontScale, color_text ,  color_rectangle ): # вывод текста с фоном с направлением 1- вверх, 0 - вниз
        '''
        ф-я выводит текст с фоном с направлением вверх или  вниз
        text: текст
        text: текст
        x: начальное положение по x 
        y: начальное положение по y
        direction: направление 1 - вверх, 0 - вниз 
        lins_saze_text: макс длина строки
        fontScale: размер текста на выводе 
        color_text: цвет текста
        color_rectangle: цвет фона
        '''
        def text_separator(text, saze = 20):# делим строку над подстроки стараясь по размерм. (уберает 2е пробелы)
            '''
            ф-я разбивает текст на троки по размеру saze
            text: текст
            saze: мах размер
            возвращает: list со строками
            '''
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
        if text !=" " and text !="" and not text is None:
            #добавить возможность обработки нескольких строк
            list_text = text_separator(text, lins_saze_text) # делим строку над подстроки стараясь по размерм. (уберает 2е пробелы)   
            saze_list = len(list_text) 
            
            [(text_width, text_height), baseline] = cv2.getTextSize(list_text[0], self.FONT_, fontScale, self.thickness)
            
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
                x1,y1,w1,h1 = self.cv2_putTex_rectangle(text=_text, x=x1, y=y1+d*(h1), distance_lines=distance_lines, fontScale=fontScale, color_rectangle=color_rectangle, color_text=color_text ) # вывод текста с фоном
                i+=1
            
    
    
    def get_(self):   
        return self.frame  
    








# True False
If_Test_Foto = False # тест по фото
If_Test_print_reset = False # вывод состояний ресетов
For_bz = 0 # счёсик для кол-во перезапусков


font = cv2.FONT_HERSHEY_COMPLEX # фон
if not if_test_wimdovs:
    cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN) 
    cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
x = y = w = h = 0

if __name__ == "__main__":
    # без обнуления   
    time_out_all = 8 # таймер на цикл

    time_ = 0 # продолжительность скана лица
    Active = True # актив прогр
    color = (255, 255, 255) # цвет задника
    frame_time = 5 # время на распознование
    # с особым обнулением

    
    # с обнулением
    time_temp1 = time.time() #начало сканирования лица #для шага в программе


    if_save_time = False # ускорение вывода
    if_save = True # было ли сохранение (можно ли сохранить )

    if_null = True #  (можно ли обнулить)
    if_on = False # при выполнении проверки на всё
    
    
    
    # для получения с потоков
    frame = None #переменная под фрейм с камеры
    #x = y = w = h = 0
    x_y_w_h = x_y_w_h_object() #None #
    id_person = None # переменная под персонал
    frame_delay_if = True #отсутствие задержки 
    fase_RGB_200_200 = None # лицо
    
    
    t = time.time()
    
    frame_Th = frame_Thread(If_Test_Foto) #данные с камеры и часить обработки
    #frame_Th.frame_time_out = frame_time
    frame_Th.start()#старт камера
    
    teplo_Th = teplo_Thread() #данные с тепловизеров
    teplo_Th.start()#старт
    
    pin_Th = pin_Thread()#управление pin
    pin_Th.start()#старт
    
    cv2_out_ob = cv2_out_object(BD, frame_Th,teplo_Th,pin_Th)
    cv2_out_ob.next_()
    #Open_Th = Open_Thread() #управление действием при удачном прохождении
    #Open_Th.start()#старт
    
    #def zeroing():
    #    t = time.time()
    
    while(Active):
        
        if if_null:
            if_null = False
            t = time.time()

        #if not x_y_w_h is None :
        #    x_y_w_h.set_()
         

        
        frame_Th.next_()
        frame, x_y_w_h,  frame_delay_if, id_person,fase_RGB_200_200 = frame_Th.out()
        frame = frame_Th.frame_orientation(frame) 
        if not frame is None :
            teplo_Th.next_()
            cv2_out_ob.next_()
            #print(x_y_w_h.get_())
            if x_y_w_h.if_(frame_Th.min_w_h): # при наличии оица
                #print("wwwwwwwwwww")
                #print(time.time() - t)
                if time.time() - t < frame_time :
                    cv2_out_ob.out_rectangle()
                    cv2_out_ob.out_name()
                    cv2_out_ob.out_time(frame_time-(time.time() - t)+0.4)
                    cv2_out_ob.out_text_if_teplo()
                elif time.time() - t < time_out_all:
                    if_ = cv2_out_ob.out_text_end()
                elif time.time() - t < time_out_all+3:
                    None
                else:
                    frame_Th.zeroing()
                    if_null = True 
                    #print("!!!!!!")
                    None
                #if time.time() - t > time_out_all:
                #    frame_Th.zeroing() 
            else :if_null = True 
            
            #cv2.rectangle(self.frame, (x, y), (x + w, y + h), (255, 0, 0), 2)#вывод квадр
               

            #frame = cv2_out_ob.get_()
            if not frame is None :
                #frame = cv2.UMat(frame)
                cv2.imshow('window', frame)
        else :if_null = True 
        '''
        #pin_Th.pin_mig(pin_Th.pin_namber("red"), True)
        #GPIO.output(23 , GPIO.LOW if (time.time() - t >= 5) else GPIO.HIGH) # действие
        if time.time() - t >= 4:
                t = time.time()
                teplo_Th.next_()
                #print(teplo_Th.teplo())
                #pin_Th.pin_mig("blue", True)
                pin_Th.pin_on_time("red", 3)
                
        '''   

        #if cv2.waitKey(1) & 0xFF == ord('q'):
        if cv2.waitKey(33) & 0xFF == ord('q') :
            #Open_Th.Stop_()
            teplo_Th.Stop_()
            pin_Th.Stop_()
            frame_Th.Stop_()
            cv2.destroyAllWindows()
            Active = False
            #break
   