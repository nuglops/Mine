#!/usr/bin/env bash

# Simple CUPS printer control menu
# Requires: lpstat, cupsdisable, cupsenable, cupsreject, cupsaccept

set -euo pipefail

# Ensure required commands exist
for cmd in lpstat cupsdisable cupsenable cupsreject cupsaccept; do
    command -v "$cmd" >/dev/null 2>&1 || {
        echo "Error: $cmd not found"
        exit 1
    }
done

# Get list of printers
mapfile -t PRINTERS < <(lpstat -a | awk '{print $1}')

if [[ ${#PRINTERS[@]} -eq 0 ]]; then
    echo "No printers found."
    exit 1
fi

echo "Available printers:"
PS3="Select a printer (or Ctrl+C to quit): "
select PRINTER in "${PRINTERS[@]}"; do
    [[ -n "$PRINTER" ]] && break
    echo "Invalid selection."
done

echo
echo "Selected printer: $PRINTER"
echo

PS3="Choose an action: "
select ACTION in \
    "Disable printer (stop printing)" \
    "Enable printer (resume printing)" \
    "Reject new jobs" \
    "Accept new jobs" \
    "Quit"
do
    case "$REPLY" in
        1)
            echo "Disabling printer $PRINTER..."
            cupsdisable -r "Disabled by admin script" "$PRINTER"
            break
            ;;
        2)
            echo "Enabling printer $PRINTER..."
            cupsenable "$PRINTER"
            break
            ;;
        3)
            echo "Rejecting jobs for $PRINTER..."
            cupsreject "$PRINTER"
            break
            ;;
        4)
            echo "Accepting jobs for $PRINTER..."
            cupsaccept "$PRINTER"
            break
            ;;
        5)
            echo "Exiting."
            exit 0
            ;;
        *)
            echo "Invalid choice."
            ;;
    esac
done

echo
echo "Current status:"
lpstat -p "$PRINTER" -l
