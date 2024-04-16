import os
import cv2
from mss import mss
import numpy as np
import subprocess

# تنظیمات ضبط صفحه نمایش
bounding_box = {'top': 0, 'left': 0, 'width': 1366, 'height': 768}

# پیدا کردن مسیر فعلی فایل main.py
current_directory = os.path.dirname(os.path.abspath(__file__))

# مسیر دایرکتوری برنامه
directory = os.path.join(current_directory, 'screenshots_and_videos')
os.makedirs(directory, exist_ok=True)

# شماره بار اجرای برنامه
run_number = 1

# پیدا کردن آخرین شماره بار اجرا شده
while os.path.exists(os.path.join(directory, f'run-{run_number}')):
    run_number += 1

# ایجاد دایرکتوری برای اجرای فعلی
run_folder = os.path.join(directory, f'run-{run_number}')
os.makedirs(run_folder)

# ایجاد شیء برای ضبط صفحه نمایش
sct = mss()

# تنظیمات خروجی ویدیو
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_path = os.path.join(run_folder, 'output.mp4')
out = cv2.VideoWriter(video_path, fourcc, 20.0, (bounding_box['width'], bounding_box['height']))

while True:
    # ضبط تصویر از صفحه نمایش
    sct_img = sct.shot(mon=-1)

    # تبدیل تصویر از مسیر فایل به آرایه numpy
    img = cv2.imread(sct_img)
    frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # نمایش تصویر در پنجره
    cv2.imshow('Screen Capture', frame)

    # ذخیره تصویر در فایل ویدیو
    out.write(frame)

    # ذخیره تصویر در فایل عکس
    image_path = os.path.join(run_folder, f'image-{run_number:02d}.png')
    cv2.imwrite(image_path, frame)

    # بررسی برای خروج با کلید 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# پاکسازی منابع
out.release()
cv2.destroyAllWindows()

# تبدیل ویدیو به فرمت قابل پخش توسط تمام پلیرها
converted_video_path = os.path.join(run_folder, 'output_converted.mp4')
subprocess.run(['ffmpeg', '-i', video_path, '-vf', 'setpts=1.0*PTS', converted_video_path])
