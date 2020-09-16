'''
В классе воспроизведения попробывать исправить if status поставить перед цыклом
'''

import os
import sys
import numpy
from PyQt5 import QtWidgets
from main_form import Ui_MainWindow
from app_thermometer.moduls.camera import VideoCamera

from PyQt5.QtCore import QSize, Qt, pyqtSignal, QThread
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
import cv2

import qimage2ndarray

class display(QThread):
    '''
    Для потокового отображения изображений на экране
    '''
    signal_frame_RGB = pyqtSignal(QPixmap, tuple)

    def __init__(self):
        QThread.__init__(self)

        #self.camera = VideoCamera(os.path.join(os.path.abspath(os.getcwd()), 'app_thermometer/rc/haarcascade_frontalface_default.xml'))
        #self.camera.start()
        self.video = cv2.VideoCapture(0)
        self.face_detector = cv2.CascadeClassifier(os.path.join(os.path.abspath(os.getcwd()), 'app_thermometer/rc/haarcascade_frontalface_default.xml'))



    def getFace(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(gray, 1.3, 5)

        return tuple(faces)


    def __converterNumpyAraayToPixMap(self, NumpyArray):
        '''
        Конвертирует Numpy массив в PixMap
        :param NumpyArray:
        :return:
        '''
        try:
            pixMapArray = QPixmap.fromImage(qimage2ndarray.array2qimage(NumpyArray))
            return pixMapArray
        except ValueError:
            print("error")
            return None

    def run(self):
        while True:
            success, frame = self.video.read()
            if not success is None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                bbox = self.getFace(frame)
                for (x, y, w, h) in bbox:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                frame = self.__converterNumpyAraayToPixMap(frame)
                self.signal_frame_RGB.emit(frame, bbox)

    # def run(self):
    #     while True:
    #         for frame_rgb, bbox in self.camera.generator_frame():
    #
    #             frame_rgb = self.__converterNumpyAraayToPixMap(frame_rgb)
    #             if not frame_rgb is None:
    #                 if not bbox is None:
    #                     self.signal_frame_RGB.emit(frame_rgb, bbox)

class controller():

    def __init__(self):
        self._app = QtWidgets.QApplication(sys.argv)
        self._view = mainForm()
        self.display_obj = display()
        self.display_obj.signal_frame_RGB.connect(self._view.showGraphicsViewRGB)
        self.display_obj.start()
        #self._view.showFullScreen()



    def run(self):
        '''
        Запускает приложение
        :return:
        '''
        self._view.show()
        return self._app.exec_()



class mainForm(QtWidgets.QMainWindow, Ui_MainWindow):

    search_button = pyqtSignal()
    signal_FrameRGB = pyqtSignal(numpy.ndarray)
    signal_run_video = pyqtSignal(bool)
    signal_form_save = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.graphicsView.fitInView(False)


    def showGraphicsViewRGB(self, pixMap, bbox):
        '''
        Позывать изображения на форме RGB
        :param pixMap:
        :param dic_info:
        :return:
        '''
        # [347 181 197 197]
        print(bbox)
        #left, -top, width, abs(height)
        # if len(bbox) == 0:
        #
        #     self.rec = self.ui.graphicsView._scene.addRect(QtCore.QRectF(0.0, 0.0, 400.0, 100.0),
        #                          pen=QtGui.QPen(QtCore.Qt.blue, 3),
        #                          brush=QtGui.QBrush(QtCore.Qt.green))


        self.ui.graphicsView.setPhoto(pixMap)



def main():

    controll = controller()
    controll.run()

if __name__ == '__main__':
    sys.exit(main())