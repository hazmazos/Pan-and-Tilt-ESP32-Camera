import requests
import numpy as np
import cv2


# GET THE FRAMES
url = "http://esp32cam.local/capture"
response = requests.get(url)

#CHECK THAT IT WORKED
print(response.status_code)
print(len(response.content))    

#TURN FROM BYTES TO BGR ARRAY
array = np.frombuffer(response.content, dtype=np.uint8)
image = cv2.imdecode(array,cv2.IMREAD_COLOR)


#CHECK THAT IT WORKED
print(image.shape)
cv2.imshow("camera",image)
cv2.waitKey(0)


#GRAYSCALE IMAGE
grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imshow("grey", grey)
cv2.waitKey(0)


#Sobel Gradients for edge detection not the best
grad_x = cv2.Sobel(grey,cv2.CV_64F, 1, 0, ksize = 3)
grad_y = cv2.Sobel(grey, cv2.CV_64F, 0, 1, ksize = 3)
magnitude = cv2.magnitude(grad_x.astype(np.float32), grad_y.astype(np.float32))
cv2.imshow("magnitude", magnitude)
cv2.waitKey(0)

#Canny gradients for edge detection - uses 2 thresholds to determine edges
canny = cv2.Canny(grey, 10, 200,)
cv2.imshow("canny",canny)
cv2.waitKey(0)

#Hough transform for line detection. has to use canny Circle method has to use grey
hough_line = image.copy()
lines = cv2.HoughLinesP(canny, 1, np.pi / 180, 50, minLineLength=50, maxLineGap=20)

print(len(lines))

for line in lines:
    x1, y1, x2, y2 = line
    cv2.line(hough_line, (x1,y1), (x2,y2), (0,255,0), 2)

cv2.imshow("hough_line", hough_line)
cv2.waitKey(0)



# Use if random noise
g_blur = cv2.GaussianBlur(grey, (5, 5),0)
cv2.imshow("Gblur", g_blur)
cv2.waitKey(0)


# use if salt and pepper
m_blur = cv2.medianBlur(grey,5)
cv2.imshow("Mblur",m_blur)
cv2.waitKey(0)


#THRESHOLD FILTERED IMAGE
_, threshold = cv2.threshold(m_blur, 80, 255, cv2.THRESH_BINARY_INV)
cv2.imshow("threshold",threshold)
cv2.waitKey(0)

#MORPHOLOGY focuses on white space
kernel = np.ones((5,5), np.uint8)
eroded = cv2.erode(threshold, kernel, iterations=1)
dilated = cv2.dilate(threshold, kernel, iterations=1)

cv2.imshow("eroded",eroded)
cv2.waitKey(0)

cv2.imshow("dilated",dilated)
cv2.waitKey(0)


opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
closing = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel)

cv2.imshow("opening",opening)
cv2.waitKey(0)

cv2.imshow("closing",closing)
cv2.waitKey(0)



#ALL CONTOURS
contours, hiearchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print("there are ", len(contours), " contours")
print("hiearchy is: ", hiearchy)

contour_image = image.copy()

cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 2)

cv2.imshow("contours",contour_image)
cv2.waitKey(0)


#CONTOURS FILTERED BY AREA
filtered_image = image.copy()
areaThreshold = 6000

for index, contour in enumerate(contours):
    area = cv2.contourArea(contour)
    print("contour :", index, " has area ", area)


    if area > areaThreshold:
        cv2.drawContours(filtered_image, [contour], -1, (0, 255, 0), 2)

        #RECTANGLE HAS BASIC WAY OF FINDING CENTRE 
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(filtered_image, (x,y), (x+w,y+h), (0,255,0), 2)
        
        #BETER WAY OF FINDING CENTRE
        M = cv2.moments(contour)

        if M["m00"] != 0:

            cx = M["m10"]/M["m00"]
            cy = M["m01"]/M["m00"]

            cv2.circle(filtered_image, (int (cx),int (cy)), 5, (0, 255, 0), 2)

        #CAN APPROXIMATE SHAPES 
        perimeter = cv2.arcLength(contour, True)
        epsilon = 0.02 * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)
        print("Original points:", len(contour))
        print("Approx points:", len(approx))


cv2.imshow("filtered contours",filtered_image)
cv2.waitKey(0)

cv2.destroyAllWindows