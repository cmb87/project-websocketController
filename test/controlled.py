import os
import base64
import numpy as np
import websocket
import cv2
import time


token = "token"
robotId = 1
deviceType = "robot"

wsurl = f"ws://localhost:8080/control?token={token}&robotid={robotId}&type={deviceType}"

def on_message(ws, message):

    try:
        print("Message received")
        print(message)


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