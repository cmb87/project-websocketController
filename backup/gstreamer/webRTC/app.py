import base64  
import json  
import threading  
import gi  
import logging
from flask import Flask, render_template  
from flask_socketio import SocketIO, emit  
  
gi.require_version("Gst", "1.0")  
from gi.repository import Gst  , GLib 
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription  

Gst.init(None)  
  
logging.basicConfig(
    level=logging.INFO,
    format=("[%(filename)8s] [%(levelname)4s] :  %(funcName)s - %(message)s"),
)


app = Flask(__name__)  
socketio = SocketIO(app, cors_allowed_origins="*")  
  
class GStreamerPipeline:  
    def __init__(self):
        
        self.pipeline = Gst.parse_launch("videotestsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! video/x-h264,profile=baseline ! appsink name=appsink emit-signals=True max-buffers=1 drop=True")  
        self.pipeline.set_state(Gst.State.PLAYING)  
        self.pipeline.get_by_name("appsink").connect("new-sample", self.on_new_sample)  
  
    def on_new_sample(self, sink):  
        sample = sink.emit("pull-sample")  
        buffer = sample.get_buffer()  
        ret, info = buffer.map(Gst.MapFlags.READ)  

        #logging.info("Emitting video frame")
        socketio.emit("video_frame", base64.b64encode(info.data).decode("utf-8")) 

        buffer.unmap(info)  
        return Gst.FlowReturn.OK  



  
@app.route("/")  
def index():  
    return render_template("index.html")  
  
@socketio.on("sdp")  
def on_sdp(data):  
    async def create_answer(data):  
        offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])  
        pc = RTCPeerConnection()  

        await pc.setRemoteDescription(offer)  
  
        @pc.on("track")  
        def on_track(track):  
            print("Track %s received" % track.kind)  
  
        answer = await pc.createAnswer()  
        await pc.setLocalDescription(answer)  
        emit("sdp", {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})  
  
    socketio.start_background_task(create_answer, data)  
  
if __name__ == "__main__":  
    Gst.init(None)  
    pipeline = GStreamerPipeline()  
    
    main_loop = GLib.MainLoop()  

    glib_loop_thread = threading.Thread(target=main_loop.run, daemon=True)  
    glib_loop_thread.start()  

    logging.info("Starting flask server")
    try:  
        socketio.run(app, host="0.0.0.0", port=8000)  
    finally:  
        pipeline.pipeline.set_state(Gst.State.NULL)  
