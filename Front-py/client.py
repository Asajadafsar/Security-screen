import asyncio
import websockets
import subprocess
import numpy as np
from mss import mss
import cv2

# Screen recording settings
sct = mss()
monitor = sct.monitors[1]  # First monitor

async def record_screen(start_recording):
    """Record the screen and send data to the server using FFmpeg."""
    command = [
        'ffmpeg',
        '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', "{}x{}".format(monitor['width'], monitor['height']),
        '-r', '10',
        '-i', '-',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast',
        '-f', 'flv',
        'rtmp://server_address/live/stream_key'
    ]
    pipe = subprocess.Popen(command, stdin=subprocess.PIPE)

    while start_recording:
        img = sct.grab(monitor)
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        pipe.stdin.write(frame.tobytes())

    pipe.terminate()

async def websocket_client():
    uri = "ws://localhost:8765"  # Websocket server address
    async with websockets.connect(uri) as websocket:
        start_recording = False
        while True:
            message = await websocket.recv()
            if message == "start":
                if not start_recording:
                    start_recording = True
                    asyncio.create_task(record_screen(start_recording))
                    print("Recording started.")
            elif message == "stop":
                if start_recording:
                    start_recording = False
                    print("Recording stopped.")
            else:
                print(f"Unknown command: {message}")

asyncio.run(websocket_client())
