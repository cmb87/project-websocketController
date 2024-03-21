import gi  
import logging
gi.require_version("Gst", "1.0")  
from gi.repository import Gst, GLib  
  
logging.basicConfig(
    level=logging.INFO,
    format=("[%(filename)8s] [%(levelname)4s] :  %(funcName)s - %(message)s"),
)

Gst.init(None)  
  
def create_receiver_pipeline(port):  
    pipeline = Gst.parse_launch(f"udpsrc port={port} ! application/x-rtp,media=video,payload=96,encoding-name=H264 ! "  
                                "rtph264depay ! avdec_h264 ! videoconvert ! appsink name=appsink emit-signals=true")  
    return pipeline  
  

def on_new_buffer(appsink):  
    sample = appsink.emit("pull-sample")  

    if sample:  
        buffer = sample.get_buffer()  
        _, mapinfo = buffer.map(Gst.MapFlags.READ)  
        data = mapinfo.data
        logging.info("data recevied")
        # Process the data as needed (e.g., display it using OpenCV)  
    return Gst.FlowReturn.OK  




def main():  
    port = 5000  
  
    # Create the GStreamer pipeline  
    receiver_pipeline = create_receiver_pipeline(port)  
    
    appsink = receiver_pipeline.get_by_name("appsink")  
    appsink.connect("new-sample", on_new_buffer)  

    # Start the pipeline  
    receiver_pipeline.set_state(Gst.State.PLAYING)  
  
    # Run the GLib main loop  
    loop = GLib.MainLoop()  
    try:  
        loop.run()  
    except KeyboardInterrupt:  
        print("Interrupted by user")  
  
    # Clean up  
    receiver_pipeline.set_state(Gst.State.NULL)  
  
if __name__ == "__main__":  
    main()  