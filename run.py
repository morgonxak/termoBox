import cv2
import time
import threading
import numpy
import RPi.GPIO as GPIO
import os




from app_thermometer import face_detector, processing_recognition, teplovizor, dataBase, pirometr,  pin_Thread, Song      #on_buzer,valid, led_red_pin, led_green_pin, 

frame_original = None
font = cv2.FONT_HERSHEY_COMPLEX
text = 'Здравствуйте'
text_2 = 'Подайдите поближе'
text_3 = 'Для распознования'

x = y = w = h = 0

flag_show_temp = True
flag_recognition = True
oldTime = time.time()
time_clear = time.time()
time_clear_text = time.time()
time_flag_timer = time.time()
count_timer = 0
tempPir = -1
temp_tepl = -1
temp_tepl_Raw = -1

time_if = 0
time_out = 0






last_photo_recognition_people = {"personID": None, "phpto": None}

class processing(threading.Thread):

    def __init__(self, mode_run = False):
        super().__init__()
        self.time_recognition = time.time()
        self.mode_run = mode_run
        
        self.start_event = threading.Event()
    def restart(self):
        if not self.mode_run :
            self.start_event.set()

    def run(self):
        global x, y, w, h, frame_original, flag_show_temp, time_if, time_out, time_out_all, count_timer, flag_recognition,  last_photo_recognition_people , min_w, min_h
        # time_flag_timer,temp_tepl, temp_tepl_Raw, , tempPir
        
        while (self.mode_run if self.mode_run else self.start_event.wait()) :

            if not frame_original is None:
                #if time.time() - self.time_recognition > 0.5:
                #if  time_if < time_out  :
                if True:
                    gray = cv2.cvtColor(frame_original, cv2.COLOR_BGR2GRAY)
                    faces = face_detector.detectMultiScale(gray, 1.3, 5)
                    x, y, w, h= 0,0,0,0
                    for (x1, y1, w1, h1) in faces:
                        #if x1+ y1+ w1+ h1 != 0 :# and (w1 >= min_w and h1 >= min_h ):
                        x, y, w, h = x1, y1, w1, h1
                        
                        
                        #if w >= min_w and h >= min_h: ## 150 150
                            #if not flag_recognition: break

                            #fase_RGB_200_200 = numpy.copy(frame[y:y + w, x:x + h])
                            #person_id = None # processing_recognition.predict_freme(fase_RGB_200_200)
                        """
                            if not person_id is None:
                                print("dict_res", person_id)

                                #name_user = dataBase.get_people_name_by_person_id(person_id)
                                #text = "Привет, {}".format(name_user)
                                #temp_tepl_Raw, temp_tepl = teplovizor.getMaxTemp()
                                #text_2 = "Ваше температура {}".format(temp_tepl)
                                #text_3 = "Поднесите руку"
                                #count_timer = 6
                                #time_flag_timer = time.time()

                                #last_photo_recognition_people['photo'] = numpy.copy(fase_RGB_200_200)
                                #last_photo_recognition_people['personID'] = person_id
                                #self.time_recognition = time.time()
                               # flag_recognition = False
                                #tempPir = -1

                            else:
                                print("dict_res_not", person_id)
                                #temp_tepl_Raw, temp_tepl = teplovizor.getMaxTemp()

                                #text = "не распознан"
                                #text_2 = "Ваше температура {}".format(temp_tepl)
                                #text_3 = "Поднесите руку"
                                #time_flag_timer = time.time()
                                #count_timer = 6
                                #flag_recognition = False
                                #last_photo_recognition_people['photo'] = numpy.copy(fase_RGB_200_200)
                                #last_photo_recognition_people['personID'] = person_id
                                #tempPir = -1
                                #self.time_recognition = time.time()
                        """
                else:
                    time.sleep(0.1)


"""

"""



recognition = processing(False)
recognition.start()

cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

width = 480
height = 640

cam = cv2.VideoCapture(0)
#cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
#cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
cam.set(cv2.CAP_PROP_FPS, 30)

thickness = 1

color = (255, 255, 255)
color_font = (255, 0, 0)
color_text =(0, 114, 255)
color_blue = (255, 0, 0)
color_green = (0, 255, 0)
color_read = (0, 0, 255)
color_orange =  (0, 114, 255)
lineType= 2
# FONT_ = cv2.FONT_HERSHEY_COMPLEX # фон

ROTATE_CLOCKWISE = cv2.ROTATE_90_CLOCKWISE



class cv2_out_object():
    def __init__(self):
        self.dataBase = dataBase
        self.color_blue = (255, 0, 0) 
        #self.color_green = (0, 255, 0) 
        self.color_green = (28, 110, 21) 
        self.color_read = (0, 0, 255) 
        self.color_orange = (0, 114, 255)
        
        self.color_rectangle = self.color_blue
        self.color_text = self.color_orange #(33, 47, 252) #(255, 150, 0) # цвет text
        self.color_text_time = self.color_green
        self.thickness = 4 # размер символов в квадрате
        self.FONT_ = cv2.FONT_HERSHEY_COMPLEX # фон
        self.lineType= 2

        self.frame = None
        self.i=0.01


        self.width = 0
        self.height = 0
        
        
        #self.next_()
    
    def next_(self, frame, width, height):
    
        self.frame = frame
        self.width = width
        self.height = height

    def out_text_if_teplo(self):  
        '''
        ф-я вывода строчки информации о нижнет теплеке
        '''
        
        temp_text_Pir = "Поднесите руку" #self.teplo_Th.Str_teplo(2)# получаем текст на тепл
        #if self.inputPir == 1:   
        
        self.cv2_text_separator_putTex_rectangle(text=temp_text_Pir, x=5, y=5, lins_saze_text=40, fontScale=0.99+self.i, direction=0, 
                                                    color_text = self.color_text, color_rectangle = self.color_rectangle, 
                                                    if_all_width_frame = True, Align = 1)
        self.i+=0.01
        
        print("i " , self.i)
        time.sleep(0.5)
        '''
        if self.inputPir == 1:   
            cv2.rectangle(self.frame, (74, 58), (406, 5), self.color_rectangle, -1)
            cv2.putText(self.frame, "Поднесите руку", (74, 45), self.FONT_, 1.5, self.color_text, self.thickness, self.lineType)
        
        #    return 1  
        '''
        #return self.inputPir == 1    
        return self.frame       
    
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
        
    def out_text_vso(self):
        '''
        выводим текст с писанием обработки
        возвращает: решениие можно ли пустить или нет
        '''
        
        x = 5
        y = self.height//2
        lins_saze_text=12

        

        Str_ = "Температура превышена. Ожидайте сотрудника службы охраны." #self.Str_ID()
        self.cv2_text_separator_putTex_rectangle(text=Str_, x=x, y=y, direction=0, lins_saze_text=lins_saze_text, fontScale=1.5 + 0.38, 
                                                color_text = self.color_text, color_rectangle = self.color_green, if_all_width_frame = True, 
                                                Align = 1 ) #  if if_ else self.color_read
        
        
        #self.i+=0.01
        
        #print("i " , self.i)
        #time.sleep(0.5)
        
        return self.frame
        
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
                    cv2.rectangle(self.frame, (0, y+baseline), (self.width, y - (text_height+baseline)), color_rectangle, -1)
                    
                    
                if Align == 1:
                    x = self.width//2 - text_width//2   
                    
                if not if_all_width_frame:
                    cv2.rectangle(self.frame, (x, y+baseline), (x+text_width, y-(text_height+baseline)), color_rectangle, -1)
                    
                cv2.putText(self.frame, text, (x, y), self.FONT_, fontScale, color_text, self.thickness, self.lineType)
                    #None
                #else:
                    #if not if_all_width_frame:
                    #    cv2.rectangle(self.frame, (x-dist, y+dist), (x+text_width+dist, y-text_height-dist), color_rectangle, -1)
                    #cv2.putText(self.frame, text, (x, y), self.FONT_, fontScale, color_text, self.thickness, self.lineType)
                
                print( " ", x, y+baseline,self.width, y-(text_height+baseline))
                #print( " ", x, y+baseline,x+text_width, y-(text_height+baseline))
                print(text, " ", x, y)
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
    


def out_rectangle_backdrop(frame,width,height, rectangle_width: int = 320, rectangle_height: int = 320):
    '''
    ф-я вывода на экран квадрата по центру для вставки цица
    '''
    # print(self.x , self.w, self.y , self.h)
    '''  
    rectangle_width = 320
    rectangle_height = 320
    '''
    rec_x = width // 2 - rectangle_width // 2
    rec_y = height // 2 - rectangle_height // 2

    # print(rec_x,rec_y, rectangle_width, rectangle_height )
    return cv2.rectangle(frame, (rec_x, rec_y), (rec_x + rectangle_width, rec_y + rectangle_height), color_green,
                  lineType)  # вывод квадр

def pull_text(frame, text):
    # width = 480
    # height = 640
    cv2.rectangle(frame, (0, 0), (width, height-500), color_font, -1)
    cv2.putText(frame, text, (5, 5), font, 1, color_text, thickness)

        
def if_input_Pir(input_Pir):
    if_ = (4<=input_Pir<=10) or input_Pir == 0
    #print("input_Pir = ", input_Pir, "//", if_)
    return if_ 

def if_pir(input_Pir, Pir, Pir_ambient):
    return False

def out_text_end(frame, if_:bool):
    color_green = (28, 110, 21) #(0, 255, 0)
    color_read = (0, 0, 255)
    thickness = 4     
    lineType = 2
    FONT_ = cv2.FONT_HERSHEY_COMPLEX 
    color_orange = (0, 184,245) #(0, 114, 255) 

    if if_:
        cv2.rectangle(frame, (0, 495), (490, 320), color_green, -1)
        #cv2.rectangle(frame, (0, 485), (480, 438), color_green, -1)
        cv2.putText(frame, "Все хорошо,", (20, 384), FONT_, 2, color_orange, thickness, lineType)
        cv2.putText(frame, "проходите", (52, 472), FONT_, 2, color_orange, thickness, lineType)
       
        return True
    else:

        cv2.rectangle(frame, (0, 70), (480, 570), color_read, -1)
        ww = 130
        cv2.putText(frame, "Температура", (31, ww), FONT_, 1.88, color_orange, thickness, lineType)
        ww += 82
        cv2.putText(frame, "превышена.", (41, ww), FONT_, 1.88, color_orange, thickness, lineType)
        ww += 82
        cv2.putText(frame, "Ожидайте", (75, ww), FONT_, 1.88, color_orange, thickness, lineType)
        ww += 82
        cv2.putText(frame, "сотрудника", (46, ww), FONT_, 1.88, color_orange, thickness, lineType)
        ww += 82
        cv2.putText(frame, "службы", (114, ww), FONT_, 1.88, color_orange, thickness, lineType)
        ww += 82
        cv2.putText(frame, "охраны.", (108, ww), FONT_, 1.88, color_orange, thickness, lineType)
        
        #cv2.rectangle(frame, (0, 495), (490, 320), color_read, -1)
        #cv2.rectangle(frame, (66, 365), (415, 320), color_read, -1)
        #cv2.rectangle(frame, (54, 411), (426, 366), color_read, -1)
        #cv2.putText(frame, "Ошибка измерения.", (66, 354), FONT_, 0.99, color_orange, thickness, lineType)
        #cv2.putText(frame, "Рука не обнаружена.", (54, 400), FONT_, 0.99, color_orange, thickness, lineType)

    return False
 
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
        
header = numpy.zeros((40,480,3), numpy.uint8)
color_blue = (255, 0, 0)
#thickness = 4    
color_green = (0, 255, 0)
frame_time = 3
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

time_out = 0 # таймер на определение человека

time_out_all = time_out + int(max(song_True.len_(), song_False.len_(), 2) )+ 1
time_if = 0

ret, frame = cam.read()
frame = cv2.rotate(frame, ROTATE_CLOCKWISE)
frame = cv2.flip(frame, 0)
height, width = cv2_height_width(frame )# размер скрина
min_w, min_h = cv2_rectangle_min_W_H(height ,width)
if_pyglet = True 

input_Pir, Pir, Pir_ambient = 0,0,0
if_input = False
if_save = True
cv2_out = cv2_out_object()
while True:
    
    ret, frame = cam.read()
    #print("qqq")
    if ret:
        #pin_Th.pin_all(False)
        #print("0000")
        t1 = time.time()

        frame = cv2.rotate(frame, ROTATE_CLOCKWISE)
        frame = cv2.flip(frame, 0)
        height, width = cv2_height_width(frame )# размер скрина
        cv2_out.next_(frame, width, height)

        # print(frame.shape)
        #frame = cv2.resize(frame, (1280, 720))
        frame_original = frame
        #print("frame_original", type(frame_original))
        #print("frame_original", id(frame_original))
        #print("frame", id(frame))
        recognition.restart()
        
        
        #1280×720


        #cv2.putText(frame, text, (10, 410), font, 0.8, (0, 0, 0), 1, cv2.LINE_AA)
        #cv2.putText(frame, text_2, (5, 435), font, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
        #cv2.putText(frame, text_3, (5, 450), font, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
        time_if = time.time() - time_clear
        #if x + y + w + h != 0 :#and (min_w <=w or min_h <=h ):
        if True:    
            
            #print("1111")
            """
            if  time_if < time_out : 
                
                
                #print("2222")
                frame = out_rectangle_backdrop(frame, width,height)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color_blue, lineType)#вывод квадр
                cv2.putText(frame, "{}".format(int(time_out-(time_if)+0.4)), (x+10, y+60), cv2.FONT_HERSHEY_SIMPLEX, w / 200, color_green, thickness, cv2.LINE_AA)
            
            
                if_input = if_input_Pir(input_Pir) # (if_pir(input_Pir, Pir, Pir_ambient))
                #print("if_input", if_input)
                if if_input:
                    #pin_Th.pin_mig("blue", True)#
                    #pin_Th.pin_all(False)     
                    time_clear = time.time()-(time_out+0.1)
                else:
                    pin_Th.pin_mig("red", True)
            """ 
            if not if_input:
                #cv2.rectangle(frame, (100, 50), (381, 5), color_blue, -1)
                #cv2.putText(frame, "Поднесите руку", (100, 39), cv2.FONT_HERSHEY_COMPLEX, 0.99, color_orange, 4, 1)
                #frame = cv2_out.out_text_if_teplo()
                

                
                cv2.rectangle(frame, (0, 69), (480, -10), color_blue, -1)
                cv2.putText(frame, "Поднесите руку", (30, 40), cv2.FONT_HERSHEY_COMPLEX, 1.5, color_orange, 4, 1)
                if x + y + w + h != 0 :
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color_blue, lineType)#вывод квадр
                input_Pir, Pir, Pir_ambient = pirometr.get_() # получаем тепло 
                if_input = if_input_Pir(input_Pir) # (if_pir(input_Pir, Pir, Pir_ambient))
                time_clear = time.time()
                time_if = time.time() - time_clear
            if if_input and time_if < time_out_all: 
                #print("3333")   
                    
                #if_input = if_input_Pir(input_Pir)
                
                #print("if_input 2", if_input)
                #if_input = True
                #print("if_input 2 {}".format( if_input ))
                if if_input :
                    #print("if_input 1")
                    if_out_text_end = out_text_end(frame, (if_pir(input_Pir, Pir, Pir_ambient) and if_input_Pir(input_Pir)) )
                    #frame = cv2_out.out_text_vso()
                
                    #if_out_text_end = False
                    #print("out_text_end 2")
                    #if_out_text_end = out_text_end(frame, True )
                    
                    #print("if_out_text_end", if_out_text_end)
                    pin_Th.pin_on_off("green" if if_out_text_end else "red", True)
                    """
                    if if_out_text_end:
                        pin_Th.pin_on_off("green", True)
                    else:
                        pin_Th.pin_on_off("red", True)
                    """
                    if if_pyglet :
                        
                        (song_True if if_out_text_end else song_False).restart()
                        if_pyglet = False
                        #print("if_pyglet")
                        
                    pin_Th.pin_on_time("door", time_out_all)
                    if if_save:
                        if_save = False
                        #dataBase.save_frame_image(fase_RGB_200_200)
                        dataBase.pull_log_Pir(Pir, Pir_ambient, input_Pir)  
                else:
                    #print("if_input else")
                    time_clear = time.time()-(time_out_all+0.1)
                #print("qqqqqwq")
                
            elif time_if < time_out_all+1 :
                #print("time_if < time_out_all+1")
                pin_Th.pin_all(False)  
                #if_save = True
                None  
                       
            else:
                #print("else")
                pin_Th.pin_all(False)  
                #frame = out_rectangle_backdrop(frame, width,height)
                x = y = w = h = 0
                if_save = True    
                time_clear = time.time()
                if_input = False
                if_pyglet = True
        else:
            pin_Th.pin_all(False) 
            #frame = out_rectangle_backdrop(frame, width,height)
            x = y = w = h = 0
            if_save = True
            if_input = False
            time_clear = time.time()
            
            
        '''  
            
        if count_timer != 0:
            if time.time() - time_flag_timer > 1:
                count_timer -=1
                text_3 = "Поднесите руку {}".format(count_timer)
                
                    
                if GPIO.input(18) == False:
                    print('Button Pressed')
                    tempPir = pirometr.get_object_1()

                time_clear_text = time.time()
                time_flag_timer = time.time()
        else:
            if not flag_recognition:
                flag_disease, text_3 = valid(tempPir, temp_tepl)
                on_buzer(True)
                #dataBase.push_data_log(flag_disease, last_photo_recognition_people['photo'],  person_id=last_photo_recognition_people['personID'], temp_pirom=tempPir, temp_teplovizor=temp_tepl, raw_teplovizor=temp_tepl_Raw)

            flag_recognition = True

        if time.time() - time_clear > 1:
            x = y = w = h = 0
            if_save = True
            time_clear = time.time()

        if time.time() - time_clear_text > 4:
            if flag_recognition:
                text = 'Здравствуйте'
                text_2 = 'Подайдите поближе'
                text_3 = 'Для распознования'
                GPIO.output(led_red_pin, GPIO.HIGH)
                GPIO.output(led_green_pin, GPIO.HIGH)

                tempPir = t_teplovizor = -1
                flag_show_temp = True
                time_clear_text = time.time()
        '''
        #frame = out_rectangle_backdrop(frame)

       # frame = numpy.concatenate((frame, header), axis=0)

        #pull_text(frame, 'поднесите руку')
        cv2.imshow("window", frame)
        
        t2 = time.time()
        print(t2 - t1)
    key = cv2.waitKey(1)
    if key == ord('q'):
        recognition.mode_run = False
        cv2.destroyAllWindows()
        break
