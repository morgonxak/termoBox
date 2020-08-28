import pipes
import tempfile
import os
import sys
import cv2
import numpy

path_pipe = r'/home/dima/packet_install/libseek-thermal/build/examples/pipe_test'

fifo = open(path_pipe, "r")
print("OK")
print(fifo)
frame = []
count = 0
while 1:

    for line in fifo:
        if count == 154:
            count = 0
            print("*" * 50)
            print(frame)
            print("*" * 50)

            im1arr_F = numpy.asarray(frame)
            im1arr_F = numpy.uint8(im1arr_F)
            cv2.imshow("test", im1arr_F)
            frame.clear()
        else:
            count += 1

            resize_line = line.replace("[", "")
            resize_line = resize_line.replace("]", "")
            resize_line = resize_line.replace("\n", "")
            resize_line = resize_line.replace(";", "")
            resize_line = resize_line.split(",")


            for c_i, i in enumerate(resize_line):
                try:
                    resize_line[c_i] = int(i)
                except BaseException as e:
                    print("error {}".format(e))

            frame.append(resize_line)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

fifo.close()

