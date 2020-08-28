import subprocess
#from app_thermometer import app
path_LCD = r'/home/pi/project/seek_thermal/app_thermometer/rc/LCD.out'


def init():
    path_LCD = r'/home/pi/project/seek_thermal/app_thermometer/rc/LCD.out'
    p = subprocess.Popen("{} s".format(path_LCD), shell=True, stdout=subprocess.PIPE)


def pull_lcd(termal1, termal2, line_2=None):
    path_LCD = r'/home/pi/project/seek_thermal/app_thermometer/rc/LCD.out'
    if not line_2 is None:
        p = subprocess.Popen("{} {} {} {}".format(path_LCD, termal1, termal2, line_2), shell=True, stdout=subprocess.PIPE)
    else:
        p = subprocess.Popen("{} {} {}".format(path_LCD, termal1, termal2), shell=True, stdout=subprocess.PIPE)

if __name__ == '__main__':
    import time
    init()
    pull_lcd(36.6,36.7,"привет")
    time.sleep(1)
    pull_lcd(36.7,36.7,"привет")
    time.sleep(1)
    pull_lcd(36.7,36.8,"привет")
    time.sleep(1)
    pull_lcd(36.8,36.8,"привет")
    time.sleep(1)