import logging
import sys
import os
import atexit

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

_initialized = False

def setup_logging(debug=False, log_to_syslog=True):
    global _initialized
    if _initialized:
        return
    _initialized = True

    level = logging.DEBUG if debug else logging.INFO

    root = logging.getLogger()
    root.setLevel(level)

    fmt = logging.Formatter('%(asctime)s - %(levelname)s - IRIS - %(name)s - %(message)s')

    if not root.handlers:
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(level)
        console.setFormatter(fmt)
        root.addHandler(console)

        main_log = os.path.join(LOG_DIR, 'main.log')
        file_handler = logging.FileHandler(main_log)
        file_handler.setLevel(level)
        file_handler.setFormatter(fmt)
        root.addHandler(file_handler)

        if log_to_syslog:
            try:
                from logging.handlers import SysLogHandler
                syslog = SysLogHandler(address='/dev/log')
                syslog.setLevel(logging.WARNING)
                syslog.setFormatter(fmt)
                root.addHandler(syslog)
            except Exception:
                pass

def get_logger(name):
    setup_logging()
    return logging.getLogger(name)
