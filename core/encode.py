import cv2
import logging
import numpy as np

from core.logger import get_logger
log = get_logger(__name__)

from core import face_recognition_wrapper as fr
from core import preprocess


def encode_face(frame, face_location=None, debug=False):
    if frame is None:
        log.error("No frame provided")
        return None
    
    gray, status = preprocess.process_ir_frame(frame, debug=debug)
    
    if gray is None:
        log.warning(f"Frame preprocessing failed: {status}")
        return None
    
    if face_location:
        rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        encodings = fr.face_encodings(rgb, [face_location])
    else:
        rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        encodings = fr.face_encodings(rgb)
    
    if len(encodings) == 0:
        log.warning("No face encoding found")
        return None
    
    encoding = encodings[0]
    
    if debug:
        log.info(f"Encoding generated: {len(encoding)} values")
        log.debug(f"First 5 values: {encoding[:5]}")
    
    return encoding


def encode_face_from_processed(gray, face_location=None, debug=False):
    if gray is None:
        log.error("No processed frame provided")
        return None
    
    if face_location:
        rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        encodings = fr.face_encodings(rgb, [face_location])
    else:
        rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        encodings = fr.face_encodings(rgb)
    
    if len(encodings) == 0:
        log.warning("No face encoding found")
        return None
    
    encoding = encodings[0]
    
    if debug:
        log.info(f"Encoding generated: {len(encoding)} values")
    
    return encoding


def encode_faces(frame, face_locations=None, debug=False):
    if frame is None:
        log.error("No frame provided")
        return []
    
    gray, status = preprocess.process_ir_frame(frame, debug=debug)
    
    if gray is None:
        log.warning(f"Frame preprocessing failed: {status}")
        return []
    
    rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    encodings = fr.face_encodings(rgb, face_locations)
    
    if debug:
        log.info(f"Generated {len(encodings)} encoding(s)")
    
    return encodings


def average_encodings(encodings, debug=False):
    if not encodings:
        log.error("No encodings to average")
        return None
    
    if len(encodings) == 1:
        return encodings[0]
    
    encoding_array = np.array(encodings)
    avg = np.mean(encoding_array, axis=0)
    
    if debug:
        log.info(f"Averaged {len(encodings)} encodings")
    
    return avg


def normalize_encoding(encoding):
    norm = np.linalg.norm(encoding)
    if norm > 0:
        return encoding / norm
    return encoding


if __name__ == "__main__":
    from core.capture import capture_frame
    from core.detect import detect_faces
    
    frame = capture_frame()
    if frame is not None:
        locations = detect_faces(frame, debug=True)
        if locations:
            enc = encode_face(frame, locations[0], debug=True)
            if enc is not None:
                print(f"Encoding: {enc[:5]}...")
        else:
            print("No face detected")
    else:
        log.error("No frame")