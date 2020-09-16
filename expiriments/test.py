# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui
import sys
import os
from app_thermometer.moduls.camera import VideoCamera

camera = VideoCamera(os.path.join(os.path.abspath(os.getcwd()), 'app_thermometer/rc/haarcascade_frontalface_default.xml'))
camera.run()

app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QWidget()
window.setWindowTitle("GraphicsScene")
window.resize(600, 400)

scene = QtWidgets.QGraphicsScene(0.0, 0.0, 500.0, 335.0)
scene.setBackgroundBrush(QtCore.Qt.white)
scene.setStickyFocus(True)




view = QtWidgets.QGraphicsView(scene)


box = QtWidgets.QVBoxLayout()
box.addWidget(view)
window.setLayout(box)

window.show()
sys.exit(app.exec_())