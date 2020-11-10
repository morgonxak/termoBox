import cv2
import numpy

cap = cv2.VideoCapture(0)
cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN) 
cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    ret, img = cap.read()
    img = cv2.flip(img,1) # ореентация камеры
    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE) 
    print(img.shape)
    cv2.imshow("window", img)

    key = cv2.waitKey(10)
    if key == 27:
        break

cv2.destroyAllWindows() 
cv2.VideoCapture(0).release()

