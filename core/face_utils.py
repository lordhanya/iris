import dlib
import os
import sys

MODEL_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'venv', 'lib', 'python3.14', 'site-packages', 'face_recognition_models', 'models'
)

face_recognition_model_path = os.path.join(MODEL_DIR, 'dlib_face_recognition_resnet_model_v1.dat')
shape_predictor_path = os.path.join(MODEL_DIR, 'shape_predictor_68_face_landmarks.dat')

_missing_models = []
for _p in [face_recognition_model_path, shape_predictor_path]:
    if not os.path.exists(_p):
        _missing_models.append(os.path.basename(_p))
if _missing_models:
    print(f"FATAL: Missing dlib model files: {', '.join(_missing_models)}", file=sys.stderr)
    print(f"Expected in: {MODEL_DIR}", file=sys.stderr)
    print("Reinstall face_recognition_models or restore the files.", file=sys.stderr)
    sys.exit(1)

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