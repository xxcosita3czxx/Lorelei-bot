#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
cd "$SCRIPT_DIR/.." || exit

cp config.py devtools/config.py.bak
git stash
sudo git pull
cp devtools/config.py.bak config.py
sudo systemctl restart lorelei.service
journalctl -xfu lorelei.service