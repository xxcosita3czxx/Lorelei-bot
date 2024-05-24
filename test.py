import logging

from main import ConfigManager

gconfig = ConfigManager("data/guilds")
gconfig.set(999,"SECURITY","anti-invites",True)
logging.info(gconfig.get(999,"SECURITY","anti-invites"))
