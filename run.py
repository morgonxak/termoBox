import cv2
import time
import threading
import numpy
import RPi.GPIO as GPIO

from app_thermometer import face_detector, processing_recognition, teplovizor, dataBase, pirometr, valid, led_red_pin, led_green_pin, on_buzer

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
last_photo_recognition_people = {"personID": None, "phpto": None}

class processing(threading.Thread):

    def __init__(self):
        super().__init__()
        self.time_recognition = time.time()
        self.mode_run = True

    def run(self):
        global x, y, w, h, frame_original, flag_show_temp, text, text_2, text_3, count_timer, time_flag_timer, flag_recognition, temp_tepl, last_photo_recognition_people, tempPir
        while self.mode_run:

            if not frame_original is None:
                if time.time() - self.time_recognition > 0.5:
                    gray = cv2.cvtColor(frame_original, cv2.COLOR_BGR2GRAY)
                    faces = face_detector.detectMultiScale(gray, 1.3, 5)

                    for (x, y, w, h) in faces:
                        x, y, w, h = x, y, w, h
                        if w >= 150 and h >= 150:
                            if not flag_recognition: break

                            fase_RGB_200_200 = numpy.copy(frame[y:y + w, x:x + h])
                            person_id = processing_recognition.predict_freme(fase_RGB_200_200)

                            if not person_id is None:
                                print("dict_res", person_id)
                                on_buzer()
                                name_user = dataBase.get_people_name_by_person_id(person_id)
                                text = "Привет, {}".format(name_user)
                                temp_tepl = teplovizor.getMaxTemp()
                                text_2 = "Ваше температура {}".format(temp_tepl)
                                text_3 = "Поднесите руку"
                                count_timer = 6
                                time_flag_timer = time.time()

                                last_photo_recognition_people['photo'] = numpy.copy(fase_RGB_200_200)
                                last_photo_recognition_people['personID'] = person_id
                                self.time_recognition = time.time()
                                flag_recognition = False
                                tempPir = -1

                            else:
                                print("dict_res_not", person_id)
                                temp_tepl = teplovizor.getMaxTemp()
                                on_buzer()
                                text = "не распознан"
                                text_2 = "Ваше температура {}".format(temp_tepl)
                                text_3 = "Поднесите руку"
                                time_flag_timer = time.time()
                                count_timer = 6
                                flag_recognition = False
                                last_photo_recognition_people['photo'] = numpy.copy(fase_RGB_200_200)
                                last_photo_recognition_people['personID'] = person_id
                                tempPir = -1
                                self.time_recognition = time.time()

recognition = processing()
recognition.start()
cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


cam = cv2.VideoCapture(0)
thickness = -1

color = (255, 255, 255)
while True:

    ret, img = cam.read()
    if ret:
        frame = img[:, 185:455]
        frame_original = frame

        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.rectangle(frame, (0, 480), (270, 380), color, thickness)

        cv2.putText(frame, text, (10, 410), font, 0.8, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, text_2, (5, 435), font, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, text_3, (5, 450), font, 0.4, (0, 0, 0), 1, cv2.LINE_AA)

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

                dataBase.push_data_log(flag_disease, last_photo_recognition_people['photo'],  person_id=last_photo_recognition_people['personID'], temp_pirom=tempPir, temp_teplovizor=temp_tepl)


            flag_recognition = True

        if time.time() - time_clear > 1:
            x = y = w = h = 0
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

        cv2.imshow("window", frame)


    key = cv2.waitKey(1)
    if key == ord('q'):
        recognition.mode_run = False
        cv2.destroyAllWindows()
        break
