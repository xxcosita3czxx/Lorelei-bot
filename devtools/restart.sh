#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
cd "$SCRIPT_DIR/.." || exit
sudo pip install -r requirements.txt --break
sudo cp config.py ../config.py.bak
sudo cp -r data ../data.bak/
sudo rm -rf ../data.bak/lang
sudo git stash
sudo git pull
sudo mv ../config.py.bak config.py
sudo mv ../data.bak/* ./data
sudo systemctl restart lorelei.service
journalctl -xfu lorelei.service