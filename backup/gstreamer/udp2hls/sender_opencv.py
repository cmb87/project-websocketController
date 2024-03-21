import numpy as np  
import gi  
import logging
import cv2
gi.require_version("Gst", "1.0")  
from gi.repository import Gst, GLib  
  
logging.basicConfig(
    level=logging.INFO,
    format=("[%(filename)8s] [%(levelname)4s] :  %(funcName)s - %(message)s"),
)

Gst.init(None)  
  



host = "127.0.0.1"  
port = 5000  
file_path = "../example.mp4"  

# Open the video file using OpenCV  
cap = cv2.VideoCapture(file_path)  

# Set up the H.264 video encoder with udpsink  
fourcc = cv2.VideoWriter_fourcc(*'H264')  
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  
fps = int(cap.get(cv2.CAP_PROP_FPS))  
  
print(fps)

if not cap.isOpened():  
    print("Error: Source not found")  
      

def create_sender_pipeline(host, port, cap):  
    pipeline = Gst.parse_launch(f"appsrc name=src  ! "  
                                "videoconvert ! videoconvert ! video/x-raw,format=I420 ! x264enc tune=zerolatency ! rtph264pay ! "  
                                f"udpsink host={host} port={port} sync=false")
    
    appsrc = pipeline.get_by_name("src")  

    # Set the appropriate properties for appsrc  
    appsrc.set_property("caps", Gst.Caps.from_string(f"video/x-raw,format=RGB,width={width},height={height},framerate={fps}/1"))  # 
    appsrc.set_property("format", Gst.Format.TIME)  
    appsrc.set_property("is-live", True)  
    appsrc.connect("need-data", on_need_data, cap)  

    return pipeline

def on_need_data(src, length, cap):  
    ret, frame = cap.read()  
    logging.info("Getting frame...")
    if not ret:  
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()  
        logging.info("restarting....")

    buf = Gst.Buffer.new_wrapped(frame.tobytes()  )  
    ret = src.emit("push-buffer", buf)   
      #  return ret



def main():  
    host = "127.0.0.1"  
    port = 5000  
  
    # Create the GStreamer pipeline  
    sender_pipeline = create_sender_pipeline(host, port, cap)  
  
    # Start the pipeline  
    sender_pipeline.set_state(Gst.State.PLAYING)  
  
    # Run the GLib main loop  
    loop = GLib.MainLoop() 

    try:  
        loop.run()  
    except KeyboardInterrupt:  
        print("Interrupted by user")  
  
    # Clean up  
    sender_pipeline.set_state(Gst.State.NULL)  
  
if __name__ == "__main__":  
    main()  










  