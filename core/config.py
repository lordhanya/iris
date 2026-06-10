import configparser
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_config = None

def load():
    global _config
    if _config is not None:
        return _config

    _config = configparser.ConfigParser()
    config_path = os.path.join(PROJECT_DIR, 'config.ini')

    if not os.path.exists(config_path):
        print(f"FATAL: Config file not found at {config_path}", file=sys.stderr)
        sys.exit(1)

    _config.read(config_path)
    return _config


def get(section, key, fallback=None):
    cfg = load()
    try:
        return cfg.get(section, key, fallback=fallback)
    except configparser.NoSectionError:
        return fallback


def getint(section, key, fallback=None):
    cfg = load()
    try:
        return cfg.getint(section, key, fallback=fallback)
    except (configparser.NoSectionError, ValueError):
        return fallback


def getfloat(section, key, fallback=None):
    cfg = load()
    try:
        return cfg.getfloat(section, key, fallback=fallback)
    except (configparser.NoSectionError, ValueError):
        return fallback


def getboolean(section, key, fallback=None):
    cfg = load()
    try:
        return cfg.getboolean(section, key, fallback=fallback)
    except (configparser.NoSectionError, ValueError):
        return fallback


def resolve(path):
    return os.path.join(PROJECT_DIR, path)


def video_device():
    return get('video', 'device', fallback='/dev/video0')


def video_width():
    return getint('video', 'width', fallback=640)


def video_height():
    return getint('video', 'height', fallback=480)


def video_fps():
    return getint('video', 'fps', fallback=30)


def auth_timeout():
    return getint('video', 'timeout', fallback=5)


def auth_threshold():
    return getfloat('auth', 'threshold', fallback=0.6)


def min_face_height():
    return getint('video', 'min_face_height', fallback=80)


def dark_threshold():
    return getfloat('video', 'dark_threshold', fallback=60)


def max_retries():
    return getint('video', 'max_retries', fallback=3)


def enroll_samples():
    return getint('auth', 'enroll_samples', fallback=5)


def enroll_attempts():
    return getint('auth', 'enroll_attempts', fallback=10)


def encoding_path():
    return resolve(get('paths', 'encoding_path', fallback='data/user_face.npy'))


def log_dir():
    return resolve(get('paths', 'log_dir', fallback='logs'))


def debug_dir():
    return resolve(get('paths', 'debug_dir', fallback='logs/debug_frames'))


def is_debug():
    return getboolean('core', 'debug', fallback=False)


def is_disabled():
    return getboolean('core', 'disabled', fallback=False)
