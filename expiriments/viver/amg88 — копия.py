import time
import busio
import board
import adafruit_amg88xx
import numpy

class amg88:
    def __init__(self):

        i2c = busio.I2C(board.SCL, board.SDA)
        try:
            self.amg = adafruit_amg88xx.AMG88XX(i2c, addr=0x69)
        except BaseException as e:
            print("Error 69 adress")
            self.amg = adafruit_amg88xx.AMG88XX(i2c, addr=0x68)

    def getMaxrix(self):
        '''
        Получает матрицу с непересчитанными температурами
        :return:
        '''
        return self.amg.pixels

    def getMatrix_recalc(self):
        '''
        Пересчитываем всю матрицу с температурами
        :return:
        '''
        matrix_temp = numpy.copy(self.getMaxrix())

        for row_count,  row in enumerate(matrix_temp):
            for col_count,  temp in enumerate(row):
                matrix_temp[row_count, col_count] = self.recalculation_of_temperatures(temp)

        return matrix_temp

    def recalculation_of_temperatures(self, temp):
        '''
        пересчет температур
        :param temp:
        :return:
        '''
        if temp <= 32.5:
            temp = temp + 4.3 + abs(32.5 - temp) / 1.23076923
        else:
            temp = temp + 4.3
        return temp

    def getMaxTemp(self):
        '''
        получить максимальную температуру
        :return:
        '''
        matrix = self.getMaxrix()
        temp = numpy.max(matrix)
        return temp, round(self.recalculation_of_temperatures(temp), 1)
        
    def test_2(self):
        while True:
            a,s = self.getMaxTemp()
            print(a)
            print(s)
            print("\n")
            time.sleep(1)
            
    def test_1(self):
        '''

        :return:
        '''

        while True:
            for row in self.getMatrix_recalc():
                print(["{0:.1f}".format(temp) for temp in row])
            print("\n")
            time.sleep(1)
            

if __name__ == '__main__':
    test = amg88()
    test.test_2()
