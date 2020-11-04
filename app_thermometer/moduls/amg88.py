import time
import busio
import board
import adafruit_amg88xx
import numpy

class amg88:
    def __init__(self, address=0x68):
        #print(busio.I2C(board.SCL, board.SDA))
        self.i2c = busio.I2C(board.SCL, board.SDA) #address #
        #print(" {}".format(self.i2c==address))
        try:
            self.amg = adafruit_amg88xx.AMG88XX(self.i2c)
            #print("amg88.__init__(0x69)")
        except:
            print("error amg88.__init__(0x69)")
            try:
                self.amg = adafruit_amg88xx.AMG88XX(self.i2c, addr=address)
                #print("amg88.__init__(0x68)")

            except:
                print("error amg88.__init__(0x68)")

    def getMaxrix(self):
        '''
        Получает матрицу с непересчитанными температурами
        :return:
        '''
        
        #print("getMaxrix")
        #print(self.amg)
        #print(self.amg.begin())
        #print("11111")
        
        return self.amg.pixels
        
    def getreturnMaxrix(self):
        
        #print("getreturnMaxrix")
        return numpy.copy(self.getMaxrix())
    def getMatrix_recalc(self):
        '''
        Пересчитываем всю матрицу с температурами
        :return:
        '''
        #print("getMatrix_recalc")
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
        #print("recalculation_of_temperatures1")
        if temp <= 32.5:
            temp = temp + 4.3 + abs(32.5 - temp) / 1.23076923
        else:
            temp = temp + 4.3
        #print("recalculation_of_temperatures2")
        return temp

    def getMaxTemp(self):
        '''
        получить максимальную температуру
        :return:
        '''
        #print("getMaxTemp1")
        matrix = self.getMaxrix()
        #print("getMaxTemp2")
        temp = numpy.max(matrix)
        #print("getMaxTemp3")
        """
        print(matrix)
        print("_________________")
        print(temp)
        print("\n")
        """
        return temp, round(self.recalculation_of_temperatures(temp), 1)
        
    def test_2(self):
        #print("test_2")
        while True:
            print(self.getreturnMaxrix())
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
    #print("11111111111111111")
    test.test_2()
