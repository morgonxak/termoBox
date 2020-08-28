import numpy
import cv2
import os
from math import log
import pickle
import base64


def device_sensor_to_k(sensor):
    # formula from http://aterlux.ru/article/ntcresistor-en

    ref_temp = 297.0  # 23C from table
    ref_sensor = 6616.0  # ref value from table
    beta = 200  # best beta coef we've found
    part3 = log(sensor) - log(ref_sensor)
    parte = part3 / beta + 1.0 / ref_temp
    return 1.0 / parte - 273.15

def openPickl(pathPickl):
    with open(pathPickl, 'rb') as f:
        data_new = pickle.load(f)
    return data_new

def getFrame_web(image):
    frame = cv2.resize(image, (640, 480))
    ret, jpeg = cv2.imencode('.jpg', frame)
    return jpeg.tobytes()

def getFrameBase64(image):
    retval, buffer = cv2.imencode('.jpg', image)
    jpg_as_text = base64.b64encode(buffer)
    return jpg_as_text

pathDirCSV = r'/home/dima/PycharmProjects/seek_thermal/app_thermometer/rc/image'
listDir = os.listdir(pathDirCSV)
for count, name in enumerate(listDir):
    if count == 1: break

    print("Name image", name)
    pathImage = os.path.join(pathDirCSV, name)
    image = openPickl(pathImage)
    print(image)
    base64 = getFrameBase64(image*255)

    print(base64)
    cv2.imshow(name, image)
    cv2.waitKey()

