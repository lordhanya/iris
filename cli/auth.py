#!/usr/bin/env python3
import os
import sys
import argparse
import time
import cv2
import numpy as np

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)
sys.path.insert(0, os.path.join(PROJECT_DIR, '..'))

from core.logger import setup_logging, get_logger
from core import config
from core import security
from core import snapshot

from core.capture import Camera
from core import preprocess
from core.detect import get_largest_face_processed, validate_face_size
from core.encode import encode_face
from core.compare import compare_faces, load_encoding

log = get_logger(__name__)


def authenticate(encoding_path=None, device=None, timeout=None, threshold=None, debug=False):
    encoding_path = encoding_path or config.encoding_path()
    device = device or config.video_device()
    timeout = timeout if timeout is not None else config.auth_timeout()
    threshold = threshold if threshold is not None else config.auth_threshold()
    min_face_h = config.min_face_height()

    if config.is_disabled():
        log.warning("Face auth is disabled in config")
        return False, "DISABLED"

    env_issues = security.check_environment()
    for tag, msg in env_issues:
        log.warning(msg)
        return False, tag

    log.info(f"Starting face authentication (timeout={timeout}s, threshold={threshold})")

    snap_frames = []
    save_failed = config.getboolean('snapshots', 'save_failed', fallback=True)
    save_successful = config.getboolean('snapshots', 'save_successful', fallback=False)
    
    if not os.path.exists(encoding_path):
        log.error(f"No enrolled face found at {encoding_path}")
        return False, "NOT_ENROLLED"
    
    known_encoding = load_encoding(encoding_path)
    if known_encoding is None:
        log.error("Failed to load stored encoding")
        return False, "LOAD_ERROR"
    
    camera = Camera(device)
    
    if not camera.open():
        log.error("Failed to open camera")
        return False, "CAMERA_ERROR"
    
    start_time = time.time()
    authenticated = False
    reason = "TIMEOUT"
    attempts = 0
    
    while time.time() - start_time < timeout:
        elapsed = time.time() - start_time
        if elapsed >= timeout:
            break
        
        attempts += 1
        
        frame = camera.read()
        if frame is None:
            log.warning("Failed to read frame")
            continue
        
        # Per-frame diagnostics for debugging auth failures
        if len(frame.shape) == 3:
            gray_check = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray_check = frame
        mean_val = float(np.mean(gray_check))
        std_val = float(np.std(gray_check))

        if debug and attempts == 1:
            debug_raw = os.path.join(config.debug_dir(), f"raw_frame_{attempts}.jpg")
            cv2.imwrite(debug_raw, frame)
            log.info(f"Saved raw frame 1 to {debug_raw}")

        # Skip dark frames caused by IR emitter flash
        is_dark, dark_pct = preprocess.is_dark_frame(gray_check)
        if is_dark:
            log.info(f"Frame {attempts}: DARK ({dark_pct:.0f}% dark, mean={mean_val:.0f})")
            continue

        if save_failed or save_successful:
            if len(snap_frames) < 3:
                snap_frames.append(frame.copy())
        
        gray, status = preprocess.process_ir_frame(frame, debug=debug)
        
        if gray is None:
            log.info(f"Frame {attempts}: REJECTED ({status}, mean={mean_val:.0f}, std={std_val:.0f})")
            continue
        
        from core import face_recognition_wrapper as fr
        face_locations = fr.face_locations_hog(gray)
        
        if not face_locations:
            log.info(f"Frame {attempts}: NO FACE (mean={mean_val:.0f}, std={std_val:.0f})")
            continue
        
        if not validate_face_size(face_locations[0], min_face_h):
            log.info(f"Frame {attempts}: FACE TOO SMALL (height < {min_face_h})")
            continue
        
        encoding = encode_face(frame, face_locations[0], debug=debug)
        
        if encoding is None:
            log.info(f"Frame {attempts}: ENCODE FAILED")
            continue
        
        match, distance = compare_faces(known_encoding, encoding, threshold, debug=debug)
        
        if match:
            log.info(f"Frame {attempts}: AUTHENTICATED (distance={distance:.4f})")
            authenticated = True
            reason = "SUCCESS"
            break
        else:
            log.info(f"Frame {attempts}: NO MATCH (distance={distance:.4f})")
    
    camera.close()

    metadata = {
        "Attempts": str(attempts),
        "Threshold": str(threshold),
        "Device": device
    }

    if authenticated:
        if save_successful and snap_frames:
            snapshot.make_snapshot(snap_frames, True, metadata)
        log.info("Authentication successful!")
        return True, "SUCCESS"
    else:
        if save_failed and snap_frames:
            metadata["Reason"] = reason
            snapshot.make_snapshot(snap_frames, False, metadata)
        log.warning(f"Authentication failed: {reason} after {attempts} attempts")
        return False, reason


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Face authentication system")
    parser.add_argument("--timeout", type=int, default=None, help="Authentication timeout in seconds")
    parser.add_argument("--threshold", type=float, default=None, help="Match threshold")
    parser.add_argument("--device", type=str, default=None, help="Camera device")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    setup_logging(debug=args.debug or config.is_debug())

    success, reason = authenticate(
        device=args.device,
        timeout=args.timeout,
        threshold=args.threshold,
        debug=args.debug or config.is_debug()
    )
    
    if success:
        print("SUCCESS")
        sys.exit(0)
    else:
        print(f"FAILED: {reason}")
        sys.exit(1)