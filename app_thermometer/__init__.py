# from flask import Flask
# import os
# try:
#     from smbus2 import SMBus
# except BaseException as e:
#     print("Error {}".format(e))
#
#
# app = Flask(__name__, static_url_path='/static')
#
# from app_thermometer.moduls.lcd_i2c_rus import lcd_rus
# from app_thermometer.moduls.measurements.mlx90614 import MLX90614
# from app_thermometer.moduls.camera import VideoCamera
# from app_thermometer.processing import processing
#
#
# pathClassificator_raspberry = r'/home/pi/project/seek_thermal/app_thermometer/rc/haarcascade_frontalface_default.xml'
# if os.path.isfile(pathClassificator_raspberry):
#     app.config['path_CascadeClassifier'] = pathClassificator_raspberry
# else:
#     app.config['path_CascadeClassifier'] = r'/home/dima/PycharmProjects/seek_thermal/app_thermometer/rc/haarcascade_frontalface_default.xml'
#
# try:
#     app.config['LCD'] = lcd_rus.init()
# except BaseException as e:
#     print("Error {}".format(e))
#     app.config['LCD'] = None
#
# #Запускаем термодатчик
# try:
#     bus = SMBus(1)
#     app.config['termo'] = MLX90614(bus)
#
# except BaseException as e:
#     print("Error {}".format(e))
#     app.config['termo'] = None
#
# #*************************************
# #
#
#
#
# app.config['camera_IR'] = None
# #
# app.config['camera_RGB'] = VideoCamera(app.config['path_CascadeClassifier'], app.config['camera_IR'], app.config['termo'])
# app.config['camera_RGB'].init()
# app.config['camera_RGB'].start()
# #
# app.config['processing'] = processing(app.config['LCD'], app.config['termo'], app.config['camera_RGB'], app.config['camera_IR'], app.config['path_CascadeClassifier'])
# app.config['processing'].start()
#
# from app_thermometer import routers
#
#
#
