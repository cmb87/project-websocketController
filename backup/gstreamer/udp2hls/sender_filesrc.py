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
  

def create_sender_pipeline(host, port):  
    pipeline = Gst.parse_launch(f"filesrc location=../example.mp4 ! qtdemux  ! rtph264pay ! "  
                                f"udpsink host={host} port={port} sync=false")  
    
  
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