import dlib
import cv2
import numpy as np
import logging
import os

from core.face_utils import get_face_encoder, get_shape_predictor, MODEL_DIR

from core.logger import get_logger
log = get_logger(__name__)

detector_path = os.path.join(MODEL_DIR, 'mmod_human_face_detector.dat')
if not os.path.exists(detector_path):
    log.warning(f"CNN detector model not found, CNN fallback disabled")

_detector = None
_hog_detector = None


def get_detector():
    global _detector
    if _detector is None:
        _detector = dlib.cnn_face_detection_model_v1(detector_path)
    return _detector


def get_hog_detector():
    global _hog_detector
    if _hog_detector is None:
        _hog_detector = dlib.get_frontal_face_detector()
    return _hog_detector


def face_locations(rgb_frame):
    detector = get_detector()
    detections = detector(rgb_frame, 1)
    
    locations = []
    for det in detections:
        rect = det.rect
        top = rect.top()
        right = rect.right()
        bottom = rect.bottom()
        left = rect.left()
        locations.append((top, right, bottom, left))
    
    return locations


def face_locations_hog(gray_frame):
    detector = get_hog_detector()
    
    if len(gray_frame.shape) == 3:
        gray = cv2.cvtColor(gray_frame, cv2.COLOR_BGR2GRAY)
    else:
        gray = gray_frame
    
    dets = detector(gray, 1)
    
    locations = []
    for rect in dets:
        top = rect.top()
        right = rect.right()
        bottom = rect.bottom()
        left = rect.left()
        locations.append((top, right, bottom, left))
    
    return locations


def face_encodings(rgb_frame, known_face_locations=None):
    locations = known_face_locations if known_face_locations else face_locations_hog(rgb_frame)
    
    if not locations:
        locations = face_locations_hog(rgb_frame)
    
    if not locations:
        return []
    
    predictor = get_shape_predictor()
    encoder = get_face_encoder()
    
    encodings = []
    for loc in locations:
        top, right, bottom, left = loc
        rect = dlib.rectangle(left, top, right, bottom)
        
        try:
            shape = predictor(rgb_frame, rect)
            encoding = encoder.compute_face_descriptor(rgb_frame, shape)
            encodings.append(np.array(encoding))
        except Exception as e:
            log.warning(f"Failed to encode face: {e}")
            continue
    
    return encodings


def detect_and_encode_grayscale(gray_frame):
    if len(gray_frame.shape) == 2:
        rgb = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)
    else:
        rgb = gray_frame
    
    locations = face_locations_hog(gray_frame)
    
    if not locations:
        return [], None
    
    encodings = face_encodings(rgb, locations)
    
    return encodings, locations[0] if locations else None


__all__ = ['face_locations', 'face_encodings', 'face_locations_hog', 'detect_and_encode_grayscale']