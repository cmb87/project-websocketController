import time
import cv2
import numpy as np
# Cam properties
fps = 30.
frame_width = 640
frame_height = 480

# Create capture
#cap = cv2.VideoCapture(0)

# Set camera properties
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
#cap.set(cv2.CAP_PROP_FPS, fps)

# Define the gstreamer sink
gst_str_rtp = "appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! rtph264pay ! udpsink host=0.0.0.0 port=5002"


# Check if cap is open
#if cap.isOpened() is not True:
#    print("Cannot open camera. Exiting.")
#   quit()

# Create videowriter as a SHM sink
out = cv2.VideoWriter(gst_str_rtp, 0, fps, (frame_width, frame_height), True)

# Loop it
while True:
    # Get the frame
    #ret, frame = cap.read()
    print("publishing....")
    ret, frame = True, np.random.randint(0,255,size=(frame_height,frame_width,3),dtype=np.uint8)
    # Check
    if ret is True:
        # Flip frame
        frame = cv2.flip(frame, 1)
        # Write to SHM
        out.write(frame)
    else:
        time.sleep(10)

cap.release()