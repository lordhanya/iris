import configparser
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_CONFIG_DIR = os.path.expanduser("~/.config/iris")
USER_DATA_DIR = os.path.expanduser("~/.local/share/iris")

_config = None
_data_base = None


def _find_config():
    """Look for config in order: user config, then local config."""
    user_cfg = os.path.join(USER_CONFIG_DIR, "config.ini")
    if os.path.exists(user_cfg):
        return user_cfg, USER_DATA_DIR
    local_cfg = os.path.join(PROJECT_DIR, "config.ini")
    if os.path.exists(local_cfg):
        return local_cfg, PROJECT_DIR
    return None, None


def load():
    global _config, _data_base
    if _config is not None:
        return _config

    _config = configparser.ConfigParser()
    cfg_path, _data_base = _find_config()

    if cfg_path is None:
        print(
            f"FATAL: No config.ini found. Create ~/.config/iris/config.ini "
            f"or place one at {PROJECT_DIR}/config.ini",
            file=sys.stderr,
        )
        sys.exit(1)

    _config.read(cfg_path)
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
    return os.path.join(_data_base if _data_base is not None else PROJECT_DIR, path)


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
