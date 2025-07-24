# Contributing to Lorelei Bot

Thank you for considering contributing to Lorelei Bot! Your contributions help make this project better for everyone.

## How to Contribute Code

Before we talk about the contributing of the code, i wanna introduce you to the system of the bot, how it works, so you can understand the code better, as i do not make much comments around the code myself.

### Bot behaviour

This bot is made using cogs and discord.py library, its startup is as follows:

- service file runs `run.py`
- `run.py` checks if `main.py` is running (main bot script)
- `main.py` is started by `run.py`
- `main.py` checks for required data like `.secret.key` with token, if not, tells the user.
- class `aclient()` gets run
- `aclient()` connects to gateway and sets idle status
- `aclient()` does `on_ready()` event
- `on_ready()` event starts loading cogs
- cogs get loaded based on priority, if no priority set, it goes from a -> z
- - if cog fails to load, displays failed and continues loading other
- cogs load from function `async def setup()`
- `on_ready()` starts activity status changing
- activity status sets discord bot to DND (or set status in `config.py`)
- `on_ready()` is complete and bot is loaded
- `on_ready()` starts helper which is accessible using `/devtools/helper_cli.py` or `/helper.py` (tui)

### Data / config management system

Bot uses a custom system for managing configs inside toml files, which makes it easier to edit, while not sacrificing on speed with optimalisations.
Its import is in /utils/configmanager.py, importable with `from utils.configmanager import ...`. I have 5 default data managers, gconfig, uconfig, lang, themes and levels. First 3 are most important:

1. gconfig - Config manager for guilds, files are in `/data/guilds/<guild id>.toml`, contains configs of each guild, e.g. auto role
2. uconfig - Config manager for users, files are in `/data/users/<user id>.toml`, contains configs and data of users, e.g. levels or language settings
3. lang - Language manager, contains all languages, they are in `/data/lang/<language>.toml`

Each of them contains functions (`<>` are required, `[]` are optional):

- `.get(<id>,<title>,<config>,[fallback])` - will get the info, you may optionally set fallback (language has fallback always as english, no need to set).
- `.set(<id>,<title>,<config>,<value>)` - will set the value.
- `.delete(<id>,[title],[config])` - will delete, should only be used when disabling configs for preserving space, instead of doing enable switch, usually used in `/commands/configuring/`.
- `_load_all_configs()` - This one is hidden, and is used to reload all configs after changing, please do not use it unless necessary (it is possible to call it outside)

Also they contain `.config` which is used for special occasions where we need more data for functions, like searching by channel id, its a variable containing json data of ALL configs.

### Configuring system (GuildConfig util)

We have quite easy system for creating configs for commands. Instead of need of single file, which when edited wrongly, can efficiently brick the whole bot, each command has its config within its file. Its better for modularity and for overall stability of the bot. We use class `GuildConfig()` which is importable from `/utils/guildconfig.py` with `from utils.guildconfig import GuildConfig`.

Its really easy to create a config, i advise checking out its functions for each type, but generaly, you create a variable containing `GuildConfig()` class, add new setting, and with the setting name, add options. Options follow consistent naming like `.add_option_<type>`

Example config creation:

```python
async def setup(bot:commands.Bot):
    cog = Example(bot)
    await bot.add_cog(cog)

    #Here we start the config creation
    configman = GuildConfig()
    configman.set_config_set("default") # you can use this to select which config system to use, we have only two, default, which is guildconfig, and user, which is userconfig. WE DONT NEED TO SET IT, UNLESS WE WANT DIFFERENT CONFIG SET THAN GUILDCONFIG
    configman.add_setting(
        category_name="Category",
        setting_name="Example",
        description="Example config test",
    )
    configman.add_option_bool(
        category_name="Category",
        setting_name="Example", # We need to set the same as in .add_setting(), first we create setting, then we add option
        name="Allow Example", # this is also used as key in json and as option name in embed
        button_title="Allow", # title of the button
        config_title="EXAMPLE", # Here comes the configuring system, here you add your config title and key
        config_key="example-allow",
        description="Allow example to do something",
    )
```

### How to Contribute

Okay so now you know few things, lets start on actualy contributing:

1. **Fork the Repository**: Start by forking the repository to your GitHub account.

2. **Clone the Repository**: Clone the forked repository to your local machine if you wanna use commands, else, just open on github directly.

    ```sh
    git clone https://github.com/your-username/Lorelei-bot.git
    cd Lorelei-bot
    ```

3. **Edit the Main Branch**: You don't need to create a new branch. Just edit the main branch in your fork.

4. **Setup your environment**: The most minimal environment is basicaly git, python and ruff, but if using VSC, i reccoment VSC-Essentials Extension pack

5. **Create a discord bot**: You should create your own discord bot for testing, its pretty much required for making new things, as you dont know how the bot will respond if you dont have one. Make sure you enable all intents.

6. **Create .secret.key**: Create `.secret.key` and put your token in there.

7. **Contribute!**: Make your changes, test the bot, and see if it worked.

8. **Commit Your Changes**: Commit your changes with a descriptive commit message.
   Upload it using commit button or with commands:

    ```sh
    git add .
    git commit -m "Adding Example commands"
    ```

9. **Push Your Changes**: Push your changes to your forked repository.
   When commiting, its already pushed, when using commands, use this:

    ```sh
    git push
    ```

10. **Create a Pull Request**: Go to the original repository on GitHub and create a pull request from your forked repository. Provide a clear description of the changes you made.

11. **Wait**: You can wait for your pull request to be reviewed and pulled, or it can be denied and you should repair things pointed out in the review. Also any unformated ruff rules get denied, you can enable those checks in actions -> ruff

## How to Contribute Translations

We welcome contributions to translate Lorelei Bot into different languages. Here are the steps to contribute translations:

1. **Fork the Repository**: Start by forking the repository to your GitHub account.

2. **Clone the Repository**: Clone the forked repository to your local machine if you wanna use commands, else, just open on github directly.

    ```sh
    git clone https://github.com/your-username/Lorelei-bot.git
    cd Lorelei-bot
    ```

3. **Edit the Main Branch**: You don't need to create a new branch. Just edit the main branch in your fork.

4. **Edit Language Files**: Navigate to the `data/lang` directory and edit the appropriate language file or create a new one if it doesn't exist. Use the existing files as a reference for the format. You may use `/devtools/translate-update.py <original language you translate from> <language youre translating into>` to get changes from the language. I advise you translate from en.toml, as its the newest always.

5. **Do Not Update Translation Progress Manually**: The translation progress percentage is updated automatically after editing the language files. **Do not update the percentage manually**.

6. **Commit Your Changes**: Commit your changes with a descriptive commit message.
   Upload it using commit button or with commands:

    ```sh
    git add .
    git commit -m "Add translation for <language>"
    ```

7. **Push Your Changes**: Push your changes to your forked repository.
   When commiting, its already pushed, when using commands, use this:

    ```sh
    git push
    ```

8. **Create a Pull Request**: Go to the original repository on GitHub and create a pull request from your forked repository. Provide a clear description of the changes you made.

## Reporting Issues

If you encounter any issues or have suggestions for improvements, please open an issue on GitHub. Provide as much detail as possible to help us understand and address the issue.

## Contact

If you have any questions or need further assistance, feel free to contact me at [cosita3cz@proton.me](mailto:cosita3cz@proton.me).

Thank you for your contributions!

---

**Note**: This project is licensed under the terms of the [Lorelei-bot License](LICENSE.md). By contributing to this project, you agree to the terms and conditions of the license.
