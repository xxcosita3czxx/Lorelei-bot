import logging
import socket
import sys

import coloredlogs

import config

coloredlogs.install(
    level=config.loglevel,
    fmt='%(asctime)s HELPER: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

def send_command(command:str):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(('localhost', 9920))  # Connect to the bot's socket
            client.sendall(command.encode('utf-8'))
            if command.startswith("reload_all"):
                logging.info("Please wait, this may take a minute or two...")
            response = client.recv(1024).decode('utf-8')
            logging.info(response)

    except ConnectionRefusedError:
        logging.error("Bot is not running")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = ' '.join(sys.argv[1:])
        send_command(command)
    else:
        logging.error("Please provide a command to send.")
