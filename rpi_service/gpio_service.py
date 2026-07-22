#!/usr/bin/env python3
"""
gpio_service.py — Lightweight Raspberry Pi service for Smart Home Automation.

Replaces the heavy PyQt5 GUI with a headless service that:
  1. Connects to the Express server via Socket.IO
  2. Listens for heating status changes (socket_status events)
  3. Controls a red LED via GPIO (ON when heating is OFF, OFF when heating is ON)
  4. Reads DHT22 sensor data and POSTs it to the Express server periodically

Usage:
  python3 gpio_service.py                     # Normal mode (GPIO active)
  python3 gpio_service.py --dry-run           # Simulate GPIO with console logs
  python3 gpio_service.py --server-url http://192.168.1.7:3001
"""

import argparse
import logging
import threading
import time
import requests
import socketio

# ---------------------------------------------------------------------------
# Configuration defaults
# ---------------------------------------------------------------------------
DEFAULT_SERVER_URL = "http://192.168.1.7:3001"
RED_LED_PIN = 17       # GPIO pin for the red LED (BCM numbering)
DHT_SENSOR_PIN = 4     # GPIO pin for the DHT22 sensor
SENSOR_READ_INTERVAL = 10  # seconds between sensor readings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("gpio_service")


class RealGPIO:
    """Controls physical GPIO pins on a Raspberry Pi."""

    def __init__(self, led_pin):
        import RPi.GPIO as GPIO
        self.GPIO = GPIO
        self.led_pin = led_pin
        self.GPIO.setmode(GPIO.BCM)
        self.GPIO.setwarnings(False)
        self.GPIO.setup(self.led_pin, GPIO.OUT)
        self.GPIO.output(self.led_pin, self.GPIO.HIGH)
        log.info(f"GPIO initialized — red LED on pin {self.led_pin}")

    def led_on(self):
        self.GPIO.output(self.led_pin, self.GPIO.LOW)
        log.info("🔴 RED LED → ON  (heating is OFF)")

    def led_off(self):
        self.GPIO.output(self.led_pin, self.GPIO.HIGH)
        log.info("⚫ RED LED → OFF (heating is ON)")

    def cleanup(self):
        self.GPIO.cleanup()
        log.info("GPIO cleaned up")


class DryRunGPIO:
    """Simulates GPIO for testing on non-Pi machines."""

    def __init__(self, led_pin):
        self.led_pin = led_pin
        log.info(f"[DRY-RUN] GPIO initialized — red LED on pin {self.led_pin}")

    def led_on(self):
        log.info("[DRY-RUN] 🔴 RED LED → ON  (heating is OFF)")

    def led_off(self):
        log.info("[DRY-RUN] ⚫ RED LED → OFF (heating is ON)")

    def cleanup(self):
        log.info("[DRY-RUN] GPIO cleaned up")



class RealDHTSensor:
    """Reads from a physical DHT22 sensor."""

    def __init__(self, pin):
        import Adafruit_DHT
        self.sensor = Adafruit_DHT.DHT22
        self.pin = pin

    def read(self):
        import Adafruit_DHT
        humidity, temperature = Adafruit_DHT.read(self.sensor, self.pin)
        if humidity is not None and temperature is not None:
            return round(temperature, 2), round(humidity, 2)
        return None, None


class DryRunDHTSensor:
    """Simulates sensor readings for testing."""
    import random

    def __init__(self, pin):
        self.pin = pin

    def read(self):
        import random
        temp = round(random.uniform(18.0, 30.0), 2)
        hum = round(random.uniform(40.0, 80.0), 2)
        return temp, hum


class GPIOService:
    def __init__(self, server_url, gpio, sensor):
        self.server_url = server_url
        self.gpio = gpio
        self.sensor = sensor
        self.sio = socketio.Client(reconnection=True, reconnection_delay=2)
        self.current_status = None
        self._setup_socket_events()

    def _setup_socket_events(self):
        @self.sio.event
        def connect():
            log.info(f"✅ Connected to server via Socket.IO")

        @self.sio.event
        def disconnect():
            log.warning("❌ Disconnected from server — will auto-reconnect")

        @self.sio.on("socket_status")
        def on_status(data):
            """Called when the web app toggles the heating status."""
            status = data.get("status") if isinstance(data, dict) else None
            log.info(f"Received socket_status event: status={status}")

            if status == 0:
                self.gpio.led_on()
                self.current_status = 0
            elif status == 1:
                self.gpio.led_off()
                self.current_status = 1
            else:
                log.warning(f"Unknown status value: {status}")

        @self.sio.on("socket_temperature_And_Humidity")
        def on_sensor_data(data):
            log.debug(f"Received sensor data from server: {data}")

        @self.sio.on("socket_treshold")
        def on_treshold(data):
            log.debug(f"Received treshold update: {data}")

    def fetch_initial_status(self):
        """Fetch current heating status from the server on startup."""
        try:
            response = requests.get(f"{self.server_url}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    status = int(data[0].get("status", 0))
                    self.current_status = status
                    if status == 0:
                        self.gpio.led_on()
                    else:
                        self.gpio.led_off()
                    log.info(f"Initial heating status: {'ON' if status == 1 else 'OFF'}")
            else:
                log.warning(f"Failed to fetch initial status: HTTP {response.status_code}")
        except Exception as e:
            log.error(f"Error fetching initial status: {e}")

    def send_sensor_data(self):
        """Read DHT22 sensor and POST data to the Express server."""
        temperature, humidity = self.sensor.read()
        if temperature is not None and humidity is not None:
            try:
                payload = {"temperature": temperature, "humidity": humidity}
                response = requests.post(
                    f"{self.server_url}/sendSenzorTemperatureAndHumidity",
                    json=payload,
                    timeout=5,
                )
                if response.status_code == 200:
                    log.info(f"Sensor data sent — temp: {temperature}°C, hum: {humidity}%")
                else:
                    log.warning(f"Sensor POST failed: HTTP {response.status_code}")
            except Exception as e:
                log.error(f"Error sending sensor data: {e}")
        else:
            log.warning("Sensor read failed — got None values")

    def _sensor_loop(self):
        """Background loop that reads and sends sensor data periodically."""
        while True:
            try:
                self.send_sensor_data()
            except Exception as e:
                log.error(f"Sensor loop error: {e}")
            time.sleep(SENSOR_READ_INTERVAL)

    def start(self):
        """Start the service: connect Socket.IO, fetch initial status, start sensor loop."""
        log.info(f"Starting GPIO Service — server: {self.server_url}")

        # Fetch initial heating status
        self.fetch_initial_status()

        # Start sensor reading in a background thread
        sensor_thread = threading.Thread(target=self._sensor_loop, daemon=True)
        sensor_thread.start()
        log.info(f"Sensor loop started (every {SENSOR_READ_INTERVAL}s)")

        # Connect to Socket.IO (blocking — will auto-reconnect)
        try:
            self.sio.connect(self.server_url, transports=["websocket"])
            log.info("Socket.IO connected — waiting for events...")
            self.sio.wait()
        except KeyboardInterrupt:
            log.info("Shutting down...")
        except Exception as e:
            log.error(f"Socket.IO connection error: {e}")
        finally:
            self.gpio.cleanup()



def main():
    parser = argparse.ArgumentParser(description="Raspberry Pi GPIO Service for Smart Home")
    parser.add_argument(
        "--server-url",
        default=DEFAULT_SERVER_URL,
        help=f"Express server URL (default: {DEFAULT_SERVER_URL})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate GPIO operations (for testing on non-Pi machines)",
    )
    parser.add_argument(
        "--led-pin",
        type=int,
        default=RED_LED_PIN,
        help=f"GPIO pin for the red LED in BCM numbering (default: {RED_LED_PIN})",
    )
    parser.add_argument(
        "--sensor-pin",
        type=int,
        default=DHT_SENSOR_PIN,
        help=f"GPIO pin for the DHT22 sensor (default: {DHT_SENSOR_PIN})",
    )
    args = parser.parse_args()

    # Choose real or simulated hardware
    if args.dry_run:
        gpio = DryRunGPIO(args.led_pin)
        sensor = DryRunDHTSensor(args.sensor_pin)
    else:
        gpio = RealGPIO(args.led_pin)
        sensor = RealDHTSensor(args.sensor_pin)

    service = GPIOService(args.server_url, gpio, sensor)
    service.start()


if __name__ == "__main__":
    main()
