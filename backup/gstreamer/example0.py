import sys  
import cv2  
import numpy as np
import gi  
import logging
import queue
import threading
from flask import Flask, Response

gi.require_version("Gst", "1.0")  
from gi.repository import Gst, GLib  
  
logging.basicConfig(
    level=logging.INFO,
    format=("[%(filename)8s] [%(levelname)4s] :  %(funcName)s - %(message)s"),
)

WIDTH = 480
HEIGHT = 320

# Initialize GStreamer  
Gst.init(None)  
  
app = Flask(__name__)
frame_queue = queue.Queue(maxsize=10)  

# Callback function to push video frames into the appsrc element  
def push_data(appsrc, length):  
    ret, frame = True, np.random.randint(0,255,size=(HEIGHT,WIDTH,3),dtype=np.uint8)
    if not ret:  
        return Gst.FlowReturn.EOS  
    else:  
        ret, buffer = cv2.imencode(".jpg", frame)  
        frame = buffer.tobytes()  
        buf = Gst.Buffer.new_wrapped(frame)  
        return appsrc.emit("push-buffer", buf)  
  
# Create a GStreamer pipeline with appsrc, videoconvert, and autovideosink elements  
pipeline = Gst.parse_launch("appsrc name=appsrc ! decodebin ! videoconvert ! appsink name=appsink emit-signals=true")  
  
# Get a reference to the appsrc element  
appsrc = pipeline.get_by_name("appsrc")  
  
# Set the appropriate properties for appsrc  
appsrc.set_property("caps", Gst.Caps.from_string(f"video/x-raw,format=RGB,width={WIDTH},height={HEIGHT},framerate=30/1"))  
appsrc.set_property("format", Gst.Format.TIME)  
appsrc.set_property("is-live", True)  
  
# Set the need-data callback for appsrc  
appsrc.connect("need-data", push_data)  
  
# Open the video source with OpenCV  

def on_new_buffer(appsink):  
    sample = appsink.emit("pull-sample")  

    if sample:  
        buffer = sample.get_buffer()  
        _, mapinfo = buffer.map(Gst.MapFlags.READ)  
        data = mapinfo.data
        if not frame_queue.full():  
            frame_queue.put(data)
        # Process the data as needed (e.g., display it using OpenCV)  
    return Gst.FlowReturn.OK  


def generate_video_frames():  
    while True:  
        frame = frame_queue.get()  
 
        yield (b'--frame\r\n'  
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  
  
@app.route("/video_feed")  
def video_feed():  
    return Response(generate_video_frames(),  
                    mimetype="multipart/x-mixed-replace; boundary=frame")  


appsink = pipeline.get_by_name("appsink")  
appsink.connect("new-sample", on_new_buffer)  

# Start the GStreamer pipeline  
pipeline.set_state(Gst.State.PLAYING)  
  
main_loop = GLib.MainLoop()  



# Run the GLib main loop to keep the pipeline running  
try:
    main_loop = GLib.MainLoop()  

    glib_loop_thread = threading.Thread(target=main_loop.run, daemon=True)  
    glib_loop_thread.start()  

    logging.info("Starting flask")
    app.run(host="0.0.0.0", port="8000")  


except KeyboardInterrupt:
    pipeline.set_state(Gst.State.NULL)  
    pass