import cv2
import numpy
#1280x720
#cv.CAP_PROP_GAIN - увеличения
#cv.CAP_PROP_MODE


cap = cv2.VideoCapture(0)

cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 60)

width = cap.get(cv2.cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.cv2.CAP_PROP_FRAME_HEIGHT)

print(width, height)

while True:
    ret, img = cap.read()
    if ret:
        img = cv2.resize(img, None, fx=0.5,fy=0.5)
        img = cv2.flip(img, 1) # ореентация камеры
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        print(img.shape)
        cv2.imshow("window", img)

    key = cv2.waitKey(10)
    if key == 27:
        break

cv2.destroyAllWindows() 
cv2.VideoCapture(0).release()

