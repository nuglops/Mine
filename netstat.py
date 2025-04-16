import psutil

for conn in psutil.net_connections(kind='inet'):
    if conn.status == 'LISTEN':
        print(f"PID {conn.pid} listening on {conn.laddr}")

