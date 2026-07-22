#!/bin/bash
# =============================================================================
# start.sh — Raspberry Pi Startup Script
#
# Launches:
#   1. gpio_service.py (headless GPIO + sensor service)
#   2. Chromium in kiosk mode pointing to the React app
#
# Usage:
#   chmod +x start.sh
#   ./start.sh
#
# For auto-start on boot, add to /etc/rc.local or create a systemd service.
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------------------
# Configuration — Edit these to match your setup
# ---------------------------------------------------------------------------
SERVER_URL="http://192.168.1.7:3001"
REACT_APP_URL="http://192.168.1.7:3000"   # Where the React app is served
LED_PIN=17                                  # BCM pin for red LED
SENSOR_PIN=4                                # BCM pin for DHT22

# ---------------------------------------------------------------------------
# 1. Start the GPIO service in the background
# ---------------------------------------------------------------------------
echo "🚀 Starting GPIO service..."
cd "$SCRIPT_DIR"
python3 gpio_service.py \
    --server-url "$SERVER_URL" \
    --led-pin "$LED_PIN" \
    --sensor-pin "$SENSOR_PIN" \
    &
GPIO_PID=$!
echo "   GPIO service PID: $GPIO_PID"

# Give the service a moment to connect
sleep 2

# ---------------------------------------------------------------------------
# 2. Launch Chromium in kiosk mode
# ---------------------------------------------------------------------------
echo "🖥️  Launching Chromium kiosk mode..."

# Disable screen blanking / screensaver
xset s off 2>/dev/null || true
xset -dpms 2>/dev/null || true
xset s noblank 2>/dev/null || true

# Hide the mouse cursor after 5 seconds of inactivity
unclutter -idle 5 &

# Remove Chromium crash flags (in case of unclean shutdown)
sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' \
    ~/.config/chromium/Default/Preferences 2>/dev/null || true
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' \
    ~/.config/chromium/Default/Preferences 2>/dev/null || true

# Launch Chromium in kiosk (fullscreen) mode
chromium-browser \
    --noerrdialogs \
    --disable-infobars \
    --kiosk \
    --incognito \
    --disable-translate \
    --no-first-run \
    --fast \
    --fast-start \
    --disable-features=TranslateUI \
    --disk-cache-size=1 \
    "$REACT_APP_URL"

# ---------------------------------------------------------------------------
# Cleanup on exit
# ---------------------------------------------------------------------------
echo "Shutting down GPIO service..."
kill $GPIO_PID 2>/dev/null || true
echo "Done."
