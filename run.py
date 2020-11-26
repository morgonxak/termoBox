#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 13:10:45 2020

@author: admin
"""



import cv2
import time
#import threading
import numpy 
import logging ## лог
import os

logging.basicConfig(filename="sample.log", level=logging.INFO)

#from multiprocessing.pool import ThreadPool
from multiprocessing import Process , Queue #,Pool 
#import tkinter as tk
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
    from app_thermometer import face_detector, processing_recognition, dataBase, pirometr #, led_red_pin,  teplovizor,led_green_pin, on_buzer, valid

    from app_thermometer import x_y_w_h_object, frame_Thread, pin_Thread, teplo_Thread, Open_Thread , Song, Song_start


    

def faces_x_y(frame): # ф-я для поиска границ
    x = y = w = h = 0
    x1 = y1 = w1 = h1 = 0
    if not frame is None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
        for (x1 , y1 , w1 , h1) in faces:
            x , y , w , h = x1 , y1 , w1 , h1 
            break
            
    return x , y , w , h

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
    if frame is None:
        return  0, 0
    if height + width == 0:
        height = numpy.size(frame, 0)
        width = numpy.size(frame, 1)
    return height, width

def frame_image(cap): # или скрин или фото от If_Test_Foto

   
    ret , frame = cap.read()    
     
    if not frame is None:
        frame = cv2.flip(frame,1) # ореентация камеры
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE) 
        #frame = frame[:, 185:455]
    else: 
        logging.info("except: frame is None") 
        print("except: frame is None")                             
        #raise Exception("frame is None")
    return frame 
    
         
# True False
If_Test_print_reset = False # вывод состояний ресетов
For_bz = 0 # счёсик для кол-во перезапусков



if not if_test_wimdovs:
    cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN) 
    cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    


x = y = w = h = 0
x1 = y1 = w1 = h1 = 0


def out_rectangle_backdrop(frame, height, width, rectangle_width:int=320, rectangle_height:int=320):
    '''
    ф-я вывода на экран квадрата по центру для вставки цица 
    '''

    '''  
    rectangle_width = 320
    rectangle_height = 320
    '''
    rec_x = width//2 - rectangle_width//2 
    rec_y = height//2 - rectangle_height//2 
    color_green = (0, 255, 0) 
    lineType= 2
    #print(rec_x,rec_y, rectangle_width, rectangle_height )
    cv2.rectangle(frame, (rec_x, rec_y), (rec_x + rectangle_width, rec_y + rectangle_height), color_green, lineType)#вывод квадр

def out_text_end(frame, if_:bool):
    color_green = (0, 255, 0)
    color_read = (0, 0, 255)
    thickness = 4     
    lineType = 2
    FONT_ = cv2.FONT_HERSHEY_COMPLEX 
    color_orange = (0, 114, 255) 
    if if_:
        cv2.rectangle(frame, (30, 365), (450, 320), color_green, -1)
        cv2.putText(frame, "Все хорошо, проходите", (30, 354), FONT_, 0.99, color_orange, thickness, lineType)

        return True
    else:
        cv2.rectangle(frame, (66, 365), (415, 320), color_read, -1)
        cv2.rectangle(frame, (54, 411), (426, 366), color_read, -1)
        cv2.putText(frame, "Ошибка измерения.", (66, 354), FONT_, 0.99, color_orange, thickness, lineType)
        cv2.putText(frame, "Рука не обнаружена.", (54, 400), FONT_, 0.99, color_orange, thickness, lineType)

        return False

        
def if_input_Raw(input_Raw):
    return (4<=input_Raw<=10) or input_Raw == 0

def if_pir(input_Raw, Pir, Pir_ambient):
    return True
    
cap = None
cap = cv2.VideoCapture(0) # подкл к камере      

if __name__ == "__main__":
    print("qq 0")
    
    STR_song_True = os.path.abspath(os.path.join(os.getcwd(), "./True.wav")) # mp3
    STR_song_False = os.path.abspath(os.path.join(os.getcwd(), "./False.wav"))
    #print(STR_song_True)
    #print(STR_song_False)
    song_True = Song(STR_song_True)
    song_False = Song(STR_song_False)
    song_True.start()
    song_False.start()
    pin_Th = pin_Thread()#управление pin
    pin_Th.start()#старт

    '''
    cap.set(cv2.CAP_PROP_FPS, 24) # Частота кадров
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600) # Ширина кадров в видеопотоке.
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # Высота кадров в видеопотоке.
    '''
    
    font = cv2.FONT_HERSHEY_COMPLEX # фон


    frame = None #переменная под фрейм с камеры
    ret = False # фрейм прочитан корректно?
    frame = frame_image( cap)# или скрин или фото


    height, width = cv2_height_width(frame )# размер скрина
    min_w, min_h = cv2_rectangle_min_W_H(height ,width)

    
    # без обнуления
    #return_Id_to_face = Queue() #очередь для сняти инфы с потока     
    time_out = 3 # таймер на определение человека

    time_out_all = time_out + int(max(song_True.len_(), song_False.len_(), 2) )+ 1

    flag_disease = False  # на решение по темпер


    Active = True # актив прогр

    fase_RGB_200_200 = None  # под скрин лица



    # с обнулением
    t = time.time() #начало сканирования лица #для шага в программе
    
    #flag_id_on = False # найден ли id
    #return_Id_to_face.put(-1) # для сняия с потока инф(чтоб без матов(часть костыля #1))
    if_save = True # было ли сохранение (можно ли сохранить )
   
    if_null = True #  (можно ли обнулить)
    if_on_fase = False # найден ли id



    #pirometr = pirometr()
    if_pyglet = True   
    lineType = 2
    color_blue = (255, 0, 0)
    thickness = 4    
    color_green = (0, 255, 0)

    print("Программа активирована.") 
    while(Active):
    
          
  
        #frame_KOSTIL_if = True 
        if if_null: # обнуление
            #print("if_null")

            pin_Th.pin_all(False) 
    
            #logging.info("Reset {}".format( time.time()))
            #led_all_off() # выкл свет  time_out = time_out_const # таймер на определение человека
            t = time.time() #начало сканирования лица
            
            #flag_id_on = False # найден ли id
            #return_Id_to_face.put(-1) # для сняия с потока инф (чтоб без матов(часть костыля #1))
            if_save = True # было ли сохранение (можно ли сохранить )
            ret = False # фрейм прочитан корректно?
            if_null = False #  (можно ли обнулить)
            if_pyglet = True
            
            x = y = w = h = 0
            x1 = y1 = w1 = h1 = 0
            fase_RGB_200_200 = None  # под скрин лица       
                    
                    
                    
                    
        #try:
        
        
        
    
        input_Raw, Pir, Pir_ambient = pirometr.get_() # получаем тепло 
        time_if = time.time() - t 
        frame = frame_image(cap) # или скрин или фото
        x1, y1, w1, h1  = faces_x_y(frame)
        if x1 + y1 + w1 + h1 != 0 and (min_w <=w1 or min_h <=h1 ) :
            x, y, w, h = x1, y1, w1, h1
            
        if x + y + w + h != 0 and (min_w <=w or min_h <=h ):
        
            if x1 + y1 + w1 + h1 != 0 and (min_w <=w1 or min_h <=h1 ) :
                fase_RGB_200_200 = numpy.copy((frame)[y:y + w, x:x + h])         
                time_if = time.time() - t
                
            if  time_if < time_out :  # flag_id_on
                out_rectangle_backdrop(frame, height, width)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color_blue, lineType)#вывод квадр

                cv2.putText(frame, "{}".format(int(time_out-(time_if)+0.4)), (x+10, y+60), cv2.FONT_HERSHEY_SIMPLEX, w / 200, color_green, thickness, cv2.LINE_AA)
                    
                
                leg = if_input_Raw(input_Raw) # (if_pir(input_Raw, Pir, Pir_ambient))
                if leg:
                    #pin_Th.pin_mig("blue", True)#
                    pin_Th.pin_all(False)     
                    t = time.time()-(time_out+0.1)
                else:
                    pin_Th.pin_mig("red", True)
                    
                
                #print("leg {}".format( leg ))
                #print("input_Raw {}".format( input_Raw ))
            elif time_if < time_out_all:    
                
                leg = if_input_Raw(input_Raw) 
                #print("leg 2 {}".format( leg ))
                if leg :
                    leg1 = out_text_end(frame, (if_pir(input_Raw, Pir, Pir_ambient) and if_input_Raw(input_Raw)) )
                    print("leg1 {}".format( leg1 ))
                    pin_Th.pin_on_off("green" if leg1 else "red", True)
                    """
                    if leg1:
                        pin_Th.pin_on_off("green", True)
                    else:
                        pin_Th.pin_on_off("red", True)
                    """
                    if if_pyglet :
                        (song_True if leg1 else song_False).restart()
                        if_pyglet = False
                        
                    pin_Th.pin_on_time("door", 3)
                    if if_save:
                        if_save = False
                        dataBase.save_frame_image(fase_RGB_200_200)
                        dataBase.pull_log_Pir(Pir, Pir_ambient, input_Raw)  
                
            elif time_if < time_out_all+1 :
                pin_Th.pin_all(False)     
            else: 
                out_rectangle_backdrop(frame, height, width)

                if_null = True #and frame_KOSTIL_if
                if If_Test_print_reset:print("reset  < 0.1")  
        else: 
            out_rectangle_backdrop(frame, height, width)
            if_null = True #and (frame_KOSTIL_if )
            
            
            
        if not frame is None:
            cv2.imshow('window', frame)
        
        """
        except: 
            
            if_null = True # and frame_KOSTIL_if
            if If_Test_print_reset:print("reset except")    
            logging.info("except: all except {}".format( time.time()))
            print("except: all except {}".format( time.time()))
        """ 

        if cv2.waitKey(1) & 0xFF == ord('q'):
            if not id_hread is None:
                if id_hread.is_alive():
                    #id_hread.join()
                    id_hread.terminate()
                id_hread.close()
            cv2.destroyAllWindows()
            #led_all_off() # выкл свет
            pin_Th.pin_all(False) 
            Active = False
            #break
    
    cap.release()

