import psutil, time

while True:
    print("CPU:", psutil.cpu_percent(), "%")
    print("RAM:", psutil.virtual_memory().percent, "%")
    print("Disk:", psutil.disk_usage('/').percent, "%")
    print("-" * 30)
    time.sleep(10)

