# Lorelei

Open-Source discord bot in python, for people
> disclaimer: Youre permited to host it yourself for personal purposes like single server or testings, for more than 100 servers, message me on discord (@cosita3cz)

## Why?

Because having too much of bots is very annoying, every single one have different configurations, web dashboards, and you can get lost quickly in it. Also most good bots these days are paid and very limited for free (hope dyno stays free 🙏). This is where my bot comes with all inside discord. Its free, its open-source, and you can do alot with it, edit it for your own needs, or help other people by making your own commands to the main bot.

## How to contribute?

Everything about contributing is [here](https://github.com/xxcosita3czxx/Lorelei-bot/blob/main/CONTRIBUTING.md)

### Translation Progress

<!-- PLEASE DONT EDIT, GETS GENERATED AUTOMATICALLY -->

| Language | Progress |
|----------|----------|
| English (🕈☹♋︎♏︎□☹♋︎♏︎♎︎) | 100.00% |
| French (Français) | 91.36% |
| Czech (Česky) | 87.65% |
| English (LoLspek) | 44.44% |
| German (Deutsch) | 39.51% |
| Hungarian (Magyar) | 39.51% |
| Slovak (Slovensky) | 39.51% |
| Russian (Русский) | 33.33% |
| English (UwU) | 32.10% |
| Polish (Polski) | 16.05% |
| Albanian (Shqip) | 14.81% |
| Chinese (中文) | 14.81% |
| Finnish (Suomi) | 14.81% |
| Turkish (Türkçe) | 14.81% |

## Support the creator

You can support me by contributing to the repo

Or donating me any eth-based crypto to this wallet:
`0xAC0de1b07AF535B8a2ac060259E2d49d5c1DAfd5`

## Installation

### Systemd (linux)

You can use systemd (linux) to run this bot

1. Put it in your desired directory (preffering `/var/lorelei-bot`)
2. Edit `lorelei.service` to match user with permissions to the directory (or leave on root, which can be unsafe) and directory to the folder
3. Place `lorelei.service` into `/etc/systemd/system/`
4. Create file named `.secret.key` and put your token inside
5. Install dependencies

    ```bash
    pip install -r requirements.txt
    ```

    (if you wanna run it as root, place `sudo` before command)

6. Enable and start the service

    ```bash
    sudo systemctl enable lorelei.service
    sudo systemctl start lorelei.service
    ```

### Pterodactyl

You can also run it using pterodactyl.
For updater to work please check if your hosting does allow using git inside their eggs
If yes, please dont use builtin updater, and let the script do its own thing. If you prefer switch from the hosting, please disable autoupdate in the bot. If disabled, bot wont update itself automaticaly after period of time, but after restart.

1. Place repository into root of the pterodactyl
2. Add all requirements from `requirements.txt` into your settings
3. Set main file as `run.py`
4. Start with main.py

### Windows

Because of some features differing or not even existing im not willing to develop it for windows. Who even uses windows server these days for this.
