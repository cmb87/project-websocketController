import os
import base64
import numpy as np
import websocket
import cv2
import time


iw,ih = 320,240



# Replace with your Bearer token  
token = "token"
robotId = 1
deviceType = "robot"

wsurl = f"ws://localhost:8080/video?token={token}&robotid={robotId}&type={deviceType}"


# websocket.enableTrace(True)

ws = websocket.WebSocket()
ws.connect(wsurl)


useCamera = False

if useCamera:
    cap = cv2.VideoCapture(0)


try:
    while True:
        
        if useCamera:
            ret, frame = cap.read()
        else:
            frame = np.random.randint(0,255,size=(ih,iw,3), dtype=np.uint8)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    
        code,jpgBuffer = cv2.imencode(".jpg",frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])

        ws.send_binary(jpgBuffer)

        time.sleep(1.0/30)

except KeyboardInterrupt:
    ws.close()
    if useCamera:
        cap.release()


#print(ws.recv())
#



# t0 = time.time()
# ctr = 0



#     #

#     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     code,jpgBuffer = cv2.imencode(".jpg",frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])


# def on_message(ws, message):
#     #encoded = 'data:image/jpg;base64,'+base64.b64encode(message)
#     img1 = np.frombuffer(message, np.uint8)
#     img_cv = cv2.imdecode(img1, cv2.IMREAD_ANYCOLOR)

#     global t0
#     global ctr

#     if (time.time()-t0) > 2.0:
#         cv2.imwrite(os.path.join(f"./calibration", f"image_{ctr}.png"), img_cv)
#         t0 = time.time()
#         ctr+=1
#         print(os.path.join(f"./calibration", f"image_{ctr}.png"))

#     #print(img_cv.shape)
#     cv2.imshow('Frame', img_cv)

#     if cv2.waitKey(25) & 0xFF == ord('q'):
#         cv2.destroyAllWindows()

# def on_error(ws, error):
#     print(error)

# def on_close(ws, close_status_code, close_msg):
#     print("### closed ###")

# def on_open(ws):
#     print("### opened ###")


# if __name__ == "__main__":
#     # When you’re first writing your code, you will want to make sure everything is working as you planned. The easiest way to view the verbose connection information is the use
#     #websocket.enableTrace(True)

#     ws = websocket.WebSocketApp("ws://192.168.2.166:81/",
#         on_open=on_open,
#         on_message=on_message,
#         on_error=on_error,
#         on_close=on_close
#     )

#     ws.run_forever()