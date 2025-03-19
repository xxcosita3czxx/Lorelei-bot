import logging
import os
from collections import defaultdict

import chardet
import coloredlogs
import toml

import config

coloredlogs.install(
    level=config.loglevel,
    fmt='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

logger = logging.getLogger("configmanager")

class ConfigManager:
    def __init__(self, config_dir, fallback_file=None):
        self.config_dir = config_dir
        self.config = defaultdict(dict)
        self.fallback_file = fallback_file
        self._load_all_configs()

    def _load_all_configs(self):
        logger.debug("Loading all configs...")
        for filename in os.listdir(self.config_dir):
            try:
                if filename.endswith('.toml'):
                    id = filename[:-5]  # Remove the .toml extension to get the ID
                    file_path = os.path.join(self.config_dir, filename)
                    with open(file_path,encoding="utf-8") as f:
                        self.config[id] = toml.load(f)
            except UnicodeDecodeError as e:
                logger.warning(
                    f"{filename} cannot be decoded with UTF-8! Error: {e}. Attempting to detect encoding...",  # noqa: E501
                )
                try:
                    with open(file_path, 'rb') as f_binary:
                        raw_data = f_binary.read()
                        detected_encoding = chardet.detect(raw_data)['encoding']
                        logger.debug(f"Detected encoding for {filename}: {detected_encoding}")  # noqa: E501
                        self.config[id] = toml.loads(raw_data.decode(detected_encoding))  # noqa: E501
                except Exception as e:
                    logger.error(f"Failed to load {filename} with detected encoding. Error: {e}")  # noqa: E501
        logger.debug(f"Loaded configs: {self.config}")

    def get(self, id, title, key, default=None):
        id = str(id)
        logger.debug(f"Getting {id}:{title}:{key}")
        result = self.config.get(id, {}).get(title, {}).get(key, default)
        if result is None and self.fallback_file:
            with open(self.fallback_file) as f:
                fallback_config = toml.load(f)
            fallback_result = fallback_config.get(title, {}).get(key, default)
            if fallback_result is not None:
                logger.debug("Giving fallback result...")
                result = fallback_result
        logger.debug("Final result: " + str(result))
        return result

    def set(self, id, title, key, value):
        logger.debug(f"Setting {id}:{title}:{key} to {value}")
        if id not in self.config:
            self.config[id] = {}
        if title not in self.config[id]:
            self.config[id][title] = {}
        self.config[id][title][key] = value
        self._save_config(id)
        self._load_all_configs()  # Reload all configs after saving
        logger.debug(f"Set {id}:{title}:{key} to {value}")

    def _save_config(self, id):
        id = str(id)
        file_path = os.path.join(self.config_dir, f"{id}.toml")
        try:
            logger.debug(f"Saving config for {id} to {file_path}")
            with open(file_path, 'w') as f:
                toml.dump(self.config[id], f)
        except Exception as e:
            logger.error(f"Failed to save config for {id}: {e}")

    def delete(self, id, title=None, key=None):
        id = str(id)
        logger.debug(f"Deleting {id}:{title}:{key}")
        if id in self.config:
            if title and key:
                if title in self.config[id] and key in self.config[id][title]:
                    del self.config[id][title][key]
                    if not self.config[id][title]:  # Clean up empty title section
                        del self.config[id][title]
            elif title:
                if title in self.config[id]:
                    del self.config[id][title]
            else:
                del self.config[id]
            self._save_config(id)
            self._load_all_configs()  # Reload all configs after saving
        logger.debug(f"Deleted {id}:{title}:{key}")

gconfig = ConfigManager("data/guilds")
uconfig = ConfigManager("data/users")
lang = ConfigManager("data/lang","data/lang/en.toml")
themes = ConfigManager("data/themes","data/themes/Default.toml")
levels = ConfigManager("data/levels","data/levels/global.toml")

def userlang(userid) -> str:
    return uconfig.get(userid,"APPEARANCE","language")
