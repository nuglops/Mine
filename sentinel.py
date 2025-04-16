## Work in Progress
## need to replace "YOUR_ABUSEIPDB_API_KEY" with your actual API key.
## Run the script as root (or via systemd with permissions) for iptables to work.
## Make sure the machine has geoiplookup installed:
##                sudo apt install geoip-bin          
import psutil
import time
import socket
import logging
import subprocess
import requests

# === CONFIG ===
LOG_FILE = "/var/log/network_monitor.log"
CHECK_INTERVAL = 10
ABUSEIPDB_API_KEY = "YOUR_ABUSEIPDB_API_KEY"
WHITELISTED_PROCESSES = {"firefox", "chrome", "sshd"}
SUSPICIOUS_PORT_THRESHOLD = 49152

# === Logging Setup ===
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_event(message):
    print(message)
    logging.warning(message)

def is_ip_blacklisted(ip):
    try:
        response = requests.get(
            f"https://api.abuseipdb.com/api/v2/check",
            headers={"Key": ABUSEIPDB_API_KEY, "Accept": "application/json"},
            params={"ipAddress": ip, "maxAgeInDays": 30}
        )
        data = response.json()
        score = data["data"]["abuseConfidenceScore"]
        return score > 50, score
    except Exception as e:
        logging.error(f"AbuseIPDB error: {e}")
        return False, 0

def geoip_lookup(ip):
    try:
        output = subprocess.check_output(["geoiplookup", ip], universal_newlines=True)
        return output.strip()
    except subprocess.CalledProcessError:
        return "GeoIP lookup failed"

def block_ip(ip):
    try:
        subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True)
        logging.info(f"Blocked IP {ip} via iptables")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to block IP {ip}: {e}")

def is_suspicious_connection(conn, proc_name):
    if conn.status != psutil.CONN_ESTABLISHED or not conn.raddr:
        return False
    rport = conn.raddr.port
    rhost = conn.raddr.ip
    if proc_name not in WHITELISTED_PROCESSES:
        return True
    if rport >= SUSPICIOUS_PORT_THRESHOLD:
        return True
    if not rhost.startswith(("192.", "10.", "172.")):
        return True
    return False

def monitor_network():
    logging.info("Started enhanced network monitor.")
    seen = set()

    while True:
        for conn in psutil.net_connections(kind="inet"):
            pid = conn.pid
            if not pid or not conn.raddr:
                continue
            try:
                proc = psutil.Process(pid)
                proc_name = proc.name()
                remote_ip = conn.raddr.ip
                unique_id = (proc_name, remote_ip, conn.raddr.port)

                if unique_id in seen:
                    continue
                if is_suspicious_connection(conn, proc_name):
                    log_event(f"[!] Suspicious connection: {proc_name} ({pid}) -> {remote_ip}:{conn.raddr.port}")

                    # GeoIP lookup
                    geo = geoip_lookup(remote_ip)
                    log_event(f"[GeoIP] {remote_ip} = {geo}")

                    # IP Blacklist check
                    blacklisted, score = is_ip_blacklisted(remote_ip)
                    if blacklisted:
                        log_event(f"[⚠️ BLACKLISTED] {remote_ip} - Abuse Score: {score}")
                        block_ip(remote_ip)
                    else:
                        log_event(f"[Clean IP] {remote_ip} - Abuse Score: {score}")

                    seen.add(unique_id)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_network()
