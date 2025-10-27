import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('.')

from arXiv_bot.arXiv_bot import *



p = argparse.ArgumentParser()
p.add_argument("--config_path", type=str, required=True)
args = p.parse_args()
BOT_DIR = args.config_path

CONFIG_FILE = os.path.join(BOT_DIR,"config.yaml")
ZULIPRC_FILE = os.path.join(BOT_DIR,".zuliprc")

run_once(CONFIG_FILE, ZULIPRC_FILE, BOT_DIR)
