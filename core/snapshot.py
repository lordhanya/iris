import cv2
import numpy as np
import os
import logging
from datetime import datetime

from core.logger import get_logger
from core import config
log = get_logger(__name__)


def make_snapshot(frames, result, metadata=None):
    if not frames:
        log.debug("No frames to snapshot")
        return None

    snap_dir = os.path.join(config.log_dir(), "snapshots")
    os.makedirs(snap_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    label = "SUCCESS" if result else "FAILED"

    frame = frames[-1]
    if len(frame.shape) == 2:
        display = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    else:
        display = frame.copy()

    cv2.putText(display, f"{label} - {timestamp}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if result else (0, 0, 255), 2)

    y_offset = 60
    if metadata:
        for key, value in metadata.items():
            cv2.putText(display, f"{key}: {value}",
                        (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            y_offset += 20

    filename = f"{label}_{timestamp}.jpg"
    filepath = os.path.join(snap_dir, filename)
    cv2.imwrite(filepath, display)
    log.info(f"Snapshot saved: {filepath}")
    return filepath
