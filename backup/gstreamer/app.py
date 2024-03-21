import sys  , os
import cv2  
import numpy as np
import gi  
import logging
import queue
import threading
from flask import Flask, Response, send_file, make_response, send_from_directory

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

#pipeline = Gst.parse_launch('appsrc name=appsrc ! videoconvert ! x264enc tune=zerolatency speed-preset=ultrafast key-int-max=30    ! hlssink target-duration=4  playlist-root=http://192.168.178.114:8000/ location=segment%05d.ts playlist-location=playlist.m3u8')  
#pipeline = Gst.parse_launch('appsrc name=appsrc ! videoconvert ! x264enc tune=zerolatency ! hlssink  max-files=5 target-duration=4  playlist-root=http://192.168.178.114:8000/ location=segment%05d.ts playlist-location=playlist.m3u8')  
#pipeline = Gst.parse_launch('appsrc name=appsrc ! videoconvert ! x264enc tune=zerolatency ! video/x-h264,stream-format=byte-stream  ! queue ! hlssink  max-files=5 target-duration=4 playlist-root=http://192.168.178.114:8000/ location=segment%05d.ts playlist-location=playlist.m3u8')  

# Working!! :)
#pipeline = Gst.parse_launch('filesrc location=example.mp4  ! qtdemux ! h264parse ! mpegtsmux ! hlssink  max-files=5 target-duration=1 playlist-root=http://192.168.178.114:8000/ location=segment%05d.ts playlist-location=playlist.m3u8')  

# Working!! :)
pipeline = Gst.parse_launch(' videotestsrc ! videoconvert ! x264enc tune=zerolatency ! h264parse ! mpegtsmux ! hlssink  max-files=5 target-duration=10 playlist-root=http://192.168.178.114:8000/ location=segment%05d.ts playlist-location=playlist.m3u8')  


# speed-preset=ultrafast key-int-max=30  ! h264parse

if False:
    # Get a reference to the appsrc element  
    appsrc = pipeline.get_by_name("appsrc")  
    
    # Set the appropriate properties for appsrc  
    appsrc.set_property("caps", Gst.Caps.from_string(f"video/x-raw,format=RGB,width={WIDTH},height={HEIGHT},framerate=30/1"))  
    appsrc.set_property("format", Gst.Format.TIME)  
    appsrc.set_property("is-live", True)  
    
    # Set the need-data callback for appsrc  
    appsrc.connect("need-data", push_data)  
  

@app.route("/playlist.m3u8")  
def serve_playlist():  
    response = make_response(send_from_directory("./", "playlist.m3u8"))  
    response.headers.set("Content-Type", "application/vnd.apple.mpegurl")  
    return response  
  
@app.route("/<path:filename>")  
def serve_segments(filename):  
    response = make_response(send_from_directory("./", filename))  
    response.headers.set("Content-Type", "video/MP2T")  
    return response  




#appsink = pipeline.get_by_name("appsink")  
#appsink.connect("new-sample", on_new_buffer)  

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