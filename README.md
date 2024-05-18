# Lorelei

## Installation

### Systemd

You can use systemd (linux) to run this bot

1. Put it in your desired directory (preffering `/var/lorelei-bot`)
2. Edit `lorelei.service` to match user with permissions to the dir (or leave on root, which can be unsafe) and directory to the folder
3. Place lorelei.service into `/etc/systemd/system/`
4. Create file named `.secret.key` and put your token inside
5. Enable and start the service
```bash
sudo systemctl enable lorelei.service
sudo systemctl start lorelei.service
```
