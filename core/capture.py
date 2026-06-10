import cv2
import numpy as np
import logging
import subprocess
import sys
import os

from core.logger import get_logger
from core import config
log = get_logger(__name__)

FORMAT = cv2.CAP_V4L2


def configure_camera(device):
    width = config.video_width()
    height = config.video_height()
    fps = config.video_fps()
    try:
        subprocess.run([
            'v4l2-ctl', '--device', device,
            '--set-fmt-video', f'width={width},height={height},pixelformat=YUYV',
            '--set-parm', str(fps)
        ], capture_output=True, timeout=5)
        log.info(f"Camera configured: {width}x{height} YUYV @ {fps}fps")
        return True
    except Exception as e:
        log.warning(f"Could not configure camera via v4l2-ctl: {e}")
        return False


class Camera:
    def __init__(self, device=None):
        self.device = device or config.video_device()
        self.width = config.video_width()
        self.height = config.video_height()
        self.cap = None
        self.frame_count = 0

    def open(self):
        log.info(f"Opening camera: {self.device}")
        
        configure_camera(self.device)
        
        self.cap = cv2.VideoCapture(self.device, FORMAT)
        
        if not self.cap.isOpened():
            log.error(f"Failed to open camera {self.device}")
            return False
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, config.video_fps())
        
        actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        log.info(f"Camera opened: {actual_width}x{actual_height} @ {actual_fps}fps")
        
        if actual_width != self.width or actual_height != self.height:
            log.warning(f"Resolution mismatch: requested {self.width}x{self.height}, got {actual_width}x{actual_height}")
        
        return True

    def read(self):
        if self.cap is None or not self.cap.isOpened():
            log.error("Camera not opened")
            return None
        
        ret, frame = self.cap.read()
        
        if not ret:
            log.warning("Failed to read frame")
            return None
        
        self.frame_count += 1
        
        if frame is None:
            log.warning("Frame is None")
            return None
        
        if frame.shape[0] != self.height or frame.shape[1] != self.width:
            frame = cv2.resize(frame, (self.width, self.height))
        
        return frame

    def read_processed(self, debug=False):
        frame = self.read()
        if frame is None:
            return None
        
        from core import preprocess
        gray, status = preprocess.process_ir_frame(frame, debug=debug)
        
        if gray is None:
            log.debug(f"Frame rejected: {status}")
            return None
        
        return gray

    def close(self):
        if self.cap:
            log.info(f"Closing camera. Total frames read: {self.frame_count}")
            self.cap.release()
            self.cap = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


def capture_frame(device=None, debug=False):
    max_retries = config.max_retries()
    camera = Camera(device)
    
    for retry in range(max_retries):
        if camera.open():
            break
        log.error(f"Retry {retry + 1}/{max_retries}")
    
    if not camera.cap or not camera.cap.isOpened():
        log.error("Camera failed to open after retries")
        return None
    
    for _ in range(5):
        frame = camera.read()
        if frame is not None:
            break
    
    camera.close()
    return frame


def capture_preview(duration=3, device=None):
    import time
    
    camera = Camera(device)
    if not camera.open():
        log.error("Camera open failed")
        return
    
    start = time.time()
    while time.time() - start < duration:
        frame = camera.read()
        if frame is not None:
            cv2.imshow("IR Camera Preview", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    camera.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    from core.logger import setup_logging
    setup_logging(debug=True)

    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        capture_preview()
    else:
        frame = capture_frame(debug=True)
        if frame is not None:
            log.info(f"Frame captured: {frame.shape}")
            sample_path = os.path.join(config.log_dir(), "sample_frame.jpg")
            cv2.imwrite(sample_path, frame)
            log.info(f"Sample frame saved to {sample_path}")
        else:
            log.error("Failed to capture frame")