#!/bin/bash

# === Configuration ===
SERVICE_NAME="falcon-sensor"
RAM_THRESHOLD=80  # RAM usage threshold in percentage
LOG_FILE="/var/log/falconsensor_monitor.log"
CHECK_INTERVAL=60  # Time between checks in seconds

# === Function to get process memory usage in percentage ===
get_ram_usage() {
    local pid=$1
    local proc_rss=$(grep VmRSS /proc/$pid/status 2>/dev/null | awk '{print $2}')
    local total_mem=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    if [[ -n "$proc_rss" && -n "$total_mem" ]]; then
        echo $(( 100 * proc_rss / total_mem ))
    else
        echo 0
    fi
}

# === Function to log messages ===
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# === Monitor Loop ===
log "Started FalconSensor RAM monitor."

while true; do
    pid=$(pgrep -f "falcon-sensor")

    if [[ -n "$pid" ]]; then
        usage=$(get_ram_usage "$pid")
        if (( usage > RAM_THRESHOLD )); then
            log "High RAM usage detected: ${usage}%. Restarting $SERVICE_NAME..."
            systemctl restart "$SERVICE_NAME"
            if [[ $? -eq 0 ]]; then
                log "Service '$SERVICE_NAME' restarted successfully."
            else
                log "Failed to restart service '$SERVICE_NAME'."
            fi
        fi
    else
        log "FalconSensor process not found."
    fi

    sleep "$CHECK_INTERVAL"
done
