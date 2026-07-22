# Raspberry Pi Setup — Smart Home Automation

This guide explains how to set up the Raspberry Pi to run the **React web app** (in Chromium kiosk mode) and the **GPIO service** (red LED + DHT22 sensor).

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Raspberry Pi                    │
│                                                  │
│   ┌──────────────┐    ┌──────────────────────┐  │
│   │ gpio_service  │    │ Chromium (kiosk)     │  │
│   │ (Python)      │    │ → React App          │  │
│   │               │    │                      │  │
│   │ • Red LED     │    │ • Dashboard UI       │  │
│   │ • DHT22       │    │ • Toggle heating     │  │
│   │ • Socket.IO   │    │ • View temp/humidity │  │
│   └──────┬───────┘    └──────────┬───────────┘  │
│          │                       │               │
│          └───────────┬───────────┘               │
│                      │ HTTP / WebSocket           │
└──────────────────────┼──────────────────────────┘
                       │
              ┌────────▼────────┐
              │  Express Server  │
              │  (port 3001)     │
              │  + MongoDB       │
              └─────────────────┘
```

## Prerequisites

- Raspberry Pi (3B+ or later recommended) with Raspberry Pi OS
- Display connected to the Pi (HDMI or DSI)
- Red LED + 220Ω resistor
- DHT22 temperature/humidity sensor
- Node.js 18+ (for building the React app or running `npm start`)
- Python 3.7+

## Hardware Wiring

### Red LED
| LED Pin    | Raspberry Pi (BCM) | Physical Pin |
|------------|---------------------|--------------|
| Anode (+)  | GPIO 17             | Pin 11       |
| Cathode (-)| GND                 | Pin 6        |

> **Note:** Place a 220Ω resistor between GPIO 17 and the LED anode.

### DHT22 Sensor
| DHT22 Pin | Raspberry Pi (BCM) | Physical Pin |
|-----------|---------------------|--------------|
| VCC       | 3.3V                | Pin 1        |
| Data      | GPIO 4              | Pin 7        |
| GND       | GND                 | Pin 9        |

> **Note:** Place a 10kΩ pull-up resistor between VCC and the Data pin.

## Installation

### 1. Clone the project on the Raspberry Pi

```bash
git clone <your-repo-url>
cd BETA_Vocal_Home_Automation
```

### 2. Install Python dependencies

```bash
cd rpi_service
pip3 install -r requirements.txt
sudo pip3 install RPi.GPIO Adafruit_DHT
```

### 3. Install and build the React app

```bash
cd ../web_client/my-app
npm install
```

**Option A — Serve the production build (recommended for Pi):**
```bash
npm run build
sudo npm install -g serve
serve -s build -l 3000
```

**Option B — Run the dev server:**
```bash
npm start
```

### 4. Configure the server URL

Edit `web_client/my-app/.env`:
```
REACT_APP_SERVER_URL=http://<YOUR_SERVER_IP>:3001
```

Edit `rpi_service/start.sh`:
```bash
SERVER_URL="http://<YOUR_SERVER_IP>:3001"
REACT_APP_URL="http://localhost:3000"   # or wherever the React app is served
```

## Running

### Manual start
```bash
cd rpi_service
chmod +x start.sh
./start.sh
```

### Testing without hardware (dry-run)
```bash
python3 gpio_service.py --dry-run --server-url http://192.168.1.7:3001
```

### Auto-start on boot (systemd)

Create `/etc/systemd/system/smarthome.service`:

```ini
[Unit]
Description=Smart Home GPIO Service + Kiosk
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
ExecStart=/home/pi/BETA_Vocal_Home_Automation/rpi_service/start.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=graphical.target
```

Enable it:
```bash
sudo systemctl enable smarthome.service
sudo systemctl start smarthome.service
```

## How It Works

1. **GPIO Service** connects to the Express server via Socket.IO
2. When someone toggles heating **OFF** in the React web app:
   - Express server updates MongoDB and emits `socket_status` with `{status: 0}`
   - GPIO Service receives the event → turns **red LED ON**
   - React app updates the UI toggle + shows a red LED indicator dot
3. When someone toggles heating **ON**:
   - Express emits `socket_status` with `{status: 1}`
   - GPIO Service → turns **red LED OFF**
4. Every 10 seconds, the GPIO Service reads the DHT22 sensor and POSTs temperature/humidity to the Express server, which broadcasts it to all connected React clients via Socket.IO

## GPIO Pin Configuration

You can customize the pins via command-line arguments:

```bash
python3 gpio_service.py --led-pin 18 --sensor-pin 4 --server-url http://192.168.1.7:3001
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| LED doesn't turn on | Check wiring, verify GPIO pin number, run with `--dry-run` to test logic |
| No sensor data | Verify DHT22 wiring, check `Adafruit_DHT` is installed |
| Chromium shows error | Verify React app is running and the URL in `start.sh` is correct |
| Socket.IO won't connect | Check Express server is running and CORS allows `*` |
| Screen goes blank | `xset s off && xset -dpms` to disable screen blanking |
