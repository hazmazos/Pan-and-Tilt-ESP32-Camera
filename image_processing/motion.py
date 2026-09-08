import requests
import cv2
import numpy as np
import time 

url = "http://esp32cam.local/capture"


    

# Works by subtracing 2 frames and marking their differences - shows whats changed which can be motion but also noise

for i in range (2):

    print("frame ",i)
    response = requests.get(url)

    array = np.frombuffer(response.content, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)

    cv2.imwrite(f"frame{i}.jpeg",image)
    cv2.imshow("frame", image)
    cv2.waitKey(3)



frame1 = cv2.imread("frame0.jpeg")
frame2 = cv2.imread("frame1.jpeg")


frames = [frame1, frame2]
processed_frames = []



for index,frame in enumerate(frames):
    grey = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    cv2.imshow("thresh", grey)
    cv2.waitKey(0)
    processed_frames.append(grey)


difference = cv2.absdiff(processed_frames[0],processed_frames[1])
cv2.imshow("diff",difference)
cv2.waitKey(0)

g_blur = cv2.GaussianBlur(difference,(3,3),0)
_, thresh = cv2.threshold(g_blur,30,255,cv2.THRESH_BINARY)
cv2.imshow("thresh",thresh)
cv2.waitKey(0)

kernel = np.ones((5,5), np.uint8)
closed = cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,kernel)
cv2.imshow("closed",closed)
cv2.waitKey(0)

contours, hiearchy = cv2.findContours(closed,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
print(len(contours))

output = frame2.copy()

area_thresh = 200
for contour in contours:
    area = cv2.contourArea(contour)
    if area >= area_thresh:
        cv2.drawContours(output,[contour], -1, (0,255,0), 2)

cv2.imshow("output",output)
cv2.waitKey(0)


cv2.destroyAllWindows()
