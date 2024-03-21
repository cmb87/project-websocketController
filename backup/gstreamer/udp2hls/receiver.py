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

WIDTH = 640
HEIGHT = 480

# Initialize GStreamer  
Gst.init(None)  
  
app = Flask(__name__)
frame_queue = queue.Queue(maxsize=10)  

# Callback function to push video frames 


os.system("rm *.ts")
os.system("rm playlist.m3u8")

def create_receiver_pipeline(port):  
    # H264
    if True:
        pipeline = Gst.parse_launch(
            f"udpsrc port={port} ! application/x-rtp,media=video,payload=96,encoding-name=H264 ! queue ! "  
            "rtph264depay ! h264parse ! "
            "mpegtsmux  ! "
            "hlssink max-files=6 playlist-length=2 target-duration=4 playlist-root=http://192.168.178.114:8000/ location=segment%05d.ts playlist-location=playlist.m3u8"                      
        ) 


    else:
    # H265
        pipeline = Gst.parse_launch(
            f"udpsrc port={port} ! application/x-rtp,media=video,payload=96,encoding-name=H265 ! queue ! "  
            "rtph265depay ! h265parse "
            "mpegtsmux  ! "
            "hlssink max-files=6 playlist-length=2 target-duration=4 playlist-root=http://192.168.178.114:8000/ location=segment%05d.ts playlist-location=playlist.m3u8"                      
        ) 
    return pipeline  
  


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

@app.route('/dash/<path:path>')  
def serve_dash_files(path):  
    return send_from_directory("./", path)  


if __name__ == "__main__":


    port = 5000  

    # Create the GStreamer pipeline  
    receiver_pipeline = create_receiver_pipeline(port)  

    # Start the GStreamer pipeline  
    receiver_pipeline.set_state(Gst.State.PLAYING)  
    
    main_loop = GLib.MainLoop()  



    # Run the GLib main loop to keep the pipeline running  
    try:
        main_loop = GLib.MainLoop()  

        glib_loop_thread = threading.Thread(target=main_loop.run, daemon=True)  
        glib_loop_thread.start()  

        logging.info("Starting flask")
        app.run(host="0.0.0.0", port="8000")  


    except KeyboardInterrupt:
        receiver_pipeline.set_state(Gst.State.NULL)  
        pass