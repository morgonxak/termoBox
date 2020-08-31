'''
команда для открытия доступа к устройсву не из под бога
https://github.com/ktandon1/RubADubDub/tree/master/pyseek
sudo chmod 666 /dev/bus/usb/001/005
'''

import usb.core
import usb.util
import numpy as np
from PIL import Image
from math import log
import cv2
from scipy import ndimage
import pickle
import os
import threading
from math import log
import sys
import subprocess
import random

#global calibration array variables
imcalib = 0
imgain = 0

#frame variables
counter=0
mode=0

class Thermal(threading.Thread):

    def __init__(self, debug=False):
        super().__init__()
        self.debug = debug
        self.frame = None
        self.temp_centrPoint = None
        self.dev = None

    def __usbinit(self):
        # найди наш Термальный прибор 289d: 0010
        self.dev = usb.core.find(idVendor=0x289d, idProduct=0x0010)

        # это было найдено?
        if self.dev is None:
            raise ValueError('Device not found')

        # установить активную конфигурацию. Без аргументов первый
        # конфигурация будет активной
        self.dev.set_configuration()

        # получить экземпляр конечной точки
        cfg = self.dev.get_active_configuration()
        intf = cfg[(0, 0)]

        ep = usb.util.find_descriptor(
            intf,
            # соответствует первой конечной точке OUT
            custom_match= \
                lambda e: \
                    usb.util.endpoint_direction(e.bEndpointAddress) == \
                    usb.util.ENDPOINT_OUT)

        assert ep is not None

        return self.dev

    def __send_msg(self, dev, bmRequestType, bRequest, wValue=0, wIndex=0, data_or_wLength=None, timeout=None):
        '''
        send_msg отправляет сообщение, которое не нужно или получает ответ
        :param dev:
        :param bmRequestType:
        :param bRequest:
        :param wValue:
        :param wIndex:
        :param data_or_wLength:
        :param timeout:
        :return:
        '''
        assert (dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout) == len(data_or_wLength))

    def __receive_msg(self, dev, bmRequestType, bRequest, wValue=0, wIndex=0, data_or_wLength=None, timeout=None):
        '''
        Функция чтения после отправки сообщения
        :param dev:
        :param bmRequestType:
        :param bRequest:
        :param wValue:
        :param wIndex:
        :param data_or_wLength:
        :param timeout:
        :return:
        '''
        zz = dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength,
                               timeout)  # == len(data_or_wLength))
        return zz

    def __camerainit(self, dev):
        '''
        Настройка камеры
        :param dev:
        :return:
        '''
        msg = b'\x01'
        self.__send_msg(dev, 0x41, 0x54, 0, 0, msg)  # 0x54 = 84 Target Platform 0x01 = Android

        self.__send_msg(dev, 0x41, 0x3C, 0, 0, b'\x00\x00')  # 0x3c = 60 Set operation mode    0x0000  (Sleep)
        ret1 = self.__receive_msg(dev, 0xC1, 0x4E, 0, 0, 4)  # 0x4E = 78 Get Firmware Info
        print("1: ", ret1)
        # array('B', [1, 3, 0, 0])

        ret2 = self.__receive_msg(dev, 0xC1, 0x36, 0, 0, 12)            # 0x36 = 54 Read Chip ID
        print("2: ", ret2)
        # array('B', [20, 0, 12, 0, 86, 0, 248, 0, 199, 0, 69, 0])

        self.__send_msg(dev, 0x41, 0x56, 0, 0, b'\x20\x00\x30\x00\x00\x00')  # 0x56 = 86 Set Factory Settings Features
        ret3 = self.__receive_msg(dev, 0xC1, 0x58, 0, 0, 0x40)                              # 0x58 = 88 Get Factory Settings
        print("3: ", ret3)
        # array('B', [2, 0, 0, 0, 0, 112, 91, 69, 0, 0, 140, 65, 0, 0, 192, 65, 79, 30, 86, 62, 160, 137, 64, 63, 234, 149, 178, 60, 0, 0, 0, 0, 0, 0, 0, 0, 72, 97, 41, 66, 124, 13, 1, 61, 206, 70, 240, 181, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 66, 0, 0, 2, 67])

        self.__send_msg(dev, 0x41, 0x56, 0, 0, b'\x20\x00\x50\x00\x00\x00')  # 0x56 = 86 Set Factory Settings Features
        ret4 = self.__receive_msg(dev,0xC1, 0x58, 0, 0, 0x40)                              # 0x58 = 88 Get Factory Settings
        print("4: ", ret4)
        # array('B', [0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 255, 161, 248, 65, 63, 40, 127, 119, 60, 44, 101, 55, 193, 240, 133, 129, 63, 244, 253, 96, 66, 40, 15, 155, 63, 43, 127, 103, 186, 9, 144, 186, 52, 0, 0, 0, 0, 0, 0, 2, 67, 0, 0, 150, 67, 0, 0, 0, 0])

        self.__send_msg(dev, 0x41, 0x56, 0, 0, b'\x20\x00\x30\x00\x00\x00')#b'\x0C\x00\x70\x00\x00\x00')  # 0x56 = 86 Set Factory Settings Features
        ret5 = self.__receive_msg(dev,0xC1, 0x58, 0, 0, 0x18)                              # 0x58 = 88 Get Factory Settings
        print("5: ", ret5)
        # array('B', [0, 0, 0, 0, 255, 255, 255, 255, 190, 193, 249, 65, 205, 204, 250, 65, 48, 42, 177, 191, 200, 152, 147, 63])

        self.__send_msg(dev, 0x41, 0x56, 0, 0, b'\x06\x00\x08\x00\x00\x00')  # 0x56 = 86 Set Factory Settings Features
        ret6 = self.__receive_msg(dev,0xC1, 0x58, 0, 0, 0x0C)                              # 0x58 = 88 Get Factory Settings
        print("6: ", ret6)
        # array('B', [49, 52, 48, 99, 49, 48, 69, 52, 50, 78, 55, 49])

        self.__send_msg(dev, 0x41, 0x3E, 0, 0, b'\x08\x00')  # 0x3E = 62 Set Image Processing Mode 0x0008 Normal, 0x00 no shutter, other modes also possible, try at you own risk
        ret7 = self.__receive_msg(dev,0xC1, 0x3D, 0, 0, 2)                                 # 0x3D = 61 Get Operation Mode
        print("7: ", ret7)
        # array('B', [0, 0])

        #self.send_msg(dev, 0x41, 0x37, 0, 0, b'\x00\x00')  # 0x37 = 55 Toggle shutter

        self.__send_msg(dev, 0x41, 0x3E, 0, 0, b'\x08\x00')  # 0x3c = 60 Set Operation Mode         0x0001  (Run)
        self.__send_msg(dev, 0x41, 0x3C, 0, 0, b'\x01\x00')  # 0x3c = 60 Set Operation Mode         0x0001  (Run)
        ret8 = self.__receive_msg(dev, 0xC1, 0x3D, 0, 0, 2)                                 # 0x3D = 61 Get Operation Mode
        print("8: ", ret8)
        # array('B', [1, 0])

    def __read_frame(self, dev):  # Send a read frame request
        '''
        Включает режим получения данных и после получает их
        :param dev:
        :return:
        '''
        self.__send_msg(dev, 0x41, 0x53, 0, 0, b'\xC0\x7E\x00\x00')  # 0x53 = 83 Set Start Get Image Transfer

        try:
            data = dev.read(0x81, 0x3F60)
            data += dev.read(0x81, 0x3F60)
            data += dev.read(0x81, 0x3F60)
            data += dev.read(0x81, 0x3F60)

        except usb.USBError as e:
            print("device error {}".format(e))
            data = None

        return data

    def initialize(self):
        '''
        Настройка устройства
        :return:
        '''
        try:
            self.dev = self.__usbinit()
            self.__camerainit(self.dev)
            return self.dev
        except BaseException as e:
            print("ERROR init {}".format(e))
            return None

    def deinit(self):
        '''
        Переводит устроство в сон
        :param dev:
        :return:
        '''
        if not self.dev is None:
            msg = '\x00\x00'
            for i in range(3):
                self.__send_msg(self.dev, 0x41, 0x3C, 0, 0, msg)  # 0x3c = 60  Set Operation Mode 0x0000 (Sleep)
            self.dev = None


    def getFrame(self):
        '''
        Для обработки
        :return:
        '''
        #frame = cv2.resize(self.frame, (640, 480))
        return self.frame


    def getMaxTemp(self, x, y, w, h):
        try:
            #x, y, w, h = bbox[0]
            if self.tempC is None: return 0

            frame = cv2.resize(self.tempC, (640, 480))
            crop_ir = frame[x:x + w, y:y + h]
            cv2.imshow("test", crop_ir)
            max = np.max(crop_ir)
            # max = np.mean(self.tempC)
            max = self.calk(max)

            # max = random.uniform(36, 36.8)
            # max = round(max, 1)

        except BaseException as e:
            print("error {}".format(e))
            max = 0
        return max

    def getFrame_web(self):
        '''
        Передает картинку для веба
        :return:
        '''
        frame = cv2.resize(self.frame, (640, 480))
        ret, jpeg = cv2.imencode('.jpg', frame*255)
        return jpeg.tobytes()

    def getTempCenterPoint(self):
        '''
        температура центральной точки у тепловизора
        :return:
        '''
        return self.temp_centrPoint

    def calk(self,RAW):

        offset = 30000
        if (RAW + offset> 2**16):
            x = RAW + offset - 2**16
        else:
            x = RAW + offset

        # y2 = 0.0122*x-325.6
        y = 458.64*log(x) - 4685.9
        return y

    def run(self):
        self.status_get_frame = False
        frameID4 = None
        calibImage = None
        while True:
            while self.status_get_frame:
                key = cv2.waitKey(1)
                if key & 0xFF == ord('q'):
                    self.deinit()
                    break

                # Send read frame request
                self.__send_msg(self.dev, 0x41, 0x53, 0, 0, b'\xC0\x7E\x00\x00')
                try:
                    ret9 = self.dev.read(0x81, 0x3F60)
                    ret9 += self.dev.read(0x81, 0x3F60)
                    ret9 += self.dev.read(0x81, 0x3F60)
                    ret9 += self.dev.read(0x81, 0x3F60)
                except usb.USBError as e:
                    sys.exit()

                raw_img = Image.frombytes("I", (208, 156), bytes(ret9), "raw", "I;16")

                img = np.asarray(raw_img).astype('uint16')
                status = ret9[20]

                if status == 1:
                    calibImage = np.array(img, copy=True)

                elif status == 3:
                    proc_img = self.processFrame(img, calibImage, frameID4)


                    temp = img - calibImage
                    # print("pix:" , temp[207 // 2, 154 // 2])

                    self.tempC = self.calk(temp[207 // 2, 154 // 2])

                    self.temp_centrPoint = self.calk(temp[207 // 2, 154 // 2])


                    nzIdx = np.nonzero(proc_img)
                    nzMin = np.min(proc_img[nzIdx])
                    nzMax = np.max(proc_img[nzIdx])
                    disp_img = (proc_img - nzMin) / (nzMax - nzMin)
                    disp_img[proc_img == 0] = 0

                    disp_img = np.rot90(disp_img, 1)
                    disp_img = np.flipud(disp_img)

                    self.frame = np.copy(disp_img)

                    cv2.imshow('win', disp_img)
                    cv2.waitKey(5)

                elif status == 4:
                    frameID4 = np.array(img, copy=True)

            #

    def processFrame(self, frame, calibFrame, frameID4):
        mask = np.logical_and(True, frame > 2000)
        mask = np.logical_and(mask, frame < 16383)
        mask = np.logical_and(mask, calibFrame > 2000)
        mask = np.logical_and(mask, calibFrame < 16383)

        p = np.array(frame, dtype=np.float64)
        div = p / 2048.0 + 8
        r = np.divide(frameID4, div)
        p += 16384.0
        p -= calibFrame
        p += r

        # преобразовать в градусы Цельсия
        p -= 15000
        p /= 50.338

        p[mask != True] = 0
        return p


if __name__ == '__main__':
    import time
    App = Thermal(True)
    App.initialize()

    App.start()
    oldTime = time.time()
    time.sleep(15)





