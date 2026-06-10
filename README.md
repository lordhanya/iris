<p align="center">
  <img src="https://img.shields.io/aur/version/iris?style=for-the-badge&logo=archlinux&color=1793D1" alt="AUR">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python">
</p>

<br>

<h1 align="center">
  <img src="https://raw.githubusercontent.com/lordhanya/iris/main/.github/logo.png" height="64" align="center">
  IRIS
</h1>

<h3 align="center"><code>Infrared Recognition & Identity System</code></h3>

<p align="center">
  <b>Password-less face unlock for SDDM</b> — optimized for Thinkpad IR cameras
</p>

<br>

---

## Features

- **Fast unlock** — recognizes your face in ~3 seconds via IR camera
- **IR-optimized** — green channel extraction, CLAHE, adaptive thresholding
- **Dark frame rejection** — ignores IR emitter flash frames automatically
- **Security checks** — skips face auth when lid is closed or over SSH
- **Snapshot capture** — saves failed auth images for review
- **Multi-layer failsafe** — never lock yourself out (emergency disable, password fallback)
- **IR emitter control** — integrates with `linux-enable-ir-emitter`

---

## Install

### AUR (recommended)

```bash
yay -S iris
```

### Manual (local checkout)

```bash
git clone https://github.com/lordhanya/iris
cd iris
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo pacman -S v4l-utils
yay -S linux-enable-ir-emitter
```

---

## Setup

### 1. Configure IR emitter

```bash
sudo linux-enable-ir-emitter configure
```

### 2. Configure IRIS

```bash
# AUR install:
mkdir -p ~/.config/iris
cp /usr/share/iris/config.example.ini ~/.config/iris/config.ini

# Local checkout:
cp config.example.ini config.ini
```

### 3. Enroll your face

```bash
iris-enroll --force
```

### 4. Test authentication

```bash
iris-auth --timeout 10
```

### 5. Integrate with SDDM

```bash
sudo /usr/share/iris/scripts/install-pam.sh
```

---

## Usage

### Lock and unlock

```bash
loginctl lock-session
```

Press `Enter` at the lock screen — IRIS authenticates and unlocks automatically.

### Emergency disable

```bash
touch /tmp/face-auth-emergency-disable
```

To re-enable: `rm /tmp/face-auth-emergency-disable`

---

## Failsafe

| Method | Command |
|--------|---------|
| Emergency disable | `touch /tmp/face-auth-emergency-disable` |
| Config disable | Set `disabled = true` in `~/.config/iris/config.ini` |
| Restore PAM backup | `sudo cp /etc/pam.d/sddm.backup /etc/pam.d/sddm` |
| Uninstall PAM | `sudo /usr/share/iris/scripts/uninstall-pam.sh` |

---

## How It Works

1. SDDM lock screen triggers PAM
2. PAM runs `scripts/face_auth.sh` (sufficient — password fallback)
3. IR emitter turns on via `linux-enable-ir-emitter`
4. `cli/auth.py` captures IR frames
5. Frames are preprocessed (green channel, CLAHE, sharpening)
6. dlib HOG detects face and generates encoding
7. Encoding is compared against stored enrollment
8. Match → unlock; No match → password prompt

---

## Project Structure

```
/usr/share/iris/
├── cli/              # Entry points (auth.py, enroll.py)
├── core/             # Library modules
├── scripts/          # PAM script, installer, utilities
├── models/           # dlib face detection/recognition models
└── docs/             # Documentation

~/.config/iris/
└── config.ini        # User configuration

~/.local/share/iris/
├── data/             # Face encodings
└── logs/             # Log files
```

---

## License

MIT — see [LICENSE](LICENSE)
