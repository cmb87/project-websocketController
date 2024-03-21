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
  
def push_data(src, frame):  
    #  ret, buffer = cv2.imencode(".jpg", frame)  
    #  frame = buffer.tobytes()  
    buf = Gst.Buffer.new_wrapped(frame.tobytes()  )  
    ret = src.emit("push-buffer", buf)   
    logging.info(ret)
    return ret
    
def on_need_data(src, length, data):  
    # Create a new numpy array for each frame  
    numpy_array = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)  
    push_data(src, numpy_array)  
  
def create_sender_pipeline(host, port):  
    pipeline = Gst.parse_launch(f"appsrc name=src  ! "  
                                "videoconvert ! x264enc tune=zerolatency ! rtph264pay ! "  
                                f"udpsink host={host} port={port} sync=false")  
    appsrc = pipeline.get_by_name("src")  

    # Set the appropriate properties for appsrc  
    appsrc.set_property("caps", Gst.Caps.from_string(f"video/x-raw,format=RGB,width={640},height={480},framerate=30/1"))  # 
    appsrc.set_property("format", Gst.Format.TIME)  
    appsrc.set_property("is-live", True)  

    appsrc.connect("need-data", on_need_data, None)  
    return pipeline  
  
def main():  
    host = "127.0.0.1"  
    port = 5000  
  
    # Create the GStreamer pipeline  
    sender_pipeline = create_sender_pipeline(host, port)  
  
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