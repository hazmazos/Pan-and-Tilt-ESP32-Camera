import requests
import numpy as np
import cv2
import http.client
import threading 
import time




def getPixel(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"hsv value is: {param[y,x]}")
def servo_control():
    while not stop_event.is_set():

        conn.request("GET", f"/servo?pan={pan_angle}&tilt={tilt_angle}")
        response = conn.getresponse()
        response.read()

        time.sleep(0.05)

url = "http://esp32cam.local/stream"
ESP32_IP = ""

pan_angle = 90
tilt_angle = 90


x = None
P = np.array([[2,1,0.75,0.5],[1,2,0.5,0.75],[0.75,0.5,2,0.5],[0.5,0.75,0.5,2]], dtype=np.float32)

A = np.array([[1,0,1,0],[0,1,0,1],[0,0,1,0],[0,0,0,1]], dtype=np.float32)
Q = np.array([[4,1,0,0],[1,4,0,0],[0,0,5,1],[0,0,1,5]], dtype=np.float32)

H = np.array([[1,0,0,0],[0,1,0,0]], dtype=np.float32)
R = np.array([[4,1],[1,4]], dtype=np.float32)
 

initialised_state = False
ball_found = False


conn = http.client.HTTPConnection(ESP32_IP,80, timeout=1)

stop_event = threading.Event()
servo_thread = threading.Thread(target=servo_control,daemon=False)
servo_thread.start()


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

        ## ball found
        if cv2.contourArea(largest_contour) >= area_thesh:     

            ball_found = True
            cv2.drawContours(image, [largest_contour], -1, (0,0,255), 2)

            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = M["m10"]/M["m00"]
                cy = M["m01"]/M["m00"]
                cv2.circle(image, (int (cx), int (cy)), 3, (0,0,255), 2)

                # ball found for first time
                if not initialised_state:
                    x = np.array([[cx],[cy],[0],[0]], dtype=np.float32)
                    initialised_state = True

                x_pred = A @ x
                P_pred = A @ P @ A.T + Q

                z = np.array([[cx],[cy]], dtype=np.float32)
                y = z - H @ x_pred

                K = P_pred @ H.T @ np.linalg.inv(H @ P_pred @ H.T + R)
                x = x_pred + K @ y

                P = (np.eye(4) - K@H) @ P_pred

                height, width = image.shape[:2]
                centre_x = int (width/2)
                centre_y = int (height/2)

                err_x = centre_x - x[0,0]
                err_y = centre_y - x[1,0]

                pan_step =int (np.clip(0.1 * err_x, -3, 3))
                tilt_step =int (np.clip(0.1 * err_y, -3, 3))

                pan_angle += pan_step

                print(pan_angle)
                

        # we diddn't find the ball
        else:
            ball_found = False
            # but we fouind it before so now lost

            if initialised_state:
                pred_limit = 20
                ## predict up to 20 frames then what??

                # now need to not measure but just predict
    cv2.imshow("Stream", image)
    if cv2.waitKey(1) == ord("q"):
        stop_event.set()
        break

response.close()
servo_thread.join()
cv2.destroyAllWindows()