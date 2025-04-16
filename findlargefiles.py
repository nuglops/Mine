import os

directory = "/var/log"
size_limit_mb = 100

for root, _, files in os.walk(directory):
    for f in files:
        path = os.path.join(root, f)
        try:
            size = os.path.getsize(path) / (1024 * 1024)
            if size > size_limit_mb:
                print(f"{path} - {size:.2f} MB")
        except:
            pass

