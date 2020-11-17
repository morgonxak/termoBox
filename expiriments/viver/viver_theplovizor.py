
import numpy
import cv2
import time
from amg88 import amg88
class VEVER_TTEPLOVIZOR:

    def convert(self, temperature):
        #print("convert 1")
        array = []
        temp = []
        id = 0
        for count, i in enumerate(temperature):
            if id == 8:
                array.append(temp)
                temp = []
                id = 0
            else:
                id = id + 1
                temp.append(i)
        #print("convert 2")
        return numpy.array(array)




    def show(self, temperature, DEBUG=False):
        #print("show 1")

        heatmap = numpy.array(temperature)
        #mx = max(map(max, temperature))
        if_ = True
        try:
            mx, i, j = self.test(temperature)
        except :
            if_ =False
            pass  
            
        #i,j = numpy.unravel_index(heatmap.armax(), heatmap.share)
        heatmapshow = None
        heatmapshow = cv2.normalize(heatmap, heatmapshow, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        heatmapshow = cv2.applyColorMap(heatmapshow, cv2.COLORMAP_JET)
        if if_:
            color_green = (0, 255, 0) 
            cv2.rectangle(heatmapshow, (j, i), (j, i), color_green, 1)#вывод квадр
            #cv2.putText(heatmapshow, mx, (i, j), cv2.FONT_HERSHEY_COMPLEX,0.1, color_green, 4, 2)
        if DEBUG:
            

            heatmapshow = cv2.circle(heatmapshow, (j, i), 1, (0, 0, 255), 1)
            #heatmapshow = cv2.resize(heatmapshow, (500, 500))
            cv2.imshow("Heatmap", heatmapshow)

            cv2.waitKey()
            
        #print("show 2")
        #print(mx)
        print("________________")
        return heatmapshow

    def test(self, matrix):
        try:
            mx = max(map(max, matrix))
            #mx = max(matrix)
            for i, e in enumerate(matrix):
                try:
                    j = e.index(mx)
                    break
                except ValueError:
                    pass

            
        except ValueError:
            pass  
        print(mx, i, j)  
        return mx, i, j
        
if __name__ == '__main__':

    """

    temperature = \
                [[30.75, 30.25, 29.75, 30.00, 29.00, 28.50, 29.75, 30.25],
                 [29.25, 28.75, 28.50, 29.25, 28.75, 28.50, 29.00, 29.25],
                 [27.25, 27.50, 27.75, 28.25, 28.25, 28.00, 28.50, 29.00],
                 [28.25, 28.25, 28.25, 28.25, 28.25, 28.75, 28.50, 28.00],
                 [27.00, 27.75, 27.75, 31.00, 28.50, 28.75, 28.50, 27.75],
                 [27.25, 28.00, 31.25, 28.00, 27.75, 27.50, 27.00, 29.50],
                 [26.75, 27.00, 26.75, 27.00, 27.50, 26.75, 27.50, 28.00],
                 [26.75, 26.75, 26.50, 25.50, 26.75, 26.75, 26.25, 29.25]
                 ]

    test = VEVER_TTEPLOVIZOR()
    test.show(temperature, True)
    #max_t, max_t_id, min_t, min_t_id = test.get_max_minTemp(temperature)
    #print(max_t, max_t_id, min_t, min_t_id)
    """

    
    teplo = amg88()
    cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    t_if = 0
    Active = True
    while Active:
        if time.time() - t_if >= 0.5:
            t_if = time.time()
            try:
                temperature = teplo.getMaxrix()
            except BaseException as e:
                print("Error {}".format(e))
                temperature = \
                    [30.75, 30.25, 29.75, 30.00, 29.00, 28.50, 29.75, 30.25,
                    29.25, 28.75, 28.50, 29.25, 28.75, 28.50, 29.00, 29.25,
                    27.25, 27.50, 27.75, 28.25, 28.25, 28.00, 28.50, 29.00,
                    28.25, 28.25, 28.25, 28.25, 28.25, 28.75, 28.50, 28.00,
                    27.00, 27.75, 27.75, 28.00, 28.50, 28.75, 28.50, 27.75,
                    27.25, 28.00, 27.25, 28.00, 27.75, 27.50, 27.00, 29.50,
                    26.75, 27.00, 26.75, 27.00, 27.50, 26.75, 27.50, 28.00,
                    26.75, 26.75, 26.50, 25.50, 26.75, 26.75, 26.25, 29.25,
                    ]

            test = VEVER_TTEPLOVIZOR()
            image = test.show(temperature)
            image = cv2.flip(image, 1)  # ореентация камеры переворот вокруг оси y
            cv2.imshow("window", image)
            
            if cv2.waitKey(33) & 0xFF == ord('q') :
                Active = False
                #break