import logging
import sys
import os

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

        from core import config
        log_dir = config.log_dir()
        os.makedirs(log_dir, exist_ok=True)

        main_log = os.path.join(log_dir, 'main.log')
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
