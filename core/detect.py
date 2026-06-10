import cv2
import logging
import numpy as np

from core.logger import get_logger
log = get_logger(__name__)

from core import face_recognition_wrapper as fr
from core import preprocess


def detect_faces(frame, debug=False):
    if frame is None:
        log.error("No frame provided")
        return []
    
    if frame.size == 0:
        log.error("Empty frame")
        return []
    
    if len(frame.shape) == 2:
        gray_frame = frame
    else:
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    valid, reason, stats = preprocess.validate_frame_quality(gray_frame)
    if not valid:
        if debug:
            log.debug(f"Frame rejected: {reason}")
        return []
    
    locations = fr.face_locations_hog(gray_frame)
    
    if not locations and debug:
        log.debug("HOG detected no faces, trying fallback")
    
    if not locations:
        try:
            locations = fr.face_locations(cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB))
        except:
            pass
    
    if debug:
        log.info(f"Detected {len(locations)} face(s)")
        for i, loc in enumerate(locations):
            log.debug(f"Face {i}: top={loc[0]}, right={loc[1]}, bottom={loc[2]}, left={loc[3]}")
    
    return locations


def detect_faces_preprocessed(frame, debug=False):
    if frame is None:
        log.error("No frame provided")
        return [], None
    
    gray, status = preprocess.process_ir_frame(frame, debug=debug)
    
    if gray is None:
        if debug:
            log.debug(f"Frame preprocessing failed: {status}")
        return [], status
    
    locations = fr.face_locations_hog(gray)
    
    if debug:
        log.info(f"Detected {len(locations)} face(s) from processed frame")
    
    return locations, "OK"


def get_largest_face(frame, debug=False):
    face_locations = detect_faces(frame, debug=debug)
    
    if len(face_locations) == 0:
        return None
    
    if len(face_locations) == 1:
        return face_locations[0]
    
    largest = None
    max_area = 0
    
    for loc in face_locations:
        top, right, bottom, left = loc
        area = (bottom - top) * (right - left)
        if area > max_area:
            max_area = area
            largest = loc
    
    log.info(f"Largest face: area={max_area}")
    return largest


def get_largest_face_processed(frame, debug=False):
    face_locations, status = detect_faces_preprocessed(frame, debug=debug)
    
    if len(face_locations) == 0:
        return None, status
    
    if len(face_locations) == 1:
        return face_locations[0], "OK"
    
    largest = None
    max_area = 0
    
    for loc in face_locations:
        top, right, bottom, left = loc
        area = (bottom - top) * (right - left)
        if area > max_area:
            max_area = area
            largest = loc
    
    log.info(f"Largest face: area={max_area}")
    return largest, "OK"


def validate_face_size(face_location, min_height=80):
    top, right, bottom, left = face_location
    height = bottom - top
    
    if height < min_height:
        log.warning(f"Face too small: height={height}, min={min_height}")
        return False
    
    return True


def detect_with_stats(frame, debug=False):
    if frame is None:
        log.error("No frame provided")
        return [], None
    
    gray, status = preprocess.process_ir_frame(frame, debug=debug)
    
    if gray is None:
        return [], status
    
    stats = {
        'mean': np.mean(gray),
        'std': np.std(gray)
    }
    
    locations = fr.face_locations_hog(gray)
    
    if debug:
        log.info(f"Detected {len(locations)} face(s), stats: mean={stats['mean']:.1f}, std={stats['std']:.1f}")
    
    return locations, stats


if __name__ == "__main__":
    from core.capture import capture_frame
    
    frame = capture_frame()
    if frame is not None:
        locations = detect_faces(frame, debug=True)
        print(f"Detected {len(locations)} face(s)")
    else:
        log.error("No frame captured")