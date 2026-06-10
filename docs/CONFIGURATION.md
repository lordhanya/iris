# IRIS Configuration Reference

Copy `config.example.ini` to `config.ini` and edit to suit your setup.

## [core]

| Key | Default | Description |
|-----|---------|-------------|
| `debug` | `false` | Enable verbose debug logging |
| `disabled` | `false` | Global disable — face auth skipped when true |

## [video]

| Key | Default | Description |
|-----|---------|-------------|
| `device` | `/dev/video0` | Camera device path |
| `width` | `640` | Capture width |
| `height` | `480` | Capture height |
| `fps` | `30` | Capture framerate |
| `timeout` | `5` | Max seconds to wait for a face |
| `dark_threshold` | `60` | Max % of pixels in lowest histogram bin before frame is rejected as dark |
| `min_face_height` | `80` | Minimum face height in pixels |
| `max_retries` | `3` | Camera open retries |

## [auth]

| Key | Default | Description |
|-----|---------|-------------|
| `threshold` | `0.6` | Face match distance (lower = stricter) |
| `enroll_samples` | `5` | Number of face samples to capture during enrollment |
| `enroll_attempts` | `10` | Max capture attempts during enrollment |

## [snapshots]

| Key | Default | Description |
|-----|---------|-------------|
| `save_failed` | `true` | Save snapshots on failed auth |
| `save_successful` | `false` | Save snapshots on successful auth |

## [paths]

| Key | Default | Description |
|-----|---------|-------------|
| `encoding_path` | `data/user_face.npy` | Face encoding file |
| `log_dir` | `logs` | Log output directory |
| `debug_dir` | `logs/debug_frames` | Debug frame dump directory |
