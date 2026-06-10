import dlib
import os
import sys

MODEL_NAMES = [
    'dlib_face_recognition_resnet_model_v1.dat',
    'shape_predictor_68_face_landmarks.dat',
    'shape_predictor_5_face_landmarks.dat',
    'mmod_human_face_detector.dat',
]


def _find_model_dir():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, '..', 'models'),
        os.path.join(script_dir, '..', 'venv', 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages', 'face_recognition_models', 'models'),
    ]
    for path in candidates:
        resolved = os.path.realpath(path)
        expected = os.path.join(resolved, 'dlib_face_recognition_resnet_model_v1.dat')
        if os.path.exists(expected):
            return resolved
    return None


MODEL_DIR = _find_model_dir()

if MODEL_DIR is None:
    # Try python -c to locate face_recognition_models
    import subprocess
    result = subprocess.run(
        [sys.executable, '-c', 'import face_recognition_models; print(face_recognition_models.__path__[0])'],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode == 0:
        MODELS_PKG = result.stdout.strip()
        MODELS_DIR = os.path.join(MODELS_PKG, 'models')
        if os.path.exists(os.path.join(MODELS_DIR, 'dlib_face_recognition_resnet_model_v1.dat')):
            MODEL_DIR = MODELS_DIR

if MODEL_DIR is None:
    print("FATAL: dlib model files not found.", file=sys.stderr)
    print("Install python-face_recognition_models or place model files in:", file=sys.stderr)
    print(f"  {os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'models')}", file=sys.stderr)
    sys.exit(1)

face_recognition_model_path = os.path.join(MODEL_DIR, 'dlib_face_recognition_resnet_model_v1.dat')
shape_predictor_path = os.path.join(MODEL_DIR, 'shape_predictor_68_face_landmarks.dat')

_face_encoder = None
_shape_predictor = None


def get_face_encoder():
    global _face_encoder
    if _face_encoder is None:
        _face_encoder = dlib.face_recognition_model_v1(face_recognition_model_path)
    return _face_encoder


def get_shape_predictor():
    global _shape_predictor
    if _shape_predictor is None:
        _shape_predictor = dlib.shape_predictor(shape_predictor_path)
    return _shape_predictor


def compute_face_descriptor(image, face_rect):
    encoder = get_face_encoder()
    predictor = get_shape_predictor()
    
    shape = predictor(image, face_rect)
    return encoder.compute_face_descriptor(image, shape)


__all__ = ['get_face_encoder', 'get_shape_predictor', 'compute_face_descriptor']