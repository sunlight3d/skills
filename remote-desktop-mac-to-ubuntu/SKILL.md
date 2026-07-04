---
name: remote-desktop-mac-to-ubuntu
description: Troubleshoot, configure, and establish remote desktop connections from macOS to Ubuntu Desktop (GNOME/Wayland). Use this skill when the user wants to connect from Mac to Ubuntu, is having RDP/VNC connection issues (such as protocol negotiation failures, NLA errors, port conflicts, or crashes), or wants to configure native remote desktop access.
---

# Remote Desktop macOS to Ubuntu (RDP/Wayland)

This skill provides a systematic troubleshooting guide and configuration reference for establishing a high-performance Remote Desktop connection from macOS to Ubuntu Desktop (specifically Ubuntu 22.04+ using GNOME and Wayland).

## Core Concepts

1. **GND (GNOME Remote Desktop)**: Modern Ubuntu uses `gnome-remote-desktop` as its native Remote Desktop server. It supports RDP (port 3389) out of the box and is compatible with the Wayland display server.
2. **Wayland Compatibility**: Traditional VNC servers (like `vino` or `x11vnc`) do not work natively under Wayland. Always prefer RDP for Wayland sessions.
3. **User-level Service**: GNOME Remote Desktop runs as a systemd user service (`gnome-remote-desktop.service`). To control it via SSH, you must set `XDG_RUNTIME_DIR`.

---

## Troubleshooting Guide

### 1. Conflict with `xrdp`
If `xrdp` is installed, it binds to port 3389 and conflicts with `gnome-remote-desktop`. Because `xrdp` attempts to start a new X11 session, it will crash or fail to connect when a user is already logged in on Wayland.

**Fix**:
1. Stop and disable `xrdp` completely:
   ```bash
   sudo systemctl disable --now xrdp xrdp-sesman
   ```
2. Restart the native GNOME Remote Desktop user service:
   ```bash
   export XDG_RUNTIME_DIR=/run/user/$(id -u)
   systemctl --user restart gnome-remote-desktop
   ```

### 2. Network Level Authentication (NLA) Mismatch
GNOME Remote Desktop requires NLA by default. If the client has NLA disabled, the connection fails during security negotiation.
- **Symptom (Ubuntu Logs)**: `[WARN][com.freerdp.core.connection] - [rdp_server_accept_nego]: server supports only NLA Security` followed by `Protocol security negotiation failure`.
- **Symptom (Client)**: Error like `Network Level Authentication (NLA) needs to be disabled on the server`.
- **Fix**: Open your client configuration (e.g., Parallels Client -> Advanced Settings) and **Enable/Check** "Network Level Authentication".

### 3. Autodetect RTT Crash (Parallels Client Bug)
Certain clients send bandwidth auto-detection packets that crash the FreeRDP library on Ubuntu.
- **Symptom (Ubuntu Logs)**: `[ERROR][com.freerdp.core.autodetect] - [autodetect_recv_rtt_measure_response]: autodetectRspPdu->headerLength != 0x06 [0x08]`.
- **Fix**: 
  - On the client side (e.g., Parallels Client), go to the **Experience** tab and change "Choose your connection speed to optimize performance" from **Auto-Detect** to a fixed option (e.g., **LAN (10 Mbps or higher)**).
  - Alternatively, switch to a more compliant RDP client like **Microsoft Remote Desktop** (Windows App).

### 4. DNS Resolution `.local` Issues
macOS applications sometimes fail to resolve multicast DNS names (Bonjour) like `hostname.local` even though standard tools (like ping) can resolve them.
- **Fix**: Resolve the IP address of the Ubuntu machine manually:
  ```bash
  hostname -I
  ```
  Then use the IP address directly in the RDP client connection settings.

---

## Reference Commands

Run these commands on the Ubuntu machine (e.g., via SSH) to inspect or modify configuration.

### Check Port Bindings
Identify which process is listening on the RDP port (3389):
```bash
sudo ss -tulnp | grep 3389
```

### Control the Service
Since GNOME Remote Desktop runs as a user service, you must export `XDG_RUNTIME_DIR` when logged in via SSH:
```bash
export XDG_RUNTIME_DIR=/run/user/$(id -u)

# Check status
systemctl --user status gnome-remote-desktop --no-pager

# Restart
systemctl --user restart gnome-remote-desktop
```

### Configure Credentials and Security
Use `grdctl` to manage GNOME Remote Desktop settings:
```bash
export XDG_RUNTIME_DIR=/run/user/$(id -u)

# Show current configuration (hides credentials by default)
grdctl status

# Show status with credentials
grdctl status --show-credentials

# Set RDP credentials
grdctl rdp set-credentials <username> <password>

# Clear RDP credentials
grdctl rdp clear-credentials
```
