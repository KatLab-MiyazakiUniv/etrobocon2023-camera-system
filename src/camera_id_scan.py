"""列車捕捉モジュール.

カメラIDを特定するためのスクリプト
@author: miyashita64
@note
    $ poetry run python camera_id_scan.py
"""

import cv2
from camera_interface import CameraInterface

for camera_id in range(0,10):
    camera = CameraInterface(camera_id)
    success, frame = camera.get_frame()
    if success:
        cv2.imwrite(f"test_{camera_id}.png", frame)