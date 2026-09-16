import requests
import numpy as np
import cv2
import http.client
import threading 
import time
from flask import Flask, Response


pan_angle = 90
tilt_angle = 90

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
conn = http.client.HTTPConnection(ESP32_IP,80, timeout=1)

stop_event = threading.Event()
servo_thread = threading.Thread(target=servo_control,daemon=False)
servo_thread.start()

app = Flask(__name__)
latest_frame = None
new_frame = False
frame_condition = threading.Condition()

def generate():

    global latest_frame, new_frame
    
    
    while True:
        with frame_condition:
            while not new_frame:
                frame_condition.wait()

            frame = latest_frame
            new_frame = False            
            yield(
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + str(len(frame)).encode() + b"\r\n\r\n" +
                latest_frame +
                b"\r\n"
            )

@app.route("/stream")
def stream():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8000, threaded=True),daemon=True).start()


kalman = cv2.KalmanFilter(4, 2)

kalman.transitionMatrix = np.array([
    [1, 0, 1, 0],
    [0, 1, 0, 1],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
], dtype=np.float32)

kalman.measurementMatrix = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0]
], dtype=np.float32)

kalman.processNoiseCov = np.array([
    [4, 1, 0, 0],
    [1, 4, 0, 0],
    [0, 0, 5, 1],
    [0, 0, 1, 5]
], dtype=np.float32)

kalman.measurementNoiseCov = np.array([
    [4, 1],
    [1, 4]
], dtype=np.float32)

kalman.errorCovPost = np.array([
    [2, 1, 0.75, 0.5],
    [1, 2, 0.5, 0.75],
    [0.75, 0.5, 2, 0.5],
    [0.5, 0.75, 0.5, 2]
], dtype=np.float32)


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

            ball_found = True     
            cv2.drawContours(image, [largest_contour], -1, (0,0,255), 2)

            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = M["m10"]/M["m00"]
                cy = M["m01"]/M["m00"]
                cv2.circle(image, (int (cx), int (cy)), 3, (0,0,255), 2)
                

                height, width = image.shape[:2]
                centre_x = int (width/2)
                centre_y = int (height/2)

                prediction = kalman.predict()

                measurement = np.array([
                    [cx],
                    [cy]
                ], dtype=np.float32)

                x = kalman.correct(measurement)


                err_x = centre_x - x[0,0]
                err_y = centre_y - x[1,0]

                kp_pan = 0.027
                kd_pan = 0.014

                kp_tilt = 0.015
                kd_tilt = 0.014

                deadband = 7

                pan_step = kp_pan * err_x - kd_pan * x[2,0]
                tilt_step = kp_tilt * err_y - kd_tilt * x[3,0]
                pan_step = np.clip(pan_step, -3, 3)
                tilt_step = np.clip(tilt_step, -3, 3)

                if abs(err_x) > deadband:
                    pan_angle = int(np.clip(pan_angle + pan_step, 0, 180))

                if abs(err_y) > deadband:
                    tilt_angle = int(np.clip(tilt_angle - tilt_step, 0, 180))

                

    success, encoded = cv2.imencode(".jpg", image)
    if success:
        latest_frame = encoded.tobytes()

        with frame_condition:
            new_frame = True
            frame_condition.notify()


    if cv2.waitKey(1) == ord("q"):
        stop_event.set()
        break

response.close()
servo_thread.join()
cv2.destroyAllWindows()