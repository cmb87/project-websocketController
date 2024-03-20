import os
import base64
import numpy as np
import websocket
import cv2
import time


token = "token"
robotId = 1
deviceType = "client"

wsurl = f"ws://192.168.128.130:8080/control?token={token}&robotid={robotId}&type={deviceType}"

def on_message(ws, message):

    try:
        print("Message received")
        img1 = np.frombuffer(message, np.uint8)
        img_cv = cv2.imdecode(img1, cv2.IMREAD_ANYCOLOR)

        cv2.imshow('Frame', img_cv)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()

    except Exception as e:
        print("ololo schololo")
        print(e)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("### opened ###")


if __name__ == "__main__":
    # websocket.enableTrace(True)

    ws = websocket.WebSocketApp(
        wsurl,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever()