import requests
import cv2
import numpy as np
import time 

url = "http://esp32cam.local/capture"


def getTwoFrames():
    for i in range (2):
        response = requests.get(url)
        array = np.frombuffer(response.content, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)

        cv2.imwrite(f"frame{i}.jpeg",image)
        cv2.imshow("frame", image)
        cv2.waitKey(1)
    cv2.destroyAllWindows()

#Sparse optical flow 
def sparceOpticalFlow():
    motion1 = cv2.imread("frame0.jpeg")
    motion2 = cv2.imread("frame1.jpeg")

    motion = [motion1, motion2]
    proc_motion = []

    for frame in motion:
        proc_motion.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

    image_corner = motion2.copy()
    corners = cv2.goodFeaturesToTrack(proc_motion[0], maxCorners=100, qualityLevel=0.1, minDistance=10)
    next_points, status, error  = cv2.calcOpticalFlowPyrLK(proc_motion[0], proc_motion[1], corners, None)

    old = corners[status == 1 ]
    new = next_points[status == 1]

    for old_point, new_point in zip(old,new):
        x0,y0 = old_point.ravel()
        x1,y1 = new_point.ravel()

        cv2.circle(image_corner, (int (x1), int (y1)), 3, (0,255,0), 2)
        cv2.line(image_corner, (int (x0), int (y0)), (int (x1), int (y1)), (0,255,0), 2)

    cv2.imshow("motion_tracked", image_corner)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


#BACKSUB METHOD 
def backSub():
    backSub = cv2.createBackgroundSubtractorMOG2()

    while True:

        response = requests.get(url)

        array = np.frombuffer(response.content, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)

        mask = backSub.apply(image)

        cv2.imshow("Foreground", mask)  

        if cv2.waitKey(1) == ord("q"):
            break

    cv2.destroyAllWindows()

    
# Works by subtracing 2 frames and marking their differences - shows whats changed which can be motion but also noise
def simpleBackSub():



    frame1 = cv2.imread("frame0.jpeg")
    frame2 = cv2.imread("frame1.jpeg")


    frames = [frame1, frame2]
    processed_frames = []



    for index,frame in enumerate(frames):
        grey = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

        cv2.imshow("grey", grey)
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