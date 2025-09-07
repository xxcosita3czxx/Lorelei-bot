import discord

##############################################

########### Log Level #############
#
# Available options
# "DEBUG"   - Shows debug info and up
# "INFO"    - Shows Info and up (Default)
# "WARNING" - Shows only Warning and up
# "ERROR"   - Show only error and fatals
# "FATAL"   - Only Fatal errors
loglevel = "DEBUG"
###################################
############ Status ###############
#
# UNCOMMENT ONLY ONE
#
# Offline status
#status = discord.Status.offline
#
# Online status
#status = discord.Status.online
#
# Do not Disturb status (default)
status = discord.Status.dnd
###################################
############ Language #############
#
# Changes default language
# en is default
language = "en"
###################################
########## Bug Reports ############
#
# Enabling of commands/other/bugreport.py
# If you dont want people to use bugreports
#
# If you dont want to see /bugreport entirely,
# rename commands/other/bugreport.py to something like bugreport.py.disabled
bugreport = True
###################################
############# Helper ##############
#
# Enables helper command, for bot
# management.
# Default = True
helper = True
#
# Helper port, default 9920
helperport = 9920
###################################
############# Shards ##############
#
# How many Shards to use?
# Default 1
shards = 1
###################################
########### AutoUpdate ############
#
# Only True or False
# True is default
autoupdate = True
###################################
########### Repository ############
#
# Repository url
# default is "xxcosita3czxx/Lorelei-bot"
repository = "xxcosita3czxx/Lorelei-bot"
###################################
########## Update Time ############
#
# EVERYTHING IN SECCONDS
#
# Time for Bot update (default 300)
bot_update = 300
#
# Time for IsAlive script ping (default 30)
Is_Alive_time = 30
###################################
######### Default Image ###########
#
# Default image to show when image object fails
#
def_image = "data/themes/fail.jpg"
###################################
######## Disable Commands #########
#
# Disable commands for the bot
#
disabler_mode = "bl"
# bl = Blacklist mode - disables specified
# wl = Whitelist mode - Only enables specified
enabled = []
disabled = []
###################################
########### Error Channel #########
#
# Server / Channel where should we send errors
#
error_channel = 1243929954744406137
###################################
