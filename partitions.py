import shutil
import logging

threshold = 90  # percent
mount_point = "/"  # root partition

total, used, free = shutil.disk_usage(mount_point)
percent_used = used / total * 100

if percent_used > threshold:
    logging.warning(f"Disk usage exceeded: {percent_used:.2f}% used on {mount_point}")

