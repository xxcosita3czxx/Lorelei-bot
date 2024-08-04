"""COSITA TOOLKIT."""
#########################################
#                                       #
#                CosTK                  #
#           - by cosita3cz              #
#                                       #
#########################################

###  Config  ###############################################
loglevel="INFO"
# (Available: "DEBUG", "INFO", "WARNING", "ERROR", "FATAL")
update_branch="main"
# (Available: "main", "devel")
############################################################

'''
MIT License

Copyright (c) 2023 xxcosita3czxx

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

#------------------------------------------------------#

class Status:

    """Statuses that code uses."""

    class Requests:

        """Requests statuses, so ruff wont complaint about magic value."""

        SUCCESS = 200
        NOT_FOUND = 404
        UNAUTHORISED = 403
    STANDBY = 100
    SUCCESS = 101
    SUCCESS_COMP = 102
    ERR_UNK = 400
    SYNTAX = 301
    BAD_OS = 402
    NOT_FOUND = 404
############   MODULE IMPORTS   ############

try:
    import logging
except ImportError:
    print ("FATAL: cannot import logging")  # noqa: T201

try:
    import coloredlogs
    coloredlogs.install(
        level=loglevel,
        fmt='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

except ImportError:
    logging.warning("will not be using colors, as the module cannot be found")

try:
    import platform

except ImportError:
    logging.fatal("Failed to import base module platform")

try:

    if platform.system() == "Windows":
        import ctypes

        import win32gui

    else:
        logging.debug("not importing windows depends")

except ImportError:
    logging.warning("Windows Dependendencies not found, could have limitations")

try:
    import subprocess

except ImportError:
    logging.warning("Module subproccess not found, could have limitations")

try:
    import netifaces

except ImportError:
    logging.warning("Module netifaces not found, could have limitations")

try:
    import psutil

except ImportError:
    logging.warning("Module psutil not found, could have limitations")

try:
    import socket

except ImportError:
    logging.warning("Module socket not found, could have limitations")

try:
    import threading

except ImportError:
    logging.warning("Module threading not found, could have limitations")

try:
    import requests

except ImportError:
    logging.warning("Module requests not found, could have limitations")

try:
    import json

except ImportError:
    logging.warning("Module json not found, could have limitations")

try:
    from time import gmtime, strftime

except ImportError:
    logging.warning("Module time not found, could have limitations")

try:
    import os

except ImportError:
    logging.warning("Module os not found, could have limitations")

try:
    import base64

except ImportError:
    logging.warning("Module base64 not found, could have limitations")


def update_script_from_github(owner:str, repo:str,branch:str, file_path:str, local_file_path:str):  # noqa: E501
    """Update local script from GitHub repository if it's different from the current version."""  # noqa: E501
    try:
        orig_dir = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Cosita-Toolkit-Updater",
        }
        response = requests.get(api_url, headers=headers,timeout=60)
        response.raise_for_status()

        github_content = base64.b64decode(response.json()["content"]).decode("utf-8")  # noqa: E501

        if os.path.exists(local_file_path):
            with open(local_file_path) as file:
                local_content = file.read()

            if github_content == local_content:
                logging.info("No update required. Local script is up to date.")
                return Status.STANDBY
        else:
            logging.info("Local script not found. Downloading from GitHub.")

        with open(local_file_path, "w") as file:
            file.write(github_content)

        logging.info("Script updated successfully.")
        return Status.SUCCESS

    except requests.RequestException as e:
        logging.error(f"Failed to fetch the script from GitHub: {e}")
        return Status.ERR_UNK
    except Exception as e:
        logging.error(f"Updater error: {e}")
        return Status.ERR_UNK
    finally:
        os.chdir(orig_dir)


# DEPRECATED, yet still DONT DELETE.
#def _main():
#    logging.warning("yet not supported")


############   FUNCTIONS   ############

class MemMod:

    """Requires windows, bcs linux works different way."""

    def pid_by_name(target_string=None, exe_name=None):  # noqa: C901
        """Get proccess pid by its name, pid needed for memory editing."""
        if exe_name is None:
            exe_name = []
        if target_string is None:
            target_string = []
        if platform.system() == "Windows":

            for proc in psutil.process_iter(['pid', 'name', 'create_time']):

                try:

                    hwnds = []

                    def callback(hwnd, hwnds):

                        if win32gui.IsWindowVisible(hwnd):

                            title = win32gui.GetWindowText(hwnd)

                            if any(t in title for t in target_string):
                                hwnds.append(hwnd)

                    win32gui.EnumWindows(callback, hwnds)

                    if hwnds:

                        try:

                            pid = proc.pid
                            #parent_pid = proc.ppid()
                            #parent_name = psutil.Process(parent_pid).name()
                            exe_name = exe_name if exe_name else psutil.Process(proc.pid).exe()  # noqa: E501

                            if proc.name() == exe_name:
                                logging.debug(
                                    f"Found process with window title containing {target_string} and PID {pid} and name: {exe_name}",  # noqa: E501
                                )
                                return pid

                        except psutil.AccessDenied:
                            pass

                        except psutil.NoSuchProcess:
                            pass

                except Exception:  # noqa: S110
                    pass

            else:
                logging.warning(
                    f"No process found with window title containing {target_string}",  # noqa: E501
                )
                return 404

        else:
            logging.warning("Unsupported system detected! skipping...")
            return Status.BAD_OS

    def modify(pid:int, address:str, new_value:int):
        """Memory editing."""
        if platform.system()=="Windows":

            new_value = ctypes.c_int(value=new_value)
            process_handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_ALL_ACCESS,
                False,
                pid,
            )
            buffer = ctypes.create_string_buffer(init=SIZEOF_INT)
            bytes_read = ctypes.c_size_t(0)
            ctypes.windll.kernel32.ReadProcessMemory(
                process_handle,
                address,
                buffer,
                SIZEOF_INT,
                ctypes.byref(bytes_read),
            )
            #value = ctypes.c_int.from_buffer(buffer)
            ctypes.windll.kernel32.WriteProcessMemory(
                process_handle,
                address,
                ctypes.byref(new_value),
                SIZEOF_INT,
                None,
            )
            ctypes.windll.kernel32.CloseHandle(process_handle)
            return 1
        if platform.system() == "Linux":
            try:
                with open(f"/proc/{pid}/mem", "wb") as mem:
                    mem.seek(address)
                    mem.write(new_value.to_bytes(4, 'little'))
                return 1
            except Exception as e:
                logging.error(f"Failed to modify memory: {e}")
                return Status.ERR_UNK
        else:
            logging.warning("Unsupported system detected! skipping...")
            return Status.BAD_OS
    def check(pid:int,address:str):
        """Get current value."""
        if platform.system()=="Windows":

            process_handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_VM_READ,
                False,
                pid,
            )
            buffer = ctypes.create_string_buffer(init=SIZEOF_INT)
            bytes_read = ctypes.c_size_t(0)
            ctypes.windll.kernel32.ReadProcessMemory(
                process_handle,
                address,
                buffer,
                SIZEOF_INT,
                ctypes.byref(bytes_read),
            )
            value = ctypes.c_int.from_buffer(buffer).value
            ctypes.windll.kernel32.CloseHandle(process_handle)
            return value
        if platform.system() == "Linux":
            try:
                with open(f"/proc/{pid}/mem", "rb") as mem:
                    mem.seek(address)
                    value_bytes = mem.read(4)
                return int.from_bytes(value_bytes, 'little', signed=True)
            except Exception as e:
                logging.error(f"Failed to read memory: {e}")
                return Status.ERR_UNK
        else:
            logging.warning("Unsupported system detected! skipping...")
            return Status.BAD_OS

class GithubApi:

    """Functions using Github API."""

    def get_repo_contributors(owner:str, repo:str) -> list:
        """
        Get repository contributors.

        Args:
        ----
            owner (str): Owner of the repo
            repo (str): Repository

        Returns:
        -------
            list: List of contributors

        """
        url = f"https://api.github.com/repos/{owner}/{repo}/contributors"

        response = requests.get(url,timeout=60)
        if response.status_code == 200:  # noqa: PLR2004
            contributors = response.json()
            return [contributor['login'] for contributor in contributors]
        else:
            logging(
                f"Failed to fetch contributors: {response.status_code} - {response.text}",  # noqa: E501
            )
            return []

    def get_last_info_raw(name:str,save_place:str,file_name:str):
        """
        Get last info of user, what he done last.

        Args:
        ----
            name (str): name of user
            save_place (str): place to be saved
            file_name (str): name of the file

        Returns:
        -------
            101: _description_

        """
        url = f"https://api.github.com/users/{name}/events/public"
        page = requests.get(url)  # noqa: S113

        if file_name is None:
            file_name = strftime(
                f"{name}%Y-%m-%d-%H-%M-%S-last-info-raw.json",
                gmtime(),
            )

        if save_place is not None and not save_place.endswith("/"):
            save_place = save_place + "/"

        if save_place is None:
            save_place = ""

        final = str(save_place+file_name)

        with open(final, "w") as f:
            json.dump(
                json.loads(page.text),
                f,
                indent=4,
            )

        return Status.SUCCESS

    def get_info_usr(name:str) -> str:
        """
        Get user info as JSON in variable.

        Args:
        ----
            name (str): User name

        Returns:
        -------
            str: JSON

        """
        url = f"https://api.github.com/users/{name}/events/public"
        page = requests.get(url,timeout=60)
        text = page.text
        text_json = json.loads(text)
        return text_json

class PokeAPI:

    """PokeAPI functions from http API."""

    def get_pokemon_raw(name:str):
        """
        Get json of a pokemon.

        Args:
        ----
            name (str): Name of the pokemon

        Returns:
        -------
            str: json of the pokemon

        """
        url = f"https://pokeapi.co/api/v2/pokemon/{name}"
        page = requests.get(url)  # noqa: S113
        text = page.text
        return text

class OsintFramework:

    """Anything that goes for info of users."""

    class Universal:

        """Universal functions, have more at once."""

        def check_username(self,username:str, service_name:str="All"):
            """
            Check username using instantusername.com API.

            Args:
            ----
                username (str): Username you want to search
                service_name (str, optional): Name of service you want. Defaults to "All".

            Returns:
            -------
                str: json text

            """  # noqa: E501
            base_url = "http://api.instantusername.com"
            services = services_json["services"]

            results = []
            for service in services:
                current_service_name = service["service"]
                endpoint = service["endpoint"]

                if service_name != "All" and current_service_name != service_name:
                    continue

                check_url = f"{base_url}{endpoint}".replace("{username}", username)
                response = requests.get(check_url)  # noqa: S113

                result = {
                    current_service_name: response.status_code == Status.Requests.SUCCESS,  # noqa: E501
                }
                results.append(result)

                if service_name != "All":
                    break
            return results

class OSspecific:

    """Functions Specific for some systems."""

    class Linux:

        """Linux specific functions."""

        def get_linux_distro():
            """
            Get os-release from Linux System.

            Returns
            -------
                str: Linux distro name

            """
            try:
                with open('/etc/os-release') as f:
                    lines = f.readlines()
                    distro_name = ""
                    distro_id = ""

                    for line in lines:
                        if line.startswith('PRETTY_NAME='):
                            distro_name = line.split('=')[1].strip().strip('"')
                        elif line.startswith('ID='):
                            distro_id = line.split('=')[1].strip().strip('"')
                            break  # Stop reading after finding the ID field

                    if distro_id == "arch":
                        return f"{distro_name} (Based on Arch)"
                    elif distro_id == "debian":
                        return f"{distro_name} (Based on Debian)"
                    else:
                        return f"{distro_name} (Custom or Unknown: {distro_id})"
            except FileNotFoundError:
                pass
            return "Unknown"
    class Windows:

        """Windows related things."""

        def get_windows_product_key():
            """
            Return windows product key.

            Returns
            -------
                str: The key

            """
            try:
                import winreg
                key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
                value_name = "DigitalProductId"

                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    product_key_bytes = winreg.QueryValueEx(key, value_name)[0]

                product_key = ""
                for b in product_key_bytes[52:67]:
                    product_key += f"{b:02x}"
                    return product_key
            except Exception:
                return platform.system()

class Networking:

    """Functions related to Network."""

    def get_lan_ip():
        """
        Return local ip.

        Returns
        -------
            int: The ip

        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except OSError:
            return None

    def check_ip_existence(ip:str, result_list:list):
        """
        Check if ip is alive.

        Args:
        ----
            ip (str): Ip to check
            result_list (list): list which it will put ip to

        Returns:
        -------
            list: Adds it to the list

        """
        try:
            if platform.system() == "Linux":
                logging.debug(f"checking {ip}")
                output = subprocess.check_output(
                    ["ping", "-c", "1", ip],  # noqa: S603, S607
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                if "1 packets transmitted," in output and "0 received" not in output:  # noqa: E501
                    result_list.append(ip)
                    logging.info(f"Checked IP: {ip}")
            elif platform.system() == "Windows":
                output = subprocess.check_output(
                    ["ping", "-n", "1", ip],  # noqa: S603, S607
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                if "Received = 1" in output:
                    result_list.append(ip)
                    logging.info(f"Checked IP: {ip}")
            return result_list
        except subprocess.CalledProcessError:
            pass
        except Exception as e:
            logging.error(f"Error checking IP {ip}: {e}")

    def scan_lan_ips(subnet:int, num_threads:int=4,start_ip:int=1,end_ip:int=255) -> list:  # noqa: E501
        """
        Will scan for local ips.

        Args:
        ----
            subnet (int): subnet number
            num_threads (int, optional): Number of threads to use. You can use up to 255 Defaults to 4.
            start_ip (int, optional): _description_. Defaults to 1.
            end_ip (int, optional): _description_. Defaults to 255.

        Raises:
        ------
            ValueError: If number of threads is more than ip's checked

        Returns:
        -------
            list: Appends to list

        """  # noqa: E501
        # Create a list to store results
        if end_ip - start_ip + 1 < num_threads:
            raise ValueError(
                "Must be same or less threads than checked ip adresses",
            )
        result_list = []

        # Calculate the number of IPs each thread should check
        ips_per_thread = (end_ip - start_ip + 1) // num_threads

        # Create and start threads
        threads = []
        for i in range(num_threads):
            start = start_ip + i * ips_per_thread
            end = start + ips_per_thread - 1
            thread = threading.Thread(
                target=Networking.check_ip_range,
                args=(subnet,
                    start,
                    end,
                    result_list,
                ),
            )
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        return result_list

    def check_ip_range(subnet:int, start:int=2, end:int=254):
        """
        Check ip range (DEPRECATED).

        Args:
        ----
            subnet (int): Subnet number
            start (int, optional): First ip number. Defaults to 2.
            end (int, optional): last ip number. Defaults to 254.

        """
        for i in range(start, end + 1):
            ip = subnet + "." + str(i)
            Networking.check_ip_existence(ip)

    def get_gateway_ip():
        """
        Get the default gateway's IP address (cross-platform).

        Returns
        -------
            str: Ip adress

        """
        try:
            gateways = netifaces.gateways()
            if 'default' in gateways and netifaces.AF_INET in gateways['default']:
                return gateways['default'][netifaces.AF_INET][0]
            return None
        except Exception as e:
            logging.error(f"Error getting router gateway IP: {e}")
            return None

class Upload:

    """File uploading functions."""

    def upload_to_transfer_sh(file_path:str):
        """
        Will upload to transfer.sh.

        Args:
        ----
            file_path (str): File to be uploaded

        Returns:
        -------
            str: Response from the web

        """
        with open(file_path, 'rb') as file:
            response = requests.put(
                'https://transfer.sh/'+ file_path,
                data=file,
                timeout=60,
            )
            return response.text.strip()


############   VARIABLES   ############

try:
    SIZEOF_INT = ctypes.sizeof(ctypes.c_int)
    PROCESS_ALL_ACCESS = 0x1F0FFF
    PROCESS_VM_READ = 0x0010
except Exception:
    logging.warning("ctypes not workin/not a windows system, skipping...")

services_json_raw = '''{
  "services": [
    { "service": "Instagram", "endpoint": "/check/instagram/{username}" },
    { "service": "TikTok", "endpoint": "/check/tiktok/{username}" },
    { "service": "Twitter", "endpoint": "/check/twitter/{username}" },
    { "service": "Facebook", "endpoint": "/check/facebook/{username}" },
    { "service": "YouTube", "endpoint": "/check/youtube/{username}" },
    { "service": "Medium", "endpoint": "/check/medium/{username}" },
    { "service": "Reddit", "endpoint": "/check/reddit/{username}" },
    { "service": "HackerNews", "endpoint": "/check/hackernews/{username}" },
    { "service": "GitHub", "endpoint": "/check/github/{username}" },
    { "service": "Quora", "endpoint": "/check/quora/{username}" },
    { "service": "9GAG", "endpoint": "/check/9gag/{username}" },
    { "service": "VK", "endpoint": "/check/vk/{username}" },
    { "service": "GoodReads", "endpoint": "/check/goodreads/{username}" },
    { "service": "Blogger", "endpoint": "/check/blogger/{username}" },
    { "service": "Patreon", "endpoint": "/check/patreon/{username}" },
    { "service": "ProductHunt", "endpoint": "/check/producthunt/{username}" },
    { "service": "500px", "endpoint": "/check/500px/{username}" },
    { "service": "About.me", "endpoint": "/check/about.me/{username}" },
    { "service": "Academia.edu", "endpoint": "/check/academia.edu/{username}" },
    { "service": "AngelList", "endpoint": "/check/angellist/{username}" },
    { "service": "Aptoide", "endpoint": "/check/aptoide/{username}" },
    { "service": "AskFM", "endpoint": "/check/askfm/{username}" },
    { "service": "BLIP.fm", "endpoint": "/check/blip.fm/{username}" },
    { "service": "Badoo", "endpoint": "/check/badoo/{username}" },
    { "service": "Bandcamp", "endpoint": "/check/bandcamp/{username}" },
    { "service": "Basecamp", "endpoint": "/check/basecamp/{username}" },
    { "service": "Behance", "endpoint": "/check/behance/{username}" },
    { "service": "BitBucket", "endpoint": "/check/bitbucket/{username}" },
    { "service": "BitCoinForum", "endpoint": "/check/bitcoinforum/{username}" },
    { "service": "BuzzFeed", "endpoint": "/check/buzzfeed/{username}" },
    { "service": "Canva", "endpoint": "/check/canva/{username}" },
    { "service": "Carbonmade", "endpoint": "/check/carbonmade/{username}" },
    { "service": "CashMe", "endpoint": "/check/cashme/{username}" },
    { "service": "Cloob", "endpoint": "/check/cloob/{username}" },
    { "service": "Codecademy", "endpoint": "/check/codecademy/{username}" },
    { "service": "Codementor", "endpoint": "/check/codementor/{username}" },
    { "service": "Codepen", "endpoint": "/check/codepen/{username}" },
    { "service": "Coderwall", "endpoint": "/check/coderwall/{username}" },
    { "service": "ColourLovers", "endpoint": "/check/colourlovers/{username}" },
    { "service": "Contently", "endpoint": "/check/contently/{username}" },
    { "service": "Coroflot", "endpoint": "/check/coroflot/{username}" },
    { "service": "CreativeMarket", "endpoint": "/check/creativemarket/{username}" },
    { "service": "Crevado", "endpoint": "/check/crevado/{username}" },
    { "service": "Crunchyroll", "endpoint": "/check/crunchyroll/{username}" },
    { "service": "DEV Community", "endpoint": "/check/devcommunity/{username}" },
    { "service": "DailyMotion", "endpoint": "/check/dailymotion/{username}" },
    { "service": "Designspiration", "endpoint":"/check/designspiration/{username}"},
    { "service": "DeviantART", "endpoint": "/check/deviantart/{username}" },
    { "service": "Disqus", "endpoint": "/check/disqus/{username}" },
    { "service": "Dribbble", "endpoint": "/check/dribbble/{username}" },
    { "service": "Ebay", "endpoint": "/check/ebay/{username}" },
    { "service": "Ello", "endpoint": "/check/ello/{username}" },
    { "service": "Etsy", "endpoint": "/check/etsy/{username}" },
    { "service": "EyeEm", "endpoint": "/check/eyeem/{username}" },
    { "service": "Flickr", "endpoint": "/check/flickr/{username}" },
    { "service": "Flipboard", "endpoint": "/check/flipboard/{username}" },
    { "service": "Foursquare", "endpoint": "/check/foursquare/{username}" },
    { "service": "Giphy", "endpoint": "/check/giphy/{username}" },
    { "service": "GitLab", "endpoint": "/check/gitlab/{username}" },
    { "service": "Gitee", "endpoint": "/check/gitee/{username}" },
    { "service": "Gravatar", "endpoint": "/check/gravatar/{username}" },
    { "service": "Gumroad", "endpoint": "/check/gumroad/{username}" },
    { "service": "HackerOne", "endpoint": "/check/hackerone/{username}" },
    { "service": "House-Mixes.com", "endpoint":"/check/house-mixes.com/{username}"},
    { "service": "Houzz", "endpoint": "/check/houzz/{username}" },
    { "service": "HubPages", "endpoint": "/check/hubpages/{username}" },
    { "service": "Homescreen.me", "endpoint": "/check/homescreen.me/{username}" },
    { "service": "IFTTT", "endpoint": "/check/ifttt/{username}" },
    { "service": "ImageShack", "endpoint": "/check/imageshack/{username}" },
    { "service": "Imgur", "endpoint": "/check/imgur/{username}" },
    { "service": "Instructables", "endpoint": "/check/instructables/{username}" },
    { "service": "Investing.com", "endpoint": "/check/investing.com/{username}" },
    { "service": "Issuu", "endpoint": "/check/issuu/{username}" },
    { "service": "Itch.io", "endpoint": "/check/itch.io/{username}" },
    { "service": "Jimdo", "endpoint": "/check/jimdo/{username}" },
    { "service": "Kaggle", "endpoint": "/check/kaggle/{username}" },
    { "service": "KanoWorld", "endpoint": "/check/kanoworld/{username}" },
    { "service": "Keybase", "endpoint": "/check/keybase/{username}" },
    { "service": "Kik", "endpoint": "/check/kik/{username}" },
    { "service": "Kongregate", "endpoint": "/check/kongregate/{username}" },
    { "service": "Launchpad", "endpoint": "/check/launchpad/{username}" },
    { "service": "Letterboxd", "endpoint": "/check/letterboxd/{username}" },
    { "service": "LiveJournal", "endpoint": "/check/livejournal/{username}" },
    { "service": "Mastodon", "endpoint": "/check/mastodon/{username}" },
    { "service": "MeetMe", "endpoint": "/check/meetme/{username}" },
    { "service": "MixCloud", "endpoint": "/check/mixcloud/{username}" },
    { "service": "MyAnimeList", "endpoint": "/check/myanimelist/{username}" },
    { "service": "NameMC", "endpoint": "/check/namemc/{username}" },
    { "service": "Newgrounds", "endpoint": "/check/newgrounds/{username}" },
    { "service": "Pastebin", "endpoint": "/check/pastebin/{username}" },
    { "service": "Pexels", "endpoint": "/check/pexels/{username}" },
    { "service": "Photobucket", "endpoint": "/check/photobucket/{username}" },
    { "service": "Pinterest", "endpoint": "/check/pinterest/{username}" },
    { "service": "Pixabay", "endpoint": "/check/pixabay/{username}" },
    { "service": "Plug.DJ", "endpoint": "/check/plug.dj/{username}" },
    { "service": "Rajce.net", "endpoint": "/check/rajce.net/{username}" },
    { "service": "Repl.it", "endpoint": "/check/repl.it/{username}" },
    { "service": "ReverbNation", "endpoint": "/check/reverbnation/{username}" },
    { "service": "Roblox", "endpoint": "/check/roblox/{username}" },
    { "service": "Scribd", "endpoint": "/check/scribd/{username}" },
    { "service": "Signal", "endpoint": "/check/signal/{username}" },
    { "service": "Slack", "endpoint": "/check/slack/{username}" },
    { "service": "SlideShare", "endpoint": "/check/slideshare/{username}" },
    { "service": "SoundCloud", "endpoint": "/check/soundcloud/{username}" },
    { "service": "SourceForge", "endpoint": "/check/sourceforge/{username}" },
    { "service": "Spotify", "endpoint": "/check/spotify/{username}" },
    { "service": "Star Citizen", "endpoint": "/check/starcitizen/{username}" },
    { "service": "Steam", "endpoint": "/check/steam/{username}" },
    { "service": "SteamGroup", "endpoint": "/check/steamgroup/{username}" },
    { "service": "Taringa", "endpoint": "/check/taringa/{username}" },
    { "service": "Telegram", "endpoint": "/check/telegram/{username}" },
    { "service": "Tinder", "endpoint": "/check/tinder/{username}" },
    { "service": "TradingView", "endpoint": "/check/tradingview/{username}" },
    { "service": "Trakt", "endpoint": "/check/trakt/{username}" },
    { "service": "Trip", "endpoint": "/check/trip/{username}" },
    { "service": "TripAdvisor", "endpoint": "/check/tripadvisor/{username}" },
    { "service": "Twitch", "endpoint": "/check/twitch/{username}" },
    { "service": "Unsplash", "endpoint": "/check/unsplash/{username}" },
    { "service": "VSCO", "endpoint": "/check/vsco/{username}" },
    { "service": "Venmo", "endpoint": "/check/venmo/{username}" },
    { "service": "Vimeo", "endpoint": "/check/vimeo/{username}" },
    { "service": "VirusTotal", "endpoint": "/check/virustotal/{username}" },
    { "service": "We Heart It", "endpoint": "/check/weheartit/{username}" },
    { "service": "WebNode", "endpoint": "/check/webnode/{username}" },
    { "service": "Fandom", "endpoint": "/check/fandom/{username}" },
    { "service": "Wikipedia", "endpoint": "/check/wikipedia/{username}" },
    { "service": "Wix", "endpoint": "/check/wix/{username}" },
    { "service": "WordPress", "endpoint": "/check/wordpress/{username}" },
    { "service": "YouPic", "endpoint": "/check/youpic/{username}" },
    { "service": "Zhihu", "endpoint": "/check/zhihu/{username}" },
    { "service": "devRant", "endpoint": "/check/devrant/{username}" },
    { "service": "iMGSRC.RU", "endpoint": "/check/imgsrc.ru/{username}" },
    { "service": "last.fm", "endpoint": "/check/last.fm/{username}" },
    { "service": "Makerlog", "endpoint": "/check/makerlog/{username}" }
  ]
}'''
services_json = json.loads(services_json_raw)

if __name__ == "__main__":
    update_script_from_github(
        owner = "xxcosita3czxx",
        repo = "Cosita-ToolKit",
        branch=update_branch,
        file_path = "cosita_toolkit.py",
        local_file_path = "./cosita_toolkit.py",
    )
