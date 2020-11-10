
import numpy
import cv2
class VEVER_TTEPLOVIZOR:

    def convert(self, temperature):
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
        return numpy.array(array)




    def show(self, temperature, DEBUG=False):

        heatmap = numpy.array(temperature)
        mx, i, j = self.test(temperature)

        heatmapshow = None
        heatmapshow = cv2.normalize(heatmap, heatmapshow, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        heatmapshow = cv2.applyColorMap(heatmapshow, cv2.COLORMAP_JET)

        if DEBUG:

            heatmapshow = cv2.circle(heatmapshow, (j, i), 1, (0, 0, 255), 1)
            #heatmapshow = cv2.resize(heatmapshow, (500, 500))
            cv2.imshow("Heatmap", heatmapshow)

            cv2.waitKey()
        return heatmapshow

    def test(self, matrix):
        mx = max(map(max, matrix))

        for i, e in enumerate(matrix):
            try:
                j = e.index(mx)
                break
            except ValueError:
                pass

        print(mx, i, j)
        return mx, i, j

if __name__ == '__main__':



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
#    max_t, max_t_id, min_t, min_t_id = test.get_max_minTemp(temperature)
    # print(max_t, max_t_id, min_t, min_t_id)


    # from .amg88 import amg88
    # teplo = amg88()
    # cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
    # cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    # while True:
    #     try:
    #         temperature = teplo.getMaxrix()
    #     except BaseException as e:
    #         print("Error {}".format(e))
    #         temperature = \
    #             [30.75, 30.25, 29.75, 30.00, 29.00, 28.50, 29.75, 30.25,
    #              29.25, 28.75, 28.50, 29.25, 28.75, 28.50, 29.00, 29.25,
    #              27.25, 27.50, 27.75, 28.25, 28.25, 28.00, 28.50, 29.00,
    #              28.25, 28.25, 28.25, 28.25, 28.25, 28.75, 28.50, 28.00,
    #              27.00, 27.75, 27.75, 28.00, 28.50, 28.75, 28.50, 27.75,
    #              27.25, 28.00, 27.25, 28.00, 27.75, 27.50, 27.00, 29.50,
    #              26.75, 27.00, 26.75, 27.00, 27.50, 26.75, 27.50, 28.00,
    #              26.75, 26.75, 26.50, 25.50, 26.75, 26.75, 26.25, 29.25,
    #              ]
    #
    #     test = VEVER_TTEPLOVIZOR()
    #     image = test.show(temperature)
    #     cv2.imshow("window", image)
    # cv2.waitKey(1)