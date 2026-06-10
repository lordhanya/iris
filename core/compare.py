import numpy as np
import logging

from core.logger import get_logger
log = get_logger(__name__)

DEFAULT_THRESHOLD = 0.6


def compare_faces(known_encoding, candidate_encoding, threshold=DEFAULT_THRESHOLD, debug=False):
    if known_encoding is None or candidate_encoding is None:
        log.error("One or both encodings are None")
        return False, -1.0
    
    known = np.array(known_encoding)
    candidate = np.array(candidate_encoding)
    
    if known.shape != candidate.shape:
        log.error(f"Encoding shape mismatch: {known.shape} vs {candidate.shape}")
        return False, -1.0
    
    distance = np.linalg.norm(known - candidate)
    
    if debug:
        log.info(f"Face distance: {distance:.4f}, threshold: {threshold}")
    
    match = distance < threshold
    
    return match, distance


def compare_multiple(known_encodings, candidate_encoding, threshold=DEFAULT_THRESHOLD, debug=False):
    if known_encodings is None or candidate_encoding is None:
        log.error("One or both encodings are None")
        return False, -1.0
    
    if isinstance(known_encodings, np.ndarray):
        known_encodings = [known_encodings]
    
    best_match = False
    best_distance = float('inf')
    best_idx = -1
    
    for i, known in enumerate(known_encodings):
        match, distance = compare_faces(known, candidate_encoding, threshold, debug=False)
        
        if debug:
            log.info(f"Comparison {i}: distance={distance:.4f}, match={match}")
        
        if match and distance < best_distance:
            best_match = True
            best_distance = distance
            best_idx = i
    
    if debug and best_idx >= 0:
        log.info(f"Best match: index={best_idx}, distance={best_distance:.4f}")
    
    return best_match, best_distance if best_match else -1.0


def load_encoding(path):
    try:
        encoding = np.load(path)
        log.info(f"Loaded encoding from {path}")
        return encoding
    except Exception as e:
        log.error(f"Failed to load encoding: {e}")
        return None


def save_encoding(encoding, path):
    try:
        np.save(path, encoding)
        log.info(f"Saved encoding to {path}")
        return True
    except Exception as e:
        log.error(f"Failed to save encoding: {e}")
        return False


if __name__ == "__main__":
    test_encoding = np.random.rand(128)
    test_encoding = test_encoding / np.linalg.norm(test_encoding)
    
    match, distance = compare_faces(test_encoding, test_encoding, debug=True)
    print(f"Same encoding - match: {match}, distance: {distance:.4f}")
    
    noise = np.random.rand(128) * 0.1
    different = test_encoding + noise
    different = different / np.linalg.norm(different)
    
    match, distance = compare_faces(test_encoding, different, debug=True)
    print(f"Different encoding - match: {match}, distance: {distance:.4f}")