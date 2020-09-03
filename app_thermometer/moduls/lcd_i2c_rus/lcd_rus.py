'''
LCD.out [param] [data]
params:
    i - init (no data)
    c - clear (no data)
    t - text [line 0 || 1] [word_1] [word_n]
    l - temp_left [temp]
    r - temp_right [temp]
'''
import subprocess
#from app_thermometer import app
path_LCD = r'/home/pi/project/seek_thermal/app_thermometer/rc/LCD.out'


def init():
    '''
    Инициалицация дисплея
    :return:
    '''
    p = subprocess.Popen("{} i".format(path_LCD), shell=True, stdout=subprocess.PIPE)
    print("{} i".format(path_LCD))

def pull_lcd_text(line, data):
    '''
    Отправить данные на экран на определенную строку
    :param line: или 0 или 1 выбор строки
    :param data:
    :return:
    '''
    p = subprocess.Popen("{} t {} {}".format(path_LCD, line, data), shell=True, stdout=subprocess.PIPE)
    #print("{} t {} {}".format(path_LCD, line, data))


def pull_lcd_l(data):
    '''
    ЛЕвая температура
    :param data:
    :return:
    '''
    p = subprocess.Popen("{} l {}".format(path_LCD, data), shell=True, stdout=subprocess.PIPE)
    #print("{} l {}".format(path_LCD, data))

def pull_lcd_r(data):
    '''
    Правая температура
    :param data:
    :return:
    '''
    p = subprocess.Popen("{} r {}".format(path_LCD, data), shell=True, stdout=subprocess.PIPE)
    #print("{} r {}".format(path_LCD, data))

def clear():
    '''
    Отчистить LCD
    :return:
    '''
    p = subprocess.Popen("{} c".format(path_LCD), shell=True, stdout=subprocess.PIPE)
    #print("{} c".format(path_LCD))

if __name__ == '__main__':
    import time
    t = 0.1
    init()
    while True:
        time.sleep(t)
        pull_lcd_text('0', 'hello')
        time.sleep(t)
        pull_lcd_text('0', 'ok')
        time.sleep(t)
        pull_lcd_l('36.6')
        time.sleep(t)
        pull_lcd_r('')
        pull_lcd_text('1', 'no')
        time.sleep(t)
        pull_lcd_l('36.6')
        time.sleep(t)
        pull_lcd_r('36.9')
        time.sleep(t)
        pull_lcd_text('1', 'nax')
        time.sleep(t)
        clear()