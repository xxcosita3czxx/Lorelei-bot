import logging
import socket
import sys

logger = logging.getLogger(name=__name__)
logger.setLevel("DEBUG")

def send_command(command):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(('localhost', 9920))  # Connect to the bot's socket
            client.sendall(command.encode('utf-8'))
            response = client.recv(1024).decode('utf-8')
            logger.info(response)

    except ConnectionRefusedError:
        logger.error("Bot is not running")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = ' '.join(sys.argv[1:])
        send_command(command)
    else:
        logger.error("Please provide a command to send.")
