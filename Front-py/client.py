import subprocess
import numpy as np
from mss import mss
import cv2

# Settings for screen recording
sct = mss()
# Getting information about the first monitor (usually the primary monitor)
monitor = sct.monitors[1]  # Index 1 represents the primary monitor
monitor_info = {'top': monitor['top'], 'left': monitor['left'], 'width': monitor['width'], 'height': monitor['height']}

# FFmpeg settings for streaming data to the server
command = [
    'ffmpeg',
    '-y',  # Overwrite existing files
    '-f', 'rawvideo',  # Input format is raw video
    '-vcodec', 'rawvideo',  # Input video codec
    '-pix_fmt', 'bgr24',  # Input pixel format
    '-s', "{}x{}".format(monitor_info['width'], monitor_info['height']),  # Using monitor dimensions
    '-r', '10',  # Frame rate
    '-i', '-',  # Read data from stdin
    '-c:v', 'libx264',  # Output video codec
    '-pix_fmt', 'yuv420p',  # Output pixel format
    '-preset', 'ultrafast',  # Default settings for high speed
    '-f', 'flv',  # Output format
    'rtmp://server_address/live/stream_key'  # RTMP server address
]

# Running the FFmpeg process
pipe = subprocess.Popen(command, stdin=subprocess.PIPE)

while True:
    # Capturing the screen
    img = sct.grab(monitor_info)
    frame = np.array(img)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)  # Convert color format
    pipe.stdin.write(frame.tobytes())  # Writing frame to stdin for FFmpeg
