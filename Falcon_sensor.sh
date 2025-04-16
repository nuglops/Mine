import psutil
import time
import logging
import subprocess
from datetime import datetime

# Configuration
SERVICE_NAME = "falcon-sensor"  # Adjust if different on your system
RAM_THRESHOLD = 80  # in percentage
CHECK_INTERVAL = 60  # seconds between checks
LOG_FILE = "/var/log/falconsensor_monitor.log"  # Make sure script has permission to write here

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_falconsensor_pid():
    """Return PID of the falcon-sensor process (if running)."""
    for proc in psutil.process_iter(['pid', 'name']):
        if "falcon-sensor" in proc.info['name'].lower():
            return proc.info['pid']
    return None

def get_process_ram_usage(pid):
    """Return RAM usage percentage of the process with given PID."""
    process = psutil.Process(pid)
    mem_info = process.memory_info()
    total_mem = psutil.virtual_memory().total
    return (mem_info.rss / total_mem) * 100

def restart_service():
    """Restart the FalconSensor service using systemctl (Linux)."""
    try:
        subprocess.run(["sudo", "systemctl", "restart", SERVICE_NAME], check=True)
        logging.info(f"Service '{SERVICE_NAME}' restarted due to high RAM usage.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to restart service '{SERVICE_NAME}': {e}")

def monitor():
    logging.info("Started FalconSensor RAM monitor.")
    while True:
        pid = get_falconsensor_pid()
        if pid:
            try:
                usage = get_process_ram_usage(pid)
                logging.debug(f"FalconSensor RAM usage: {usage:.2f}%")
                if usage > RAM_THRESHOLD:
                    logging.warning(f"High RAM usage detected: {usage:.2f}%. Restarting service.")
                    restart_service()
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logging.error(f"Error accessing FalconSensor process: {e}")
        else:
            logging.warning("FalconSensor process not found.")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()

