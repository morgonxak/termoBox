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

dict_connect_settings = {"database": "thermobox",
                         "user": "pi",
                         "password": "asm123",
                         "host": "127.0.0.1",
                          "port": "5432"}

path_haarcascade = '/home/pi/project/termoBox/app_thermometer/rc/haarcascade_frontalface_default.xml'
pathProject = '/home/pi/project/termoBox/expiriments'

#Recognition
face_detector = cv2.CascadeClassifier(path_haarcascade)

k = 1
path_cvm_model = os.path.join(pathProject, 'svm_model_{}.pk'.format(k))
path_knn_model = os.path.join(pathProject, 'knn_model_{}.pk'.format(k))

model_cvm = pickle.load(open(path_cvm_model, 'rb'))
model_knn = pickle.load(open(path_knn_model, 'rb'))

processing_recognition = processing_faceid(model_cvm, model_knn)
##########################

teplovizor = amg88()
pirometr = MLX90614(SMBus(1))

dataBase = BD(dict_connect_settings)

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def valid(tempPir, t_teplovizor):
    '''
    Решения о состоянии здоровья
    :param tempPir:
    :param t_teplovizor:
    :return: текст сообщения
    '''
    if t_teplovizor >= 37.2 or tempPir >= 37.2:
        if tempPir == -1:
            return True, 'Обратитесь к врачу: {}'.format(t_teplovizor)
        else:
            return True, 'Обратитесь к врачу: {}: '.format(round(numpy.max([t_teplovizor, tempPir]), 1))
    else:
        if tempPir == -1:
            return False, 'Все хорошо, проходите: {}'.format(t_teplovizor)
        else:
            return False, 'Все хорошо, проходите: {}'.format(round(numpy.max([t_teplovizor, tempPir]), 1))
