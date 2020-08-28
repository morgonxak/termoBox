import subprocess
import cv2

path_LCD = r'./home/pi/project/libseek-thermal/build/examples/seek_test'
p = subprocess.Popen("{}".format(path_LCD), shell=True, stdout=subprocess.PIPE)
while 1:
    print("t= ",p.stdout.read())
