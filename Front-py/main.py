import os
import cv2
from mss import mss
import subprocess
import psutil
import sqlite3
from datetime import datetime
import time 
#setting record view
bounding_box = {'top': 0, 'left': 0, 'width': 1366, 'height': 768}

#search file main.py
current_directory = os.path.dirname(os.path.abspath(__file__))

# path dirctory app
directory = os.path.join(current_directory, 'screenshots_and_videos')
os.makedirs(directory, exist_ok=True)

# number bar app
run_number = 1

# search app end
while os.path.exists(os.path.join(directory, f'run-{run_number}')):
    run_number += 1

# creat foolder now
run_folder = os.path.join(directory, f'run-{run_number}')
os.makedirs(run_folder)

# creat class this record
sct = mss()

# setting output video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_path = os.path.join(run_folder, 'output.mp4')
out = cv2.VideoWriter(video_path, fourcc, 0.5, (bounding_box['width'], bounding_box['height']))

chrome_process_name = "chrome.exe"
chrome_running = False

# Create or connect to SQLite database file
db_folder = os.path.join(current_directory, 'db')
os.makedirs(db_folder, exist_ok=True)
db_path = os.path.join(db_folder, 'screen_capture_data.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Create table if it does not exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS screen_capture_data (
                        id INTEGER PRIMARY KEY,
                        image_path TEXT NOT NULL,
                        video_path TEXT NOT NULL,
                        timestamp TEXT NOT NULL
                    )''')

    while True:
        # Check if Chrome is running
        for proc in psutil.process_iter(['pid', 'name']):
            if chrome_process_name in proc.info['name']:
                chrome_running = True
                break
        else:
            chrome_running = False

        if chrome_running:
            # Capture screen image
            sct_img = sct.shot(mon=-1)
            frame = cv2.cvtColor(cv2.imread(sct_img), cv2.COLOR_BGR2RGB)

            # Display the captured frame
            cv2.imshow('Screen Capture', frame)

            # Write the frame to the video output
            out.write(frame)

        else:
            print("Chrome is not running. Exiting...")
            break

        # Check for 'q' key press to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(1)  # استفاده از ماژول time برای تأخیر

finally:
    # Save the last captured frame as an image file
    last_image_path = os.path.join(run_folder, f'last_image.png')
    cv2.imwrite(last_image_path, frame)

    # Update the database with the last image and video paths
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('INSERT INTO screen_capture_data (image_path, video_path, timestamp) VALUES (?, ?, ?)', (last_image_path, video_path, timestamp))

    # Commit changes and close the database connection
    conn.commit()
    conn.close()

    # Release resources
    out.release()
    cv2.destroyAllWindows()

    # Convert video to a playable format by all players
    converted_video_path = os.path.join(run_folder, 'output_converted.mp4')
    subprocess.run(['ffmpeg', '-i', video_path, '-vf', 'setpts=1.0*PTS', converted_video_path])
