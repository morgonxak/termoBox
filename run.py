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
#import pyglet
#import pygame
#from pygame import mixer
#import vlc
import os
#import playsound
#import gi
from pydub import AudioSegment


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
    from app_thermometer import face_detector, processing_recognition, BD, dataBase, \
        on_buzer #,teplovizor, pirometr, valid, pin_red_pin, pin_green_pin  
    from app_thermometer import x_y_w_h_object, frame_Thread, pin_Thread, teplo_Thread, Open_Thread




class cv2_out_object():
    def __init__(self, dataBase:BD, frame_Th:frame_Thread, teplo_Th:teplo_Thread, pin_Th:pin_Thread):
        self.dataBase = dataBase
        self.color_blue = (255, 0, 0) 
        self.color_green = (0, 255, 0) 
        self.color_read = (0, 0, 255) 
        self.color_orange = (0, 114, 255) 
       
        self.color_rectangle = self.color_blue
        self.color_text = self.color_orange #(33, 47, 252) #(255, 150, 0) # цвет text
        self.color_text_time = self.color_green
        self.thickness = 4 # размер символов в квадрате
        self.FONT_ = cv2.FONT_HERSHEY_COMPLEX # фон
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
        self.r_w = 0 #w/(23) #w/23 / 21.5
        self.fontScale = 0
        
        self.next_()
    
    def next_(self):
        
        self.frame, self.x_y_w_h, self.frame_delay_if, self.id_person_temp, self.fase_RGB_200_200 = self.frame_Th.out()
        # = frame_Th.id_person
        #if self.id_person is None:
        #    if not self.fase_RGB_200_200 is None :
        self.id_person = self.id_person_temp
        
        self.x, self.y, self.w, self.h = self.x_y_w_h.get_() 
        self.temp_tepl_Raw, self.t_teplovizor, self.tempPir, self.inputPir = self.teplo_Th.teplo()
        self.r_w = self.w / 200 #w/(23) #w/23 / 21.5
        
        self.fontScale = self.r_w/ 2
    """    
    def set_(self, frame, time , x_y_w_h: x_y_w_h_object, id_person):
        self.frame = frame #переменная под фрейм с камеры
        self.time = time
        self.x , self.y , self.w , self.h = x_y_w_h.get_()
        self.id_person = id_person # переменная под персонал
        
        self.r_w = self.w/200#w/(23) #w/23 / 21.5
        
        self.fontScale=self.r_w/2
    """
    def out_rectangle(self, x:int=0, y:int=0, w:int=0, h:int=0):
        '''
        ф-я вывода на экран квадрата выделяюшего лицо 
        '''
        #print(self.x , self.w, self.y , self.h)
        if x + w + y + h == 0:
            x , w , y , h = self.x , self.w , self.y , self.h          
        if x + w + y + h > 0: 
            cv2.rectangle(self.frame, (self.x, self.y), (self.x + self.w, self.y + self.h), self.color_rectangle, self.lineType)#вывод квадр
            
    def out_rectangle_backdrop(self, rectangle_width:int=320, rectangle_height:int=320):
        '''
        ф-я вывода на экран квадрата по центру для вставки цица 
        '''
        #print(self.x , self.w, self.y , self.h)
        '''  
        rectangle_width = 320
        rectangle_height = 320
        '''
        rec_x = self.frame_Th.width//2 - rectangle_width//2 
        rec_y = self.frame_Th.height//2 - rectangle_height//2 
        
        #print(rec_x,rec_y, rectangle_width, rectangle_height )
        cv2.rectangle(self.frame, (rec_x, rec_y), (rec_x + rectangle_width, rec_y + rectangle_height), self.color_green, self.lineType)#вывод квадр
    
    def out_time(self, time:int = 0):
        '''
        ф-я вывода времени в квадрат
        ''' 
        q_h =self.y+60 #int(y+(h/2 + r_w*(10.5))) #y+h-10
        q_w =self.x+10 #int(x+(w/2 - r_w*(9.7)))
        if self.x + self.w+self.y + self.h >0: 
            cv2.putText(self.frame, "{}".format(int(time)), (q_w, q_h), cv2.FONT_HERSHEY_SIMPLEX, self.r_w, self.color_text_time, self.thickness, cv2.LINE_AA)

    def out_name(self): 
        '''
        ф-я вывода имени над квадратом
        '''
        if self.x + self.w+self.y + self.h >0: 
            Str_ = self.Str_ID()    
            self.cv2_text_separator_putTex_rectangle(text=Str_, x=self.x, y=self.y+self.w, lins_saze_text=20, 
                                                    fontScale=self.fontScale, direction=1, color_text = self.color_text, color_rectangle = self.color_rectangle, 
                                                    if_all_width_frame = False, Align = 0)
        
    def out_text_if_teplo(self):  
        '''
        ф-я вывода строчки информации о нижнет теплеке
        '''
        '''
        temp_text_Pir = self.teplo_Th.Str_teplo(2)# получаем текст на тепл
        #if self.inputPir == 1:   
        
        self.cv2_text_separator_putTex_rectangle(text=temp_text_Pir, x=5, y=5, lins_saze_text=40, fontScale=0.99, direction=0, 
                                                    color_text = self.color_text, color_rectangle = self.color_rectangle, 
                                                    if_all_width_frame = True, Align = 1)
        '''
        if self.inputPir == 1:   
            cv2.rectangle(self.frame, (100, 50), (381, 5), self.color_rectangle, -1)
            cv2.putText(self.frame, "Поднесите руку", (100, 39), self.FONT_, 0.99, self.color_text, self.thickness, self.lineType)
        
        #    return 1  
        return self.inputPir == 1                                        
    
    def out_text_end(self):
        if self.teplo_Th.if_valid() and self.teplo_Th.inputPir == 0:
            cv2.rectangle(self.frame, (30, 365), (450, 320), self.color_green, -1)
            cv2.putText(self.frame, "Все хорошо, проходите", (30, 354), self.FONT_, 0.99, self.color_text, self.thickness, self.lineType)

            return True
        else:
            cv2.rectangle(self.frame, (66, 365), (415, 320), self.color_read, -1)
            cv2.rectangle(self.frame, (54, 411), (426, 366), self.color_read, -1)
            cv2.putText(self.frame, "Ошибка измерения.", (66, 354), self.FONT_, 0.99, self.color_text, self.thickness, self.lineType)
            cv2.putText(self.frame, "Рука не обнаружена.", (54, 400), self.FONT_, 0.99, self.color_text, self.thickness, self.lineType)

            return False
            
    def out_text_end1(self):
        '''
        выводим текст с писанием обработки
        возвращает: решениие можно ли пустить или нет
        '''
        
        x = 5
        y = self.frame_Th.height//2
        lins_saze_text=21
        fontScale=0.99
        
        if self.teplo_Th.if_valid() and self.teplo_Th.inputPir == 0:
            
            if_ = not self.id_person is None#:
            """
                self.cv2_text_separator_putTex_rectangle(text="Все хорошо, проходите", x=x, y=y, direction=0, lins_saze_text=lins_saze_text, 
                                                        fontScale=fontScale, color_text = self.color_text, color_rectangle = self.color_green, 
                                                        if_all_width_frame = True, Align = 1)
            else: 
            """
            Str_ = "Все хорошо, проходите" #self.Str_ID()
            self.cv2_text_separator_putTex_rectangle(text=Str_, x=x, y=y, direction=0, lins_saze_text=lins_saze_text, fontScale=fontScale, 
                                                    color_text = self.color_text, color_rectangle = self.color_green, if_all_width_frame = True, 
                                                    Align = 1 ) #  if if_ else self.color_read
            return True #True                                        
        elif self.teplo_Th.inputPir == 1:
            self.cv2_text_separator_putTex_rectangle(text="Ошибка измерения. Рука не обнаружена.", x=x, y=y, direction=0, lins_saze_text=lins_saze_text, 
                                                    fontScale=fontScale, color_text = self.color_text, color_rectangle = self.color_read, 
                                                    if_all_width_frame = True, Align = 1)
            #self.cv2_text_separator_putTex_rectangle(text="Рука не обнаружена", x=x, y=y, lins_saze_text=lins_saze_text, fontScale=fontScale, color_rectangle = self.color_read )
        elif not self.teplo_Th.if_valid():
            self.cv2_text_separator_putTex_rectangle(text="Температура превышена. Ожидайте сотрудника службы охраны.", x=x, y=y, direction=0, lins_saze_text=lins_saze_text, 
                                                    fontScale=fontScale, color_text = self.color_text, color_rectangle = self.color_read, 
                                                    if_all_width_frame = True, Align = 1 )
        else:
            self.cv2_text_separator_putTex_rectangle(text="Ошибка измерения.", x=x, y=y, direction=0, lins_saze_text=lins_saze_text, fontScale=fontScale, 
                                                    color_text = self.color_text, color_rectangle = self.color_read, if_all_width_frame = True, Align = 1 )
        return False
    
    def Str_ID(self, if_:bool=False):# текст на  id
        
        if if_:
            temp_text = "Не распознан"# "Здравствуйте Сотрудник ИЦ"
            return temp_text
        #print("sddsdsd ")
        #print(self.id_person)
        if self.id_person is None or self.id_person == -1:
            temp_text =  "Не распознан"
            #temp_text =  "Здравствуйте Сотрудник ИЦ"
        #elif self.id_person == -1:
        #    temp_text = "Подойдите ближе для распознования" #"" #
        else :
            #print(self.id_person)
            temp_text = "Привет, {}".format(self.dataBase.get_people_name_by_person_id(self.id_person))
            #temp_text = "Привет, "
        #print(temp_text)
        return temp_text
        #  cv2_putTex_rectangle(frame, text, x, y , distance_lines, cv2_FONT=self.FONT_, fontScale, color_text, thickness,  color_font = self.color_rectangle, lineType): # вывод текста с фоном   
    def cv2_putTex_rectangle(self, text, x:int, y:int  ,fontScale, color_rectangle, color_text, if_all_width_frame:bool, Align:int): # вывод текста с фоном
        '''                                 ,distance_lines
        ф-я добавляет текст на изображение и фон к тексту
        text: текст
        x: начальное положение по x 
        y: начальное положение по y
        #distance_lines: конец текста  
        fontScale: размер текста на выводе 
        color_rectangle: цвет фона
        color_text: цвет текста
        if_all_width_frame: растянуть фон текста на весь экран
        Align:выравнивание текста 0 - с лева, 1 - центр 
        возвращает: расположение текста 
        '''
        x1,y1 = x, y
        w1 = h1 =0
        if text !=" ":       
            [(text_width, text_height), baseline] = cv2.getTextSize(text, self.FONT_, fontScale, self.thickness)
            
            
            #distance_lines = text_height
            #(frame_Th.width//2 - dist) 
            if text_width != 0 and text_height != 0:
                #dist = int (text_height//2) #distance_lines
                dist =0
                #cv2.rectangle(self.frame, (x, y+baseline), (x+text_width, y-(text_height+baseline)), color_rectangle, -1)
                #cv2.putText(self.frame, text, (x, y), self.FONT_, fontScale, color_text, self.thickness, self.lineType) 
                
                if  if_all_width_frame:
                    cv2.rectangle(self.frame, (0, y+baseline), (self.frame_Th.width, y - (text_height+baseline)), color_rectangle, -1)
                    
                    
                if Align == 1:
                    x = self.frame_Th.width//2 - text_width//2   
                    
                if not if_all_width_frame:
                    cv2.rectangle(self.frame, (x, y+baseline), (x+text_width, y-(text_height+baseline)), color_rectangle, -1)
                    
                cv2.putText(self.frame, text, (x, y), self.FONT_, fontScale, color_text, self.thickness, self.lineType)
                    #None
                #else:
                    #if not if_all_width_frame:
                    #    cv2.rectangle(self.frame, (x-dist, y+dist), (x+text_width+dist, y-text_height-dist), color_rectangle, -1)
                    #cv2.putText(self.frame, text, (x, y), self.FONT_, fontScale, color_text, self.thickness, self.lineType)
                #print(text, " ", x, y)
                #print( " ", x, y+baseline,x+text_width, y-(text_height+baseline))
                x1, y1, w1, h1 = x, y, text_width , text_height  #+ text_height# distance_lines 
                
                #print(x, y, text_width, text_height, baseline)
                #print(x1, y1, w1, h1)
                #print( cv2.getTextSize(text, self.FONT_, fontScale, self.thickness))
        return x1, y1, w1, h1 # x, y, ширена, длина - текст
    
        #def cv2_text_separator_putTex_rectangle(frame, text, x, y, cv2_FONT, fontScale, color_text, thickness,  color_font = self.color_rectangle, lineType, direction=0): # вывод текста с фоном с направлением 1- вверх, 0 - вниз
    def cv2_text_separator_putTex_rectangle(self , text, x:int, y:int, direction:int, lins_saze_text:int, fontScale, color_text ,  color_rectangle , if_all_width_frame:bool, Align:int): # вывод текста с фоном с направлением
        '''
        ф-я выводит текст с фоном с направлением вверх или  вниз
        text: текст
        text: текст
        x: начальное положение по x 
        y: начальное положение по y
        direction: направление 1 - вверх, 0 - вниз 
        lins_saze_text: макс длина строки (кол-во букв) (20 стандартно)
        fontScale: размер текста на выводе 
        color_text: цвет текста
        color_rectangle: цвет фона
        if_all_width_frame: растянуть фон текста на весь экран
        Align:выравнивание текста 0 - с лева, 1 - центр 
        '''
        def text_separator(text, saze:int = 20):# делим строку над подстроки стараясь по размерм. (уберает 2е пробелы)
            '''
            ф-я разбивает текст на троки по размеру saze
            text: текст
            saze: мах размер
            возвращает: list1 со строками
            '''
            list1 = []
            if len(text) <= saze:
                list1.append(text.strip())  
            else:
                text_temp = ""
                text_temp_end = 0
                saze_temp = 0
                for w in text.split(): #пройтись по каждому слову
                    if text_temp != "" and saze_temp + len(w) > saze:
                        list1.append(text_temp.strip())     
                        text_temp = ""
                        saze_temp = 0
                        text_temp_end = 0
                        
                    if text_temp == "" and len(w) > saze:
                        list1.append(w.strip()) 
                        text_temp_end = 0
                        text_temp = ""
                        saze_temp = 0 
                    else:
                        if saze_temp + len(w)  <= saze:
                            saze_temp += len(w) 
                            text_temp += w
                            text_temp_end = 1 
                        else:    
                            list1.append(text_temp.strip()) 
                            text_temp_end = 0
                            saze_temp = len(w)
                            text_temp = w 
                            text_temp_end = 1
                        if saze_temp != 0 and saze_temp <= saze - 1:
                            saze_temp += 1
                            text_temp += " "
                if text_temp_end == 1 :
                    list1.append(text_temp.strip())
            return list1
            
        if text !=" " and text !="" and not text is None:
            #добавить возможность обработки нескольких строк
            list_text = text_separator(text, lins_saze_text) # делим строку над подстроки стараясь по размерм. (уберает 2е пробелы)   
            #saze_list = len(list_text) 
            
            [(text_width, text_height), baseline] = cv2.getTextSize(list_text[0], self.FONT_, fontScale, self.thickness)
            dist = int (text_height)
            d=0
            x1=y1=w1=h1=0
            x1 = x
            #distance_lines = text_height
            if direction == 1: #вверх 
                d=-1 
                y1 = y +baseline#-text_height #*(saze_list) 
            elif direction == 0:  # вниз
                y1 = y # + text_height *2 #distance_lines
                d=1
            y1 = y + (baseline)  
            #print( d)
            
            i=0
            
            if direction == 0:
                list_ = list_text
            elif direction == 1:  # вниз
                list_ = reversed(list_text)
            #for i, _text in enumerate(list_text)
            for _text in list_: #пройтись по каждому слову ####################distance_lines=distance_lines,
                x1,y1,w1,h1 = self.cv2_putTex_rectangle(text=_text, x=x1, y=y1+d*((h1+dist)*1),  fontScale=fontScale, color_rectangle=color_rectangle, 
                                                        color_text=color_text , if_all_width_frame = if_all_width_frame, Align = Align) # вывод текста с фоном
                i+=1
            
    
    
    def get_(self):   
        return self.frame  
    


 

class save_numpy_bd_object():
    def __init__(self, dataBase:BD,  teplo_Th:teplo_Thread):
        self.dataBase = dataBase
        self.teplo_Th = teplo_Th 
        self.time_save_bd = 5 * 60 # время на отправку в бд
        self.t_save_bd = 0 # time.time() # счёчик времени на отправку в бд
        
        self.t = time.time() #время 1го прохода
        self.time = 30 # 2 #миним время 1го прохода
        
        self.list_len = 35 #
        self.list_save_Raw = [33] # для мах теплика
        self.list_save_Pir = [33] # для пирометра
        self.IfOutPrint = True
    def ___add___(self): 
        
        
        Raw, t_teplovizor, Pir, inputPir = self.teplo_Th.teplo()
        
        
        #if inputPir == 1: # /0 - есть рука / 1 - нет руки
        self.dataBase.pull_log_background(self.teplo_Th.temp_tepl_arr, [Pir]) # 
    
        #print(Raw, Pir)
        if len(self.list_save_Raw) >= self.list_len:
            self.list_save_Raw.pop(0)
        if len(self.list_save_Pir) >= self.list_len:
            self.list_save_Pir.pop(0)
        self.list_save_Raw.append(Raw)
        self.list_save_Pir.append(Pir)
        #print(self.list_save_Raw[-1], self.list_save_Pir[-1])
        #print("_________")
        if self.IfOutPrint:
            self.IfOutPrint = False
            print("save_numpy_bd_object rewritten")
        
        
    def ___avg___(self, list_): 
        return sum(list_) / len(list_)
        
    def out_last(self):
        return self.list_save_Raw[-1], self.list_save_Pir[-1]
        
    def save(self):
    
        if time.time() - self.t >= self.time:
            self.t = time.time()
            
            list_save_Raw, list_save_Pir = self.out_last()
            self.teplo_Th.next_(list_save_Raw, list_save_Pir )
            self.___add___()
            
            
            if time.time() - self.t_save_bd >= self.time_save_bd and ( len(self.list_save_Raw) >= self.list_len and len(self.list_save_Pir) >= self.list_len ):
                self.t_save_bd = time.time() 
                #self.dataBase.pull_calibration_threshold(self.___avg___(self.list_save_Raw),self.___avg___(self.list_save_Pir) )
                
                
            teplo_Th.zeroing()    
        
   




# True False
If_Test_Foto = False # тест по фото
If_Test_print_reset = False # вывод состояний ресетов
For_bz = 0 # счёсик для кол-во перезапусков


font = cv2.FONT_HERSHEY_COMPLEX # фон
if not if_test_wimdovs:
    cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN) 
    cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
x = y = w = h = 0



import threading
from threading import Thread
if __name__ == "__main__":
    # без обнуления   
    time_out_all = 6 # таймер на цикл

    frame_time = 3 # время на распознование
    time_ = 0 # продолжительность скана лица
    Active = True # актив прогр
    color = (255, 255, 255) # цвет задника
    rectangle_width = 320 #фоновый квадрат для лица (width)
    rectangle_height = 320 #фоновый квадрат для лица (height)
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
    
    teplo_Th = teplo_Thread(dataBase) #данные с тепловизеров
    teplo_Th.start()#старт
    
    pin_Th = pin_Thread()#управление pin
    pin_Th.start()#старт
    
    cv2_out_ob = cv2_out_object(dataBase, frame_Th, teplo_Th, pin_Th)
    
    save_numpy_bd_ob = save_numpy_bd_object(dataBase, teplo_Th)
    #"file://"+
    STR_song_True = os.path.abspath(os.path.join(os.getcwd(), "./True.mp3"))
    STR_song_False = os.path.abspath(os.path.join(os.getcwd(), "./False.mp3"))
    print(STR_song_True)
    print(STR_song_False)
    
    
    song_True = AudioSegment.from_mp3(STR_song_True)
    song_False = AudioSegment.from_mp3(STR_song_False)

    #song_True = vlc.MediaPlayer(STR_song_True)
    #song_False = vlc.MediaPlayer(STR_song_False)

    
    
    #mixer.init()
    ##mixer.music.load("play.mp3")    
    #song_True = mixer.music.load("True.mp3")
    #song_False = mixer.music.load("False.mp3")
    
    #pygame.init()
    #song_True = pygame.mixer.Sound('True.mp3') #pygame.mixer.Sound('./True.mp3')
    ##os.path.abspath(os.path.join(os.getcwd(), './True.mp3')))
    #song_False =pygame.mixer.Sound('False.mp3') #pygame.mixer.Sound('./False.mp3')
    ##os.path.abspath(os.path.join(os.getcwd(), './False.mp3'))) #pygame.mixer.Sound('./False.mp3')
    ##song_ = None
    
    #cv2_out_ob.next_()
    
    #Open_Th = Open_Thread() #управление действием при удачном прохождении
    #Open_Th.start()#старт
    
    #def zeroing():
    #  
    if_pyglet = True
    if_save_bd = True
    frame_Th.next_()
    
    #th = Thread(target=sleepMe, args=(i, ), daemon = True)
    #th.start()

    while(Active):
        
        if if_null:
            if_null = False
            t = time.time()

        #if not x_y_w_h is None :
        #    x_y_w_h.set_()
         

        
        #frame_Th.next_()
        frame, x_y_w_h,  frame_delay_if, id_person, fase_RGB_200_200 = frame_Th.out()
        #frame = frame_Th.frame_orientation(frame) 
        
        cv2_out_ob.next_()    
        #if  not frame is None and x_y_w_h.if_(frame_Th.min_w_h): # при наличии оица
        if  not frame is None and x_y_w_h.if_(frame_Th.min_w_h):# and not frame_Th.frame_if: # при наличии оица
            #cv2_out_ob.next_()
            #print(x_y_w_h.get_())
            #print("wwwwwwwwwww")
            #print(time.time() - t)
            time_if = time.time() - t
            #print(time_if)
            if time_if < frame_time :
                if_save_bd = True
                #list_save_Raw, list_save_Pir = save_numpy_bd_ob.out_last()
                
                #print(list_save_Raw, list_save_Pir)
                #teplo_Th.next_(list_save_Raw, list_save_Pir )
                teplo_Th.next_(save_numpy_bd_ob.out_last() )
                
                #print(teplo_Th.teplo())
                
                
                th1 = Thread(target=cv2_out_ob.out_name, args=())
                #cv2_out_time = frame_time-(time_if)
                #th2 = Thread(target=cv2_out_ob.out_time, args=(cv2_out_time))
                
                th3 = Thread(target=cv2_out_ob.out_text_if_teplo, args=())
                
                
                th1.start()
                #th2.start()
                th3.start()
                
                
                cv2_out_ob.out_rectangle_backdrop(rectangle_width,rectangle_height)
                cv2_out_ob.out_rectangle()
                cv2_out_ob.out_time(frame_time-(time_if)+0.4)
                
                
                th1.join()
                #th2.join()
                th3.join()
                '''
                cv2_out_ob.out_name()
                cv2_out_ob.out_time(frame_time-(time_if)+0.4)
                cv2_out_ob.out_text_if_teplo()
                #leg = ( cv2_out_ob.out_text_if_teplo())
                '''
                leg = (cv2_out_ob.inputPir == 1)
                if leg == 0:
                    pin_Th.pin_mig("blue", True)#
                    t = time.time()-(frame_time+0.1)
                else:
                    pin_Th.pin_mig("red", True)
                
            elif time_if < time_out_all:
                #print(time_if)
                #print(time_out_all)
                #print(time_if < time_out_all)
                #print("OOOOOOO")
                
                if cv2_out_ob.out_text_end():
                    pin_Th.pin_on_off("green", True)
                    if if_pyglet:
                        #song_ = song_True
                        if_pyglet = False
                        #song_True.play()
                        #playsound.playsound(STR_song_True, True)
                        song_True.export("final.wav", format="wav")
                else:
                    pin_Th.pin_on_off("red", True)
                    if if_pyglet:
                        #song_ = song_False
                        if_pyglet = False
                        #playsound.playsound(STR_song_False, True)
                        song_False.export("final.wav", format="wav")
                        #song_False.play()
                #if if_pyglet:
                #    if_pyglet = False
                #    song_.play()  
                pin_Th.pin_on_time("door", 3)
                if if_save_bd:
                    if_save_bd = False
                    #dataBase.pull_log(fase_RGB_200_200, teplo_Th.if_valid(), id_person)   
                    #dataBase.pull_temperature(teplo_Th.temp_tepl_arr, [teplo_Th.tempPir], teplo_Th.inputPir,  frame_delay_if)
                    dataBase.pull_log(fase_RGB_200_200, teplo_Th.if_valid(), id_person)   
                    dataBase.pull_temperature(teplo_Th.temp_tepl_arr, [teplo_Th.tempPir], teplo_Th.inputPir,  frame_delay_if)
                    #print("dataBase.pull_log")
                    #print(dataBase.get_agv_10_calibration_threshold())
            elif time_if < time_out_all+1:
                pin_Th.pin_all(False)
                
                teplo_Th.next_(save_numpy_bd_ob.out_last() )
                None
            else:
                
                frame_Th.zeroing()
                teplo_Th.zeroing()
                pin_Th.pin_all(False)
                #t = time.time()
                if_null = True 
                #print("!!!!!!")
                None

        else:
            #cv2_out_ob.next_()
            cv2_out_ob.out_rectangle_backdrop(rectangle_width,rectangle_height)
            save_numpy_bd_ob.save() # обсчёт и сейв окружающей
        

           

        #frame = cv2_out_ob.get_()
        #if not frame is None :
        if not frame is None :#and not frame_Th.frame_if :
            #frame = cv2.UMat(frame)

            cv2.imshow('window', frame)
            #cv2.imshow('window', frame)
        frame_Th.next_()
        
        """
        #pin_Th.pin_mig(pin_Th.pin_namber("red"), True)
        #GPIO.output(23 , GPIO.LOW if (time.time() - t >= 5) else GPIO.HIGH) # действие
        
        if time.time() - t >= 4:
            t = time.time()
            print(time.time() - t )
            #teplo_Th.next_()
            #print(teplo_Th.teplo())
            #pin_Th.pin_mig("blue", True)
            #pin_Th.pin_on_off("blue", True)
            pin_Th.pin_on_time("red", 3)
               
        """   

        #if cv2.waitKey(1) & 0xFF == ord('q'):
        if cv2.waitKey(33) & 0xFF == ord('q') :
            #Open_Th.Stop_()
            if teplo_Th.if_active:
                teplo_Th.Stop_()
            pin_Th.Stop_()
            if frame_Th.if_active:
                frame_Th.Stop_()
            #pyglet.app.run()
            #pygame.quit()
            cv2.destroyAllWindows()
            Active = False
            
            #break
   