import requests
import numpy as np
import cv2
import http.client
import threading 
import time

pan_angle = 90
tilt_angle = 90

ESP32_IP = ""
conn = http.client.HTTPConnection(ESP32_IP,80, timeout=1)

url = "http://esp32cam.local/stream"

stop_event = threading.Event()

def servo_control():
    

    while not stop_event.is_set():

        conn.request("GET", f"/pan?angle={pan_angle}")
        response = conn.getresponse()
        response.read()

        conn.request("GET", f"/tilt?angle={tilt_angle}")
        response = conn.getresponse()
        response.read()

        time.sleep(0.1)

servo_thread = threading.Thread(target=servo_control,daemon=False)
servo_thread.start()

def getPixel(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"hsv value is: {param[y,x]}")

while True:
    try:
        response = requests.get(url, stream=True, timeout=2)
        print("Connected to ESP32")
        buffer = b""
        chunk = response.iter_content(chunk_size=1024)
        break

    except requests.exceptions.RequestException:
        print("Waiting for ESP32")

while True:

    while b"\xff\xd8" not in buffer:
        buffer += next(chunk)
    soi = buffer.find(b"\xff\xd8")

    while b"\xff\xd9" not in buffer[soi + 2:]:
        buffer += next(chunk) 
    eoi = buffer.find(b"\xff\xd9", soi + 2)

    if eoi < soi:
        buffer = buffer[eoi + 2:]
        continue

    jpeg = buffer[soi:eoi + 2]
    buffer = buffer[eoi + 2:]

    array = np.frombuffer(jpeg, np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    image = cv2.flip(image,0)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #cv2.namedWindow("HSV")
    #cv2.setMouseCallback("HSV", getPixel, hsv)

    #cv2.imshow("HSV", image)
    #if cv2.waitKey(1) == ord("q"):
        #continue

    H1 = 50
    H2 = 80

    S1 = 50
    S2 = 130

    V1 = 90
    V2 = 230

    lower = np.array([H1,S1,V1])
    upper = np.array([H2,S2,V2])

    
    mask = cv2.inRange(hsv, lower, upper)
    #cv2.imshow("Mask", mask)

    area_thesh = 1000
    contours, hiearchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_contour) >= area_thesh:     
            cv2.drawContours(image, [largest_contour], -1, (0,0,255), 2)

            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = M["m10"]/M["m00"]
                cy = M["m01"]/M["m00"]
                cv2.circle(image, (int (cx), int (cy)), 3, (0,0,255), 2)
                

                height, width = image.shape[:2]
                centre_x = int (width/2)
                centre_y = int (height/2)

                err_x = centre_x - cx
                err_y = centre_y - cy

                inside = cv2.pointPolygonTest(largest_contour, (centre_x, centre_y), False)
                if inside >= 0:
                    print("centred")

                else:
                    print("not centred")
                    if err_x > 0:
                        pan_angle +=1
                    elif err_x < 0:
                        pan_angle -=1

                    pan_angle = max(0, min(180, pan_angle))

                    if err_y > 0:
                        tilt_angle -=1
                    elif err_y < 0:
                        tilt_angle +=1

                    tilt_angle = max(0, min(180, tilt_angle))


            '''
            
            x = np.array([[cx],[cy],[0],[0]], dtype=float)
            P = None

            A = np.array([[1,0,1,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]], dtype=float)
            R = None

            H = np.array([[1,0,0,0],[0,1,0,0]], dtype=float)
            Q = None
            '''
    cv2.imshow("Stream", image)
    if cv2.waitKey(1) == ord("q"):
        stop_event.set()
        break

response.close()
servo_thread.join()
cv2.destroyAllWindows()