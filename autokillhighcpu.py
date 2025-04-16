import psutil

cpu_limit = 80.0

for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
    try:
        cpu = proc.cpu_percent(interval=0.1)
        if cpu > cpu_limit:
            print(f"Killing {proc.info['name']} (PID {proc.pid}) using {cpu:.2f}% CPU")
            proc.kill()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

