# IRIS — Infrared Recognition & Identity System

Password-less face unlock for SDDM on Linux, optimized for Thinkpad IR cameras.

## Features

- **Fast unlock** — recognizes your face in ~3 seconds via IR camera
- **IR-optimized** — green channel extraction, CLAHE, adaptive thresholding
- **Dark frame rejection** — ignores IR emitter flash frames automatically
- **Security checks** — skips face auth when lid is closed or over SSH
- **Snapshot capture** — saves failed auth images for review
- **Multi-layer failsafe** — never lock yourself out (emergency disable, password fallback)
- **IR emitter control** — integrates with `linux-enable-ir-emitter`

## Requirements

### Python
- Python 3.10+
- dlib, face_recognition, opencv-python, numpy

### System
- v4l-utils
- linux-enable-ir-emitter (AUR: `linux-enable-ir-emitter`)
- SDDM (for lock screen integration)

## Quick Install

### Arch Linux (AUR)

*Coming soon — search `iris-face-auth` on AUR*

### Manual

```bash
# 1. Install dependencies
sudo pacman -S v4l-utils python-opencv python-numpy
yay -S linux-enable-ir-emitter
pip install dlib face_recognition

# 2. Clone and set up
git clone https://github.com/lordhanya/iris
cd iris
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure IR emitter
sudo linux-enable-ir-emitter configure

# 4. Enroll your face
python cli/enroll.py --force

# 5. Test authentication
python cli/auth.py --timeout 10

# 6. Integrate with SDDM
sudo scripts/install-pam.sh
```

## Usage

### Enroll your face
```bash
source venv/bin/activate
python cli/enroll.py --force
```

### Test authentication
```bash
source venv/bin/activate
python cli/auth.py --timeout 10
```

### Lock and unlock
```bash
loginctl lock-session
# Press Enter at the lock screen
# IRIS will authenticate and unlock automatically
```

## Failsafe

| Method | Command |
|--------|---------|
| Emergency disable | `touch /tmp/face-auth-emergency-disable` |
| Config disable | Set `disabled = true` in `config.ini` |
| Restore PAM backup | `sudo cp /etc/pam.d/sddm.backup /etc/pam.d/sddm` |
| Uninstall PAM | `sudo scripts/uninstall-pam.sh` |

## Configuration

Copy `config.example.ini` to `config.ini` and edit:

```bash
cp config.example.ini config.ini
```

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for all options.

## Project Structure

```
iris/
├── cli/            # Entry points (auth.py, enroll.py)
├── core/           # Library modules
├── scripts/        # PAM script, installer, utilities
├── data/           # Face encodings (gitignored)
├── docs/           # Documentation
├── logs/           # Log files (gitignored)
├── config.ini      # User configuration (gitignored)
├── config.example.ini  # Example configuration
└── venv/           # Python virtual environment (gitignored)
```

## How It Works

1. SDDM lock screen triggers PAM
2. PAM runs `scripts/face_auth.sh` (sufficient — password fallback)
3. IR emitter turns on via `linux-enable-ir-emitter`
4. `cli/auth.py` captures IR frames
5. Frames are preprocessed (green channel, CLAHE, sharpening)
6. dlib HOG detects face and generates encoding
7. Encoding is compared against stored enrollment
8. Match → unlock; No match → password prompt

## License

MIT
