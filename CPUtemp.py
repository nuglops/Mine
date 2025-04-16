import psutil

def check_cpu_temp():
    temps = psutil.sensors_temperatures()
    if 'coretemp' in temps:
        for entry in temps['coretemp']:
            if entry.label.startswith("Package id"):
                print(f"CPU Temp: {entry.current}°C")

check_cpu_temp()

