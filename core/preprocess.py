import cv2
import numpy as np
import logging
import os

from core.logger import get_logger
from core import config
log = get_logger(__name__)

DEBUG_DIR = config.debug_dir()
os.makedirs(DEBUG_DIR, exist_ok=True)

MIN_MEAN = 30
MIN_STD = 10
MIN_FACE_SIZE = config.min_face_height()


def validate_frame_quality(gray, debug=False):
    mean_val = float(np.mean(gray))
    std_val = float(np.std(gray))
    
    if mean_val < MIN_MEAN:
        return False, "TOO_DARK", {"mean": mean_val, "std": std_val}
    
    if std_val < MIN_STD:
        return False, "LOW_DETAIL", {"mean": mean_val, "std": std_val}
    
    return True, "OK", {"mean": mean_val, "std": std_val}


def is_dark_frame(gray, threshold=None):
    if gray is None or gray.size == 0:
        return True, 100

    if threshold is None:
        threshold = config.dark_threshold()

    hist = cv2.calcHist([gray], [0], None, [8], [0, 256])
    hist_total = float(np.sum(hist))
    if hist_total == 0:
        return True, 100

    darkest_pct = float(hist[0][0]) / hist_total * 100
    return darkest_pct > threshold, darkest_pct


def process_ir_frame(frame, debug=False):
    if frame is None:
        return None, "NO_FRAME"
    
    if frame.size == 0:
        return None, "EMPTY_FRAME"
    
    h, w = frame.shape[:2]
    
    if len(frame.shape) == 2:
        gray = frame
    elif frame.shape[2] == 1:
        gray = frame.squeeze()
    elif frame.shape[2] == 4:
        gray = frame[:, :, 1]
    elif frame.shape[2] == 3:
        channel_1 = frame[:, :, 1]
        if np.mean(channel_1) > 100:
            gray = channel_1
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    else:
        return None, "INVALID_SHAPE"
    
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    
    equalized = cv2.equalizeHist(gray)
    
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]], dtype=np.float32)
    gray = cv2.filter2D(gray, -1, kernel)
    
    valid, reason, stats = validate_frame_quality(gray)
    if not valid:
        return None, reason
    
    if debug:
        debug_path = os.path.join(DEBUG_DIR, f"processed_{os.getpid()}.jpg")
        cv2.imwrite(debug_path, gray)
        log.debug(f"Saved processed frame to {debug_path}")
    
    return gray, "OK"


def process_ir_frame_stable(frame, previous_frame=None):
    gray, status = process_ir_frame(frame, debug=False)
    if gray is None:
        return None, status, None
    
    valid, reason, stats = validate_frame_quality(gray)
    if not valid:
        return None, reason, stats
    
    if previous_frame is not None:
        diff = cv2.absdiff(gray, previous_frame)
        diff_pct = np.mean(diff) / (np.mean(previous_frame) + 1)
        
        if diff_pct > 0.3:
            return gray, "FRAME_UNSTABLE", stats
    
    return gray, "OK", stats


def select_best_frames(frames_with_detection, required=3):
    if len(frames_with_detection) == 0:
        return []
    
    if len(frames_with_detection) <= required:
        return frames_with_detection
    
    scored = []
    for gray, face_locs, stats in frames_with_detection:
        if face_locs:
            face = face_locs[0]
            area = (face[2] - face[0]) * (face[1] - face[3])
            score = area * stats['std'] / 100
            scored.append((score, gray, face_locs))
    
    scored.sort(reverse=True, key=lambda x: x[0])
    
    return [(gray, locs) for score, gray, locs in scored[:required]]


def enhance_for_detection(frame, debug=False):
    if frame is None:
        return None, "NO_FRAME"
    
    h, w = frame.shape[:2]
    
    if len(frame.shape) == 3 and frame.shape[2] == 3:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    elif len(frame.shape) == 2:
        gray = frame
    else:
        gray = frame
    
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    
    valid, reason, stats = validate_frame_quality(gray)
    if not valid:
        return None, reason
    
    return gray, "OK"


if __name__ == "__main__":
    from core.logger import setup_logging
    setup_logging(debug=True)
    from core.capture import capture_frame
    
    frame = capture_frame()
    if frame is not None:
        gray, status = process_ir_frame(frame, debug=True)
        if gray is not None:
            print(f"Frame processed successfully: {gray.shape}")
            path = os.path.join(config.log_dir(), "processed_frame.jpg")
            cv2.imwrite(path, gray)
            print(f"Processed frame saved to {path}")
        else:
            print(f"Processing failed: {status}")
    else:
        print("No frame captured")