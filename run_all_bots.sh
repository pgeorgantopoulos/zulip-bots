#!/bin/bash
# ---------------------------
# Run Zulip bots with dynamic repo path
# ---------------------------

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd $SCRIPT_DIR

<path/to/python> $SCRIPT_DIR/bot.py --config_path $SCRIPT_DIR/novel-objects-arXiv
<path/to/python> $SCRIPT_DIR/bot.py --config_path $SCRIPT_DIR/physicscv-arXiv

# Capture exit status
status=$?
if [ $status -eq 0 ]; then
    echo "Zulip bots executed successfully at $(date)" >> "$SCRIPT_DIR/.last_cron_status"
else
    echo "Zulip bots FAILED (exit code $status) at $(date)" >> "$SCRIPT_DIR/.last_cron_status"
fi
