#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
cd "$SCRIPT_DIR/.." || exit
sudo pip install -r requirements.txt --break
sudo cp config.py devtools/config.py.bak
sudo git stash
sudo git pull
sudo cp devtools/config.py.bak config.py
sudo systemctl restart lorelei.service
journalctl -xfu lorelei.service