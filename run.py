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

from multiprocessing.pool import ThreadPool
from multiprocessing import Pool, Process , Queue
if_test_wimdovs = True
if if_test_wimdovs:
    face_detector = cv2.CascadeClassifier(r'C:\Users\Admin\Desktop\python\haarcascade_frontalface_default.xml')
    led_red_pin = 23
    led_green_pin = 24
else:
    import RPi.GPIO as GPIO
    from app_thermometer import face_detector, processing_recognition, teplovizor, dataBase, pirometr, valid, led_red_pin, led_green_pin, on_buzer


def Id_to_face(fase_RGB_200_200, return_Id_to_face):
    id_person = -1
    if if_test_wimdovs:
        id_person = processing_recognition.predict_freme(fase_RGB_200_200)
    #if return_Id_to_face.get() == -1 :
    return_Id_to_face.put(id_person)

#if __name__ != '__main__': # ????????????? 

def led_off(led_pin,on = False): # выкл свет  
    if on == True:
        if if_test_wimdovs:
            GPIO.output(led_pin, GPIO.HIGH) # выкл
            #print("{} GPIO.HIGH".format(led_pin))
        else:
            print("{} GPIO.HIGH".format(led_pin))
    else:
        if if_test_wimdovs:
            GPIO.output(led_pin, GPIO.LOW) # выкл
            #print("{} GPIO.HIGH".format(led_pin))
        else:
            print("{} GPIO.LOW".format(led_pin))
        
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


def Str_ID(id_person):# текст на  id
    if id_person == None:
        temp_text =  "Не распознан"
        temp_text2 = " "
        led_all_mig()
        
        #led_red_mig()
    elif id_person == -1:
        temp_text = "Подойдите ближе" #"" #
        temp_text2 = " для распознования"
        #GPIO.output(led_red_pin, GPIO.HIGH)
        
    else :
        temp_text = "Привет, {}".format(dataBase.get_people_name_by_person_id(id_person))
        temp_text2 =  " "
        #GPIO.output(led_green_pin, GPIO.HIGH)
        led_green_mig()
    return temp_text, temp_text2


def valid(tempPir, t_teplovizor):
    '''
    Решения о состоянии здоровья
    :param tempPir:
    :param t_teplovizor:
    :return: текст сообщения
    '''
    
    #print("valid")
    if t_teplovizor == 0 or tempPir == 0:
        return False, 'Нет всей информации по температуре. '    
    
    tepl = round(numpy.max([t_teplovizor, tempPir]), 1)
    if tepl >= 37.2:
        led_red_mig(3)
        return True, 'Обратитесь к врачу: {}'.format(tepl)
    else:
        return False, 'Все хорошо, проходите: {}'.format(t_teplovizor)
    
    """
    if t_teplovizor >= 37.2 or tempPir >= 37.2:
        #GPIO.output(led_red_pin, GPIO.LOW)# вкл
        led_red_mig(3)
        if tempPir <= 0:
            return True, 'Обратитесь к врачу: {}'.format(t_teplovizor)
        else:
            return True, 'Обратитесь к врачу: {}: '.format(round(numpy.max([t_teplovizor, tempPir]), 1))
    else:
        #GPIO.output(led_green_pin, GPIO.LOW)
        
        if tempPir <= 0:
            return False, 'Все хорошо, проходите: {}'.format(t_teplovizor)
        else:
            return False, 'Все хорошо, проходите: {}'.format(round(numpy.max([t_teplovizor, tempPir]), 1))
    """
    
def valid_text(tempPir, t_teplovizor):
    iff, text = valid(tempPir, t_teplovizor)
    return text    

def valid_var(tempPir, t_teplovizor):
    iff, text = valid(tempPir, t_teplovizor)
    return iff    

def teplo(temp_tepl_Raw=0, temp_tepl=0, tempPir=0):
    temp_tepl_Raw = temp_tepl = tempPir = 0
    try:
        temp_tepl_Raw, temp_tepl = teplovizor.getMaxTemp()
        if GPIO.input(18) == False:#у нас есть отжатая кнопа?  
            tempPir = round(pirometr.get_object_1(),1)
    except: # Queue.Empty
        pass
    return temp_tepl_Raw, temp_tepl, tempPir

def Str_teplo(temp_tepl_Raw=0, temp_tepl=0, tempPir=0):# текст на  tepl
    #temp_tepl_Raw, temp_tepl, tempPir = teplo()
    temp_text_telo = "Ваша температура {}".format(temp_tepl)  
    #if (32 < tempPir < 45):
    if tempPir != 0 :   
        temp_text_Pir = "Ваша температура по руке {}".format(tempPir)
    else : 
        temp_text_Pir = "Поднесите руку"
    temp_text_tepl = valid_text(temp_tepl, tempPir)
    return temp_text_telo, temp_text_Pir, temp_text_tepl

def faces_x_y(frame, x , y , w , h): #, id_hread, return_Id_to_face): # ф-я для поиска границ
    x = y = w = h = 0
    x1 = y1 = w1 = h1 = 0
    if not frame is None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
        for (x1 , y1 , w1 , h1) in faces:
            x , y , w , h = x1 , y1 , w1 , h1       
    return x , y , w , h #, id_hread 
import tkinter as tk

def cv2_putText_flag_id_on(flag_id_on,thickness=4):##вывод v/x на экран
    if flag_id_on: #если нашли человека
        cv2.putText(frame, "V", (q_w, q_h), cv2.FONT_HERSHEY_SIMPLEX, r_w, (0, 255, 0), thickness, cv2.LINE_AA)
    else:
        cv2.putText(frame, "X", (q_w, q_h), cv2.FONT_HERSHEY_SIMPLEX, r_w, (0, 0, 255), thickness, cv2.LINE_AA) 


def cv2_putText(frame, id_person, temp_tepl_Raw, temp_tepl, tempPir, height=0, width=0): # вывод текста на экран
    channels = 0
    thickness = 1
    #height = width =  0 ## для рвзмера экрана 
    """
    
    s = Gdk.Screen.get_default()
    """
    
    if height + width == 0:
        #height, width, channels = frame.shape # по изображению
        #height, width, channels = frame.size # по изображению
        #height, width = frame.shape[:2]
        #width, height = s.get_width(), s.get_height() # по экрану?
        #width, height = desktop.width(), desktop.height() # по экрану?
        
        height = numpy.size(frame, 0)
        width = numpy.size(frame, 1)
        
        #root = tk.Tk()
        #width, height= root.winfo_screenwidth(), root.winfo_screenheight()

    
    #print("width = {}".format(width))  
    #print("height = {}".format(height))     
        
    hei_n= height - (100) # (30+25+15+20+10) *(thickness) 
    cv2.rectangle(frame, (0, height), (width, hei_n), (255, 255, 255), -1)
    
    TStr_ID1, TStr_ID2  = Str_ID(id_person)
    
    temp_text_telo, temp_text_Pir, temp_text_tepl = Str_teplo(temp_tepl_Raw, temp_tepl, tempPir)# получаем текст на тепло
    
    hei = hei_n + 20*(thickness)
    #cv2.putText(frame, Str_ID(id_person),   (5, hei),   font, 0.4*thickness, (0, 0, 0), thickness, cv2.LINE_AA)##
    cv2.putText(frame, TStr_ID1,       (5, hei),   font, 0.4*thickness, (0, 0, 0), thickness, cv2.LINE_AA)##
    hei += 20*(thickness)
    cv2.putText(frame, TStr_ID2,       (5, hei),   font, 0.4*thickness, (0, 0, 0), thickness, cv2.LINE_AA)##
    hei += 20*(thickness)
    cv2.putText(frame, temp_text_telo, (5, hei),   font, 0.4*thickness, (0, 0, 0), thickness, cv2.LINE_AA)##
    hei += 15*(thickness)
    cv2.putText(frame, temp_text_Pir,  (5, hei),   font, 0.4*thickness, (0, 0, 0), thickness, cv2.LINE_AA)##
    hei += 20*(thickness)
    cv2.putText(frame, temp_text_tepl, (5, hei),   font, 0.4*thickness, (0, 0, 0), thickness, cv2.LINE_AA)##
    hei += 10*(thickness)
    

def clearQueue(q): # обнуление очереди (чтоб без матов(часть костыля #1))
    try:
        while True:
            q.get_nowait()
    except: # Queue.Empty
        pass
         
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
cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN) 
cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

x = y = w = h = 0
"""
from gi.repository import Gdk
s = Gdk.Screen.get_default()
print s.get_width(), s.get_height()
"""
if __name__ == "__main__":


    # без обнуления
    return_Id_to_face = Queue() #очередь для сняти инфы с потока     
    #height, width = 626+100, 537 #зармеры экрана
            
    #fasehread = faseThread()
    time_out = 6 #6 # таймер на определение человека
    #temp_text_telo = ""  # текст под температуру 
    #temp_text_Pir = "" # текст под температуру руки
    #temp_text_tepl = "" # текст под решение по темпер
    flag_disease = False  # на решение по темпер
    time_ = 0 # продолжительность скана лица
    Active = True # актив прогр
    if If_Test_Foto :
        image = cv2.imread("./Test.jpg")
    color = (255, 255, 255) # цвет задника
    
    # с особым обнулением
    id_hread =  None #для потока
    
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
    if_null_hread = False #  (можно ли обнулить именно id_hread )
    if_on_fase = False # найден ли id
    #time_if = False # момент за 1 сек до time_out
    #i = 0 # ходов программы без прерывания
    while(Active):
        temp_tepl_Raw, temp_tepl, tempPir = teplo()# получаем тепло 
        #flag_disease = valid_var(temp_tepl, tempPir) 
        #temp_text_telo, temp_text_Pir, temp_text_tepl = Str_teplo(temp_tepl_Raw, temp_tepl, tempPir)# получаем текст на тепло
        time_ = time.time() - time_temp1        
        #print(if_null) 
        if if_null: # обнуление
            #print("reset")  
            """
            flag_id_on = False # найден ли id
            if_save = True
            if_null = False 
            x = y = w = h = 0
            ret = frame = None #переменная под изабр м камеры
            lag_frame_on = False 
            id_hread = None
            return_Id_to_face.put(-1) # для сняия с потока инф
            """
            led_all_off() # выкл свет  
            
            For_bz += 1
            print("For_bz = {}".format(For_bz)) 
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
            #if_null_hread = True #  (можно ли обнулить именно id_hread )# возможно косяки...
        if if_null_hread: # возможно косяки...
            if not id_hread is None: # сущ ли процесс
                if id_hread.is_alive():# заверш ли процесс
                    if_null_hread = True #  (можно ли обнулить именно id_hread )# возможно косяки...
                    if If_Test_print_reset:print("1 id_hread")  
                    #id_hread.terminate() #????????????
                    #id_hread.join()
                    #if  id_hread.is_alive():# заверш ли процесс ## может так везде?
                if not id_hread.is_alive():    
                    id_hread.close()
                    if If_Test_print_reset:print("1 id_hread 1")  
                    id_hread = None
                    if_null_hread = False
        if not If_Test_Foto :
            del frame #переменная под фрейм с камеры
            frame = None #переменная под фрейм с камеры
            ret , frame = cap.read()
                             
            if not frame is None:
                frame = cv2.flip(frame,1)
                frame = frame[:, 185:455]
        else:
        #if 1==1: # для теста
            frame = numpy.copy((image))
            
        x, y, w, h  = faces_x_y(frame, x , y, w, h)
        
        if x + y + w + h != 0 and (150 <=w or 150 <=h ) and not if_null_hread:
            if If_Test_print_reset:print("next")
            if not flag_id_on:
                if id_hread is None:#если процесс не сущ
                    fase_RGB_200_200 = numpy.copy((frame)[y:y + w, x:x + h]) 
                    clearQueue(return_Id_to_face) # обнуление очереди( костыль #1)
                    id_hread = Process(target=Id_to_face, args=(fase_RGB_200_200,return_Id_to_face))#, daemon=True
                    id_hread.start()#запуск потока по поиску в бд      
            
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)#вывод квадр
            
            time_out_ = time_out-time_
            if If_Test_print_reset:print(time_out_)
            if not flag_id_on and  1.5 < time_out_ :

                if not id_hread is None: # сущ ли процесс
                    if not id_hread.is_alive(): # заверш ли процесс
                        try:
                            id_person_temp = return_Id_to_face.get() # вытаскиваем ID
                            if If_Test_print_reset:print("id_person_temp {}".format(id_person_temp))
                        except:
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
            flag_id_on = (not (id_person is None or id_person == -1)) #True 

            r_w = w/(23) #w/23 / 21.5
            q_h = int(y+(h/2 + r_w*(10.5))) #y+h-10
            q_w = int(x+(w/2 - r_w*(9.7)))
            #if  1.0 < time_out_:
                #text_fase if 1.0 < time_out_ "{}".format(int(time_out_)) else if flag_id_on: "V" else "X"
                #cv2.putText(frame, text_fase , (q_w, q_h), cv2.FONT_HERSHEY_SIMPLEX, r_w, (0, 255, 0), 1, cv2.LINE_AA)
            #print("_____________")
            if (not (id_person is None or id_person == -1)) and ((32 < tempPir < 45) and (32 < temp_tepl < 45) and 1.0 < time_out_):
                if_save_time = True # ускорение вывода
                time_temp1 = time_out-time_-(time_out-1)
                #print("ok")
                
            if  1.0 < time_out_ and (not if_save_time): # выводим время
                cv2.putText(frame, "{}".format(int(time_out_)), (q_w, q_h), cv2.FONT_HERSHEY_SIMPLEX, r_w, (0, 255, 0), thickness_fase, cv2.LINE_AA)
            elif time_out_ <= 1.0 or (if_save_time): # выводим распазнание # 0.5 <
                cv2_putText_flag_id_on(flag_id_on, thickness_fase)#вывод v/x на экран
                """
                if flag_id_on: #если нашли человека
                    cv2.putText(frame, "V", (q_w, q_h), cv2.FONT_HERSHEY_SIMPLEX, r_w, (0, 255, 0), 5, cv2.LINE_AA)
                else:
                    cv2.putText(frame, "X", (q_w, q_h), cv2.FONT_HERSHEY_SIMPLEX, r_w, (0, 0, 255), 5, cv2.LINE_AA)   
                """
            
                
            #if 0.1 < time_out_ < 0.5:  # сохраняем 
            if  0.5 < time_out_ and (not if_save_time): # выводим время
                pass #if False: print("") # 
            elif 0.1 < time_out_ <= 0.5 or (if_save_time):  # сохраняем   
                if_save_time = False
                #For_bz += 0.5
                #print("For_bz = {}".format(For_bz)) 
                if  if_save  : 
                    #For_bz += 1   
                    if ((32 < tempPir < 45) and (32 < temp_tepl < 45)): # защита от нелюдей
                        
                        #print("_____________")
                        #print("For_bz = {}".format(For_bz)) 
                        if_save = False
                        print("on_buzer")
                        flag_disease = valid_var(temp_tepl, tempPir) 
                        if If_Test_print_reset:print("on {} log {}".format(flag_disease, id_person))
                        #on_buzer(True)
                        #dataBase.push_data_log(flag_disease, fase_RGB_200_200,  person_id=id_person, temp_pirom=tempPir, temp_teplovizor=temp_temp_tepl, raw_teplovizor=temp_tepl_Raw)
                        if (not flag_disease) and flag_id_on: # если человек и температ, то действие
                            if_on = True # при выполнении проверки на всё
                            #print(if_on)
                        else: led_red_mig()
                    else: led_red_mig()
                    if  not if_save  :
                        if_null = True
                        if If_Test_print_reset:print("reset not if_save")  
            else: 
                if_null = True
                if If_Test_print_reset:print("reset time_out_ < 0.1")  
             
        else: 
            if_null = True
            if If_Test_print_reset:print("reset x-y-h-w")  
        #print(id_person)
        cv2_putText(frame, id_person, temp_tepl_Raw, temp_tepl, tempPir, height, width) # вывод текста на экран
               
        
        
        
        #if if_on: #если нашли человека
        #    cv2_putText_flag_id_on(flag_id_on, thickness_fase) #вывод v/x на экран
        cv2.imshow('window', frame)
        
        if if_on:# если человек и температ, то действие
            print("on")
            if_on = False # при выполнении проверки на всё
            led_green_mig(3)
                
            #  действие
            time.sleep(2)
        
        
        # cv2.imshow('frame',gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            
            #faceshread.mode_run = False
            if not id_hread is None:
                if id_hread.is_alive():
                    #id_hread.join()
                    id_hread.terminate()
                id_hread.close()
            cv2.destroyAllWindows()
            
            Active = False
            #break
    if not If_Test_Foto :
        cap.release()

