import requests
import numpy as np
import cv2
from ultralytics import YOLO
from flask import Flask, Response
import threading

model = YOLO("yolo26n.pt")

url = "http://esp32cam.local/stream"

##LOOK INTO VS CODE TASK TO LAUNCH BOTH AT SAME TIME 
while True:
    try:
        response = requests.get(url, stream=True, timeout=2)
        print("Connected to ESP32")
        buffer = b""
        chunk = response.iter_content(chunk_size=1024)
        break

    except requests.exceptions.RequestException:
        print("Waiting for ESP32")



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

    jpeg = buffer[soi : eoi + 2]
    array = np.frombuffer(jpeg, np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    image = cv2.flip(image, 0)



    results = model(image, verbose=False)
    result = results[0]

    for box, conf, cls in zip (result.boxes.xyxy, result.boxes.conf, result.boxes.cls):
         

        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(image, (x1,y1), (x2,y2), (0,255,0), 2)

        label = result.names[int(cls)]
        confidence = float (conf)
        text = f"{label} {confidence:.2f}"

        text_y = y1 - 10
        if text_y < 10:
            text_y = y1 + 20 

        cv2.putText(image, text, (x1, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

    success, encoded = cv2.imencode(".jpg", image)
    if success:
        latest_frame = encoded.tobytes()

        with frame_condition:
            new_frame = True
            frame_condition.notify()
        
        

    #cv2.imshow("stream", image)
    buffer = buffer[eoi + 2:]

    #if cv2.waitKey(1) == ord("q"):
        #break


#response.close()
#cv2.destroyAllWindows()