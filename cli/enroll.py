#!/usr/bin/env python3
import os
import sys
import argparse
import cv2
import numpy as np

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)
sys.path.insert(0, os.path.join(PROJECT_DIR, '..'))

from core.logger import setup_logging, get_logger
from core import config

from core.capture import Camera
from core import preprocess
from core.detect import get_largest_face_processed, validate_face_size
from core.encode import encode_faces, average_encodings
from core.compare import save_encoding

log = get_logger(__name__)


def capture_and_encode(device=None, num_samples=None, total_captures=None, debug=False):
    device = device or config.video_device()
    num_samples = num_samples or config.enroll_samples()
    total_captures = total_captures or config.enroll_attempts()
    min_face_h = config.min_face_height()

    camera = Camera(device)
    
    if not camera.open():
        log.error("Failed to open camera")
        return None
    
    encodings = []
    valid_frames = []
    
    for i in range(total_captures):
        log.info(f"Capturing sample {i + 1}/{total_captures}...")
        
        frame = camera.read()
        if frame is None:
            log.warning(f"Failed to read frame {i + 1}")
            continue
        
        # Skip dark frames caused by IR emitter flash
        if len(frame.shape) == 3:
            gray_check = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray_check = frame
        is_dark, dark_pct = preprocess.is_dark_frame(gray_check)
        if is_dark:
            log.debug(f"Skipping dark frame ({dark_pct:.0f}% dark)")
            continue
        
        gray, status = preprocess.process_ir_frame(frame, debug=debug)
        
        if gray is None:
            log.warning(f"Frame {i + 1} rejected: {status}")
            continue
        
        from core import face_recognition_wrapper as fr
        face_locations = fr.face_locations_hog(gray)
        
        if not face_locations:
            log.warning(f"No face detected in sample {i + 1}")
            continue
        
        if not validate_face_size(face_locations[0], min_face_h):
            log.warning(f"Face too small in sample {i + 1} (height < {min_face_h})")
            continue
        
        encoding = encode_faces(frame, face_locations, debug=debug)
        
        if not encoding:
            log.warning(f"Failed to encode face in sample {i + 1}")
            continue
        
        encodings.append(encoding[0])
        valid_frames.append(i + 1)
        log.info(f"Sample {i + 1} captured successfully (total valid: {len(encodings)})")
        
        if len(encodings) >= num_samples:
            break
    
    camera.close()
    
    if len(encodings) < 3:
        log.error(f"Not enough valid samples: {len(encodings)} (need at least 3)")
        return None
    
    log.info(f"Using {len(encodings)} samples for encoding")
    avg_encoding = average_encodings(encodings, debug=debug)
    log.info(f"Averaged {len(encodings)} encodings")
    
    return avg_encoding


def enroll(user_encoding_path=None, device=None, num_samples=None, debug=False, force=False):
    user_encoding_path = user_encoding_path or config.encoding_path()
    device = device or config.video_device()
    num_samples = num_samples or config.enroll_samples()

    log.info("Starting face enrollment...")
    
    if os.path.exists(user_encoding_path):
        log.warning(f"Existing encoding found at {user_encoding_path}")
        if not force:
            response = input("Overwrite existing encoding? (y/n): ")
            if response.lower() != 'y':
                log.info("Enrollment cancelled")
                return False
    
    encoding = capture_and_encode(device, num_samples, debug=debug)
    
    if encoding is None:
        log.error("Failed to capture face encoding")
        return False
    
    success = save_encoding(encoding, user_encoding_path)
    
    if success:
        os.chmod(user_encoding_path, 0o600)
        log.info(f"Face encoding saved to {user_encoding_path}")
        log.info("Enrollment successful!")
        return True
    else:
        log.error("Failed to save encoding")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Face enrollment system")
    parser.add_argument("--samples", type=int, default=None, help="Number of samples to capture")
    parser.add_argument("--device", type=str, default=None, help="Camera device")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing encoding")
    args = parser.parse_args()

    setup_logging(debug=args.debug or config.is_debug())

    success = enroll(
        device=args.device,
        num_samples=args.samples,
        debug=args.debug or config.is_debug(),
        force=args.force
    )
    
    sys.exit(0 if success else 1)