#!/bin/bash

sudo git pull
sudo systemctl restart lorelei.service
journalctl -xfu lorelei.service