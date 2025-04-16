#!/bin/bash

# Define mount points to check (customize as needed)
MOUNT_POINTS=(
  "/mnt/data"
  "/mnt/backup"
)

MISSING_MOUNTS=0

for mount_point in "${MOUNT_POINTS[@]}"; do
    if ! mountpoint -q "$mount_point"; then
        echo "Mount point $mount_point is not mounted."
        MISSING_MOUNTS=1
    fi
done

if [ "$MISSING_MOUNTS" -eq 1 ]; then
    echo "Running mount -a to remount all filesystems..."
    /bin/mount -a
fi

