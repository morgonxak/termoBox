'''
команда для открытия доступа к устройсву не из под бога
sudo chmod 666 /dev/bus/usb/001/005
'''

import usb.core
import usb.util
import numpy as np
import sys
import time
from PIL import Image
import numpy
import cv2
from scipy import ndimage
import pickle
import os
# import colorscale

# import tkinter as Tkinter


#global calibration array variables
imcalib = 0
imgain = 0

#frame variables
counter=0
mode=0


class Thermal(Tkinter.Tk):
# class Thermal():

    def __init__(self):
        Tkinter.Tk.__init__(self)
        scl = Tkinter.Scale(self, from_=0, to=255, length=200, orient=Tkinter.HORIZONTAL, label='Bottom Range')
        scl.set(0)
        scl.grid(row=0, column=0, sticky='W')

        scl1 = Tkinter.Scale(self, from_=0, to=255, length=200, orient=Tkinter.HORIZONTAL, label='Top Range')
        scl1.set(64)
        scl1.grid(row=0, column=2)

        scl2 = Tkinter.Scale(self, from_=100, to=300, length=200, orient=Tkinter.HORIZONTAL, label='Tuning')
        scl2.set(200)
        scl2.grid(row=0, column=1)

        self.scl = scl
        self.scl1 = scl1
        self.scl2 = scl2

        palettes = dict()
        #palettes['tillscale'] = colorscale.TillPalette()

        self.palettes = palettes


    def usbinit(self):
        # найди наш Термальный прибор 289d: 0010
        dev = usb.core.find(idVendor=0x289d, idProduct=0x0010)

        # это было найдено?
        if dev is None:
            raise ValueError('Device not found')

        # установить активную конфигурацию. Без аргументов первый
        # конфигурация будет активной
        dev.set_configuration()

        # получить экземпляр конечной точки
        cfg = dev.get_active_configuration()
        intf = cfg[(0, 0)]

        ep = usb.util.find_descriptor(
            intf,
            # соответствует первой конечной точке OUT
            custom_match= \
                lambda e: \
                    usb.util.endpoint_direction(e.bEndpointAddress) == \
                    usb.util.ENDPOINT_OUT)

        assert ep is not None
        self.dev = dev
        return dev

    # send_msg отправляет сообщение, которое не нужно или получает ответ
    def send_msg(self, dev, bmRequestType, bRequest, wValue=0, wIndex=0, data_or_wLength=None, timeout=None):
        assert (dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength, timeout) == len(data_or_wLength))

    # метод псевдонимов, чтобы сделать код проще для чтения
    # получать смс на самом деле также отправляет сообщение.
    def receive_msg(self, dev, bmRequestType, bRequest, wValue=0, wIndex=0, data_or_wLength=None, timeout=None):
        zz = dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength,
                               timeout)  # == len(data_or_wLength))
        return zz


    # Инициализация камеры
    def camerainit(self, dev):

        msg = b'\x01'
        self.send_msg(dev, 0x41, 0x54, 0, 0, msg)  # 0x54 = 84 Target Platform 0x01 = Android

        self.send_msg(dev, 0x41, 0x3C, 0, 0, b'\x00\x00')  # 0x3c = 60 Set operation mode    0x0000  (Sleep)
        ret1 = self.receive_msg(dev, 0xC1, 0x4E, 0, 0, 4)  # 0x4E = 78 Get Firmware Info
        print("1: ", ret1)
        # array('B', [1, 3, 0, 0])

        ret2 = self.receive_msg(dev, 0xC1, 0x36, 0, 0, 12)            # 0x36 = 54 Read Chip ID
        print("2: ", ret2)
        # array('B', [20, 0, 12, 0, 86, 0, 248, 0, 199, 0, 69, 0])

        self.send_msg(dev, 0x41, 0x56, 0, 0, b'\x20\x00\x30\x00\x00\x00')  # 0x56 = 86 Set Factory Settings Features
        ret3 = self.receive_msg(dev, 0xC1, 0x58, 0, 0, 0x40)                              # 0x58 = 88 Get Factory Settings
        print("3: ", ret3)
        # array('B', [2, 0, 0, 0, 0, 112, 91, 69, 0, 0, 140, 65, 0, 0, 192, 65, 79, 30, 86, 62, 160, 137, 64, 63, 234, 149, 178, 60, 0, 0, 0, 0, 0, 0, 0, 0, 72, 97, 41, 66, 124, 13, 1, 61, 206, 70, 240, 181, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 66, 0, 0, 2, 67])

        self.send_msg(dev, 0x41, 0x56, 0, 0, b'\x20\x00\x50\x00\x00\x00')  # 0x56 = 86 Set Factory Settings Features
        ret4 = self.receive_msg(dev,0xC1, 0x58, 0, 0, 0x40)                              # 0x58 = 88 Get Factory Settings
        print("4: ", ret4)
        # array('B', [0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 255, 161, 248, 65, 63, 40, 127, 119, 60, 44, 101, 55, 193, 240, 133, 129, 63, 244, 253, 96, 66, 40, 15, 155, 63, 43, 127, 103, 186, 9, 144, 186, 52, 0, 0, 0, 0, 0, 0, 2, 67, 0, 0, 150, 67, 0, 0, 0, 0])

        self.send_msg(dev, 0x41, 0x56, 0, 0, b'\x20\x00\x30\x00\x00\x00')#b'\x0C\x00\x70\x00\x00\x00')  # 0x56 = 86 Set Factory Settings Features
        ret5 = self.receive_msg(dev,0xC1, 0x58, 0, 0, 0x18)                              # 0x58 = 88 Get Factory Settings
        print("5: ", ret5)
        # array('B', [0, 0, 0, 0, 255, 255, 255, 255, 190, 193, 249, 65, 205, 204, 250, 65, 48, 42, 177, 191, 200, 152, 147, 63])

        self.send_msg(dev, 0x41, 0x56, 0, 0, b'\x06\x00\x08\x00\x00\x00')  # 0x56 = 86 Set Factory Settings Features
        ret6 = self.receive_msg(dev,0xC1, 0x58, 0, 0, 0x0C)                              # 0x58 = 88 Get Factory Settings
        print("6: ", ret6)
        # array('B', [49, 52, 48, 99, 49, 48, 69, 52, 50, 78, 55, 49])

        self.send_msg(dev, 0x41, 0x3E, 0, 0, b'\x08\x00')  # 0x3E = 62 Set Image Processing Mode 0x0008 Normal, 0x00 no shutter, other modes also possible, try at you own risk
        ret7 = self.receive_msg(dev,0xC1, 0x3D, 0, 0, 2)                                 # 0x3D = 61 Get Operation Mode
        print("7: ", ret7)
        # array('B', [0, 0])

        #self.send_msg(dev, 0x41, 0x37, 0, 0, b'\x00\x00')  # 0x37 = 55 Toggle shutter

        self.send_msg(dev, 0x41, 0x3C, 0, 0, b'\x01\x00')  # 0x3c = 60 Set Operation Mode         0x0001  (Run)
        ret8 = self.receive_msg(dev, 0xC1, 0x3D, 0, 0, 2)                                 # 0x3D = 61 Get Operation Mode
        print("8: ", ret8)
        # array('B', [1, 0])

    def read_frame(self, dev):  # Send a read frame request

        self.send_msg(dev, 0x41, 0x53, 0, 0, b'\xC0\x7E\x00\x00')  # 0x53 = 83 Set Start Get Image Transfer

        try:
            data = dev.read(0x81, 0x3F60, 1000)
            data += dev.read(0x81, 0x3F60, 1000)
            data += dev.read(0x81, 0x3F60, 1000)
            data += dev.read(0x81, 0x3F60, 1000)

        except usb.USBError as e:
            print("device error {}".format(e))
            data = None

        return data

    def initialize(self):

        global dev, scl, scl1, scl2

        # Настроить устройство
        dev = self.usbinit()
        self.camerainit(dev)

        # Запустите процедуру обновления образа с определенной задержкой
        #self.UpdateImage(0.001)

    def deinit(self, dev):
        msg = '\x00\x00'
        for i in range(3):
            self.send_msg(dev, 0x41, 0x3C, 0, 0, msg)  # 0x3c = 60  Set Operation Mode 0x0000 (Sleep)

    def saveImage(self, data, name):
        return 0
        with open(os.path.join('/home/dima/PycharmProjects/seek_thermal/image', name), 'wb') as f:
            pickle.dump(data, f)



    def UpdateImage(self, delay, event=None):
        global scl, scl1, dev, status, calImage, label, dc, pal, counter, mode, actnum

        count = 0
        while 1:
            status = 0
            while status != 3:
                #time.sleep(1)

                ret9 = self.read_frame(dev)

                if ret9 is None: continue
                count += 1

                status = ret9[20]
                status1 = ret9[80]
                print(status, status1)

                self.saveImage(ret9, str(count)+"_st_{}".format(status))

                if status == 1:  #получаем калибровочное изображение

                    calimgI = Image.frombytes("F", (208, 156), bytes(ret9), "raw", "F;16")
                    calImagex = Image.frombytes("I", (208, 156), bytes(ret9), "raw", "I;16")

                    im2arr = numpy.asarray(calimgI)

                    im2arr = numpy.where(im2arr < 2000, 2000, im2arr)
                    im2arrF = im2arr.astype('float')
                    im2arrF[0, 40] = 2000
                    im2arrF[:, 206] = numpy.zeros(156)
                    calImage = im2arrF

            try:

                imgx = Image.frombytes("F", (208, 156), bytes(ret9), "raw", "F;16")
                imgy = Image.frombytes("I", (208, 156), bytes(ret9), "raw", "I;16")

                im1arr = numpy.asarray(imgx)
                im1arr = numpy.where(im1arr < 2000, 2000, im1arr)
                im1arrF = im1arr.astype('float')

                im1arrF[0, 40] = 2000
                im1arrF[:, 206] = numpy.zeros(156)

                additionF = (im1arrF) + 600 - (calImage)
                additionF = (im1arrF) - (calImage)

                noiselessF = ndimage.median_filter(additionF, 3)
                minimum = numpy.min(im1arrF)
                maximum = numpy.max(im1arrF)

                print("min", minimum, self.temp_from_raw(minimum))
                print("max", maximum, self.temp_from_raw(maximum))
                #
                print("px1", self.temp_from_raw(maximum))
                print("px2", self.temp_from_raw(maximum))
                #
                for c_i, i in enumerate(im1arrF):
                    for c_j, j in enumerate(i):
                        im1arrF[c_i, c_j] = self.temp_from_raw(j)

                numpy.savetxt("txt"+str(count),im1arrF, delimiter=',')
                bottom = self.scl.get()
                top = self.scl1.get()

                display_min = bottom * 4
                display_max = top * 16
                image8 = noiselessF

                image8.clip(display_min, display_max, out=image8)
                image8 -= display_min
                image8 //= (display_max - display_min + 1) / 256.
                image8 = image8.astype(numpy.uint8)

                noiselessI8 = image8
                pal = 'tillscale'
                conv = colorscale.GrayToRGB(self.palettes[pal])

                cred = numpy.frompyfunc(conv.get_red, 1, 1)
                cgreen = numpy.frompyfunc(conv.get_green, 1, 1)
                cblue = numpy.frompyfunc(conv.get_blue, 1, 1)

                # Convert to a PIL image sized to 640 x 480
                color = numpy.dstack((cred(noiselessI8).astype(noiselessI8.dtype),
                                      cgreen(noiselessI8).astype(noiselessI8.dtype),
                                      cblue(noiselessI8).astype(noiselessI8.dtype)))
                imgCC = Image.fromarray(color).resize((640, 480), Image.ANTIALIAS).transpose(3)


                imgCC.show()
                color = cv2.resize(color, (640, 480))

                cv2.imshow("color_9", color)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            except BaseException as e:
                print("e {}".format(e))
        self.deinit(dev)

    def temp_from_raw(self, x: int):
        # Known measurements (SeekPro):
        # 0C => 273K => 13500 raw (ice)
        # 19C => 292K => 14396 raw (my room temperature)
        # 36C => 309K => 16136 raw (my body temp, more or less)
        # 100C => 373K => 20300 raw (freshely boiled water)
        # 330C => 603K => 32768 raw (known upper limit, full 15 bits - 2^15)

        # All values above perfectly demonstrate linear tendency in Excel.
        # Constants below are taken from linear trend line in Excel.
        # -273 is translation of Kelvin to Celsius
        return (0.0171156038 * x + 37) - 273


if __name__ == '__main__':
    App = Thermal()
    App.initialize()




