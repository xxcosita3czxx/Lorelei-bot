import asyncio
import logging
import os
from collections import defaultdict

import chardet
import toml

logger = logging.getLogger("configmanager")

#TODO WARNING THIS SHOULD BE DONE UNDER DEVELOPMENT BRANCH
#TODO Size of the config may be problem in the future, please consider loading on demand or using a database  # noqa: E501
#TODO Indexing could be a fix (can infinitely loop, or do on changes querried by set)  # noqa: E501
#TODO each saving of the config reloads all configs, maybe should be changed, just save it into the dict  # noqa: E501

# Retain the modularity of this manager with the indexer.


class ConfigManager:
    def __init__(self, config_dir, fallback_file=None):
        self.config_dir = config_dir
        self.config = defaultdict(dict) # type: ignore
        self.fallback_file = fallback_file
        self._load_all_configs()
        logger.info(f"Loaded {self}")

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
                        with open(file_path, 'w', encoding='utf-8') as f_utf8:
                            f_utf8.write(raw_data.decode(detected_encoding)) # type: ignore
                        with open(file_path, encoding='utf-8') as f:
                            self.config[id] = toml.load(f)
                except Exception as e:
                    logger.error(f"Failed to load {filename} with detected encoding. Error: {e}")  # noqa: E501
            except Exception as e:
                logger.error(f"Failed to load {filename}. Error: {e}")
        logger.debug(f"Loaded configs: {self.config}")

    def _load_config(self, id: str):
        id = str(id)
        file_path = os.path.join(self.config_dir, f"{id}.toml")
        try:
            with open(file_path, encoding="utf-8") as f:
                self.config[id] = toml.load(f)
        except UnicodeDecodeError as e:
            logger.warning(
                f"{id}.toml cannot be decoded with UTF-8! Error: {e}. Attempting to detect encoding...",  # noqa: E501
            )
            try:
                with open(file_path, 'rb') as f_binary:
                    raw_data = f_binary.read()
                    detected_encoding = chardet.detect(raw_data)['encoding']
                    logger.debug(f"Detected encoding for {id}.toml: {detected_encoding}")  # noqa: E501
                    with open(file_path, 'w', encoding='utf-8') as f_utf8:
                        f_utf8.write(raw_data.decode(detected_encoding)) # type: ignore
                    with open(file_path, encoding='utf-8') as f:
                        self.config[id] = toml.load(f)
            except Exception as e:
                logger.error(f"Failed to load {id}.toml with detected encoding. Error: {e}")  # noqa: E501
        except Exception as e:
            logger.error(f"Failed to load config for {id}: {e}")

    def _save_config(self, id:str):
        id = str(id)
        file_path = os.path.join(self.config_dir, f"{id}.toml")
        try:
            logger.debug(f"Saving config for {id} to {file_path}")
            with open(file_path, 'w') as f:
                toml.dump(self.config[id], f)
                logger.debug(f"Config for {id} saved successfully.")  # noqa: E501
        except Exception as e:
            logger.error(f"Failed to save config for {id}: {e}")

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

    def set(self, id:str, title, key, value):
        logger.debug(f"Setting {id}:{title}:{key} to {value}")
        id = str(id)
        if id not in self.config:
            self.config[id] = {}
        if title not in self.config[id]:
            self.config[id][title] = {}
        self.config[id][title][key] = value
        self._save_config(id)
        self._load_all_configs()  # Reload all configs after saving
        logger.debug(f"Set {id}:{title}:{key} to {value}")

    def delete(self, id:str, title=None, key=None):
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

    def set_index(self, index_name, conf_title, conf_key=None):
        pass

    def get_index(self, index_name):
        pass

async def _indexer():
    logger.info("Indexer started.")
    while True:
        # Placeholder for indexing logic
        await asyncio.sleep(300)  # Sleep for 5 minutes

gconfig = ConfigManager("data/guilds")
uconfig = ConfigManager("data/users")
lang = ConfigManager("data/lang","data/lang/en.toml")
themes = ConfigManager("data/themes","data/themes/Default.toml")
levels = ConfigManager("data/levels","data/levels/global.toml")

def userlang(userid) -> str:
    return uconfig.get(userid,"APPEARANCE","language")
