from main import ConfigManager

gconfig = ConfigManager("data/guilds")
gconfig.set("999","SECURITY","anti-invites",True)
test = gconfig.get("999","SECURITY","anti-invites")
#print(test)
