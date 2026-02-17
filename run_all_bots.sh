#!/bin/bash
# ---------------------------
# Run Zulip bots with dynamic repo path
# ---------------------------

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd $SCRIPT_DIR

# /home/panos/.conda_envs/zulip-bots/bin/python $SCRIPT_DIR/run_bot.py --config_path $SCRIPT_DIR/novel-objects-arXiv
/home/panos/.conda_envs/zulip-bots/bin/python $SCRIPT_DIR/run_bot.py --config_path $SCRIPT_DIR/physicscv-arXiv

# Capture exit status
status=$?
if [ $status -eq 0 ]; then
    echo "Zulip bots executed successfully at $(date)" >> "$SCRIPT_DIR/run_all_bots.cronjob_log"
else
    echo "Zulip bots FAILED (exit code $status) at $(date)\n" >> "$SCRIPT_DIR/run_all_bots.cronjob_log"
fi
