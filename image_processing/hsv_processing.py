import requests
import cv2
import numpy as np

url = "http://esp32cam.local/capture"

response = requests.get(url)

array = np.frombuffer(response.content, dtype=np.uint8)

image = cv2.imdecode(array, cv2.IMREAD_COLOR)

#Click to get HSV values
def getPixel(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("position is: ", x, y)
        print("hsv value is: ", param[y,x])

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

cv2.namedWindow("camera")
cv2.setMouseCallback("camera", getPixel, hsv)
cv2.imshow("camera",image)
cv2.waitKey(0)

H1 = 0
S1 = 30
V1 = 47

H2 = 80
S2 = 90
V2 = 160

lower = np.array([H1,S1,V1])
upper = np.array([H2,S2,V2])

#COLOR BASED MASK
mask = cv2.inRange(hsv,lower,upper)
cv2.imshow("mask", mask)
cv2.waitKey(0)

contours, hiearchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

contour_image = image.copy()
filtered_contour = image.copy()
hull_image = image.copy()

cv2.drawContours(contour_image, contours, -1, (0,255,0), 2)
cv2.imshow("all_contours", contour_image)
cv2.waitKey(0)

area_threshold = 2000
for index, contour in enumerate(contours):
    area = cv2.contourArea(contour)

    

    if area >= area_threshold:
        perimeter = cv2.arcLength(contour, True)

        cv2.drawContours(filtered_contour, [contour], -1, (0,255,0), 2)
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(filtered_contour, (x, y), (x+w, y+h), (0,255,0), 2)

        #SIMPLE WAYS TO DISTINGUISH OBJECTS
        aspect_ratio = w / h
        print("Object ", index, "has ratio of ", aspect_ratio)
        circularity = 4 * np.pi * area / perimeter **2
        print("Object ", index, "has circularity of ", circularity)
        hull = cv2.convexHull(contour)
        cv2.drawContours(hull_image, [hull], -1, (0,255,0), 2 )

        




        M = cv2.moments(contour)

        if M["m00"] != 0:
            cx = M["m10"] / M["m00"]
            cy = M["m01"] / M["m00"]

        cv2.circle(filtered_contour,(int (cx), int (cy)), 5, (0,255,0), 2)

cv2.imshow("hull_image", hull_image)
cv2.waitKey(0)

cv2.imshow("filtered_contours", filtered_contour)
cv2.waitKey(0)

cv2.destroyAllWindows()


