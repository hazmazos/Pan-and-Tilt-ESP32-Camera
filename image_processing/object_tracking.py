import requests
import numpy as np
import cv2

url = "http://esp32cam.local/stream"

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

    
    contours, hiearchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)     
        cv2.drawContours(image, [largest_contour], -1, (0,0,255), 2)

        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = M["m10"]/M["m00"]
            cy = M["m01"]/M["m00"]
            cv2.circle(image, (int (cx), int (cy)), 3, (0,0,255), 2)

            measurement = np.array([cx,cy], dtype=np.float32)

    cv2.imshow("Stream", image)
    if cv2.waitKey(1) == ord("q"):
        break

cv2.destroyAllWindows()