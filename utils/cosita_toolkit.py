#########################################
#                                       #
#                CosTK                  #
#           - by cosita3cz              #
#                                       #
#########################################

###  Config  ###############################################
loglevel="INFO"
# (Available: "DEBUG", "INFO", "WARNING", "ERROR", "FATAL")
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

############   MODULE IMPORTS   ############

try:
    import logging
except:
    print ("FATAL: cannot import logging")

try:
    import coloredlogs
    coloredlogs.install(level=loglevel, fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
except:
    logging.warning("will not be using colors, as the module cannot be found")

try:
    import platform
except:
    logging.fatal("Failed to import base module platform")

try:
    if platform.system() == "Windows":
        import win32gui
        import ctypes
    else:
        logging.debug("not importing windows depends")
except:
    logging.warning("Windows Dependendencies not found, could have limitations")

try:
    import subprocess
except:
    logging.warning("Module subproccess not found, could have limitations")

try:
    import hashlib
except:
    logging.warning("Module hashlib not found, could have limitations")

try:
    import netifaces
except:
    logging.warning("Module netifaces not found, could have limitations")

try:
    import psutil
except:
    logging.warning("Module psutil not found, could have limitations")

try:
    import socket
except:
    logging.warning("Module socket not found, could have limitations")

try:
    import threading
except:
    logging.warning("Module threading not found, could have limitations")

try:
    import requests
except:
    logging.warning("Module requests not found, could have limitations")

try:
    import json
except:
    logging.warning("Module json not found, could have limitations")

try:
    from time import gmtime, strftime
except:
    logging.warning("Module time not found, could have limitations")

try:
    import os
except:
    logging.warning("Module os not found, could have limitations")

try:
    import base64
except:
    logging.warning("Module base64 not found, could have limitations")


def update_script_from_github(owner, repo, file_path, local_file_path):
    '''
    Updating from github, so you dont have to download always from git
    '''
    try:
        from git import Repo
        # Specify the details for the file update
        if __name__ == "__main__":
            orig_dir = os.getcwd()
            os.chdir(os.path.dirname(os.path.abspath(__file__)))

        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Cosita-Toolkit-Updater"
        }
        response = requests.get(api_url, headers=headers)
        print (response.status_code)
        if response.status_code == 200:
            github_content = response.json()["content"]
            github_content = base64.b64decode(github_content).decode("utf-8")

            try:
                with open(local_file_path, "r") as file:
                    local_content = file.read()

                if github_content != local_content:
                    with open(local_file_path, "w") as file:
                        file.write(github_content)
                    print("Script updated successfully.")
                    if __name__=="__main__":
                        os.chdir(orig_dir)
                    return 1
                else:
                    logging.info("No update required. Local script is up to date.")
                    if __name__=="__main__":
                        os.chdir(orig_dir)
                    return 2
            except FileNotFoundError:
                with open(local_file_path, "w") as file:
                    file.write(github_content)
                logging.info("Script downloaded and saved successfully.")
                if __name__=="__main__":
                    os.chdir(orig_dir)
                return 7
        else:
            print("Failed to fetch the script from GitHub.")
            if __name__=="__main__":
                os.chdir(orig_dir)
            return response.status_code
    except Exception as e:
        logging.error("updater error ->> "+str(e))
        os.chdir(orig_dir)
        return 400
if __name__ == "__main__":
    update_script_from_github(owner = "xxcosita3czxx", repo = "Cosita-ToolKit", file_path = "cosita_toolkit.py", local_file_path = "./cosita_toolkit.py")


def main():
    logging.warning("yet not supported")


############   FUNCTIONS   ############

class memMod:
    '''
    Requires windows, bcs linux works different way
    '''
    def pid_by_name(target_string=[], exe_name=[]):
        '''
        Get proccess pid by its name, pid needed for memory editing
        '''
        if platform.system() == "Windows":
            for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                try:
                    hwnds = []
                    # Enumerate all windows and add the handle to the list if the target string is in the title
                    def callback(hwnd, hwnds):
                        if win32gui.IsWindowVisible(hwnd):
                            title = win32gui.GetWindowText(hwnd)
                            if any(t in title for t in target_string):
                                hwnds.append(hwnd)
                    win32gui.EnumWindows(callback, hwnds)
                    # If we found a matching window, check the parent process
                    if hwnds:
                        try:
                            pid = proc.pid
                            parent_pid = proc.ppid()
                            parent_name = psutil.Process(parent_pid).name()
                            exe_name = psutil.Process(proc.pid).exe() if not exe_name else exe_name
                            if proc.name() == exe_name:
                                logging.debug(f"Found process with window title containing {target_string} and PID {pid} and name: {exe_name}")
                                return pid
                        except psutil.AccessDenied:
                            # Access denied - ignore this process
                            pass
                        except psutil.NoSuchProcess:
                            # Process may have terminated while iterating
                            pass
                except:
                    pass
            else:
                logging.warning(f"No process found with window title containing {target_string}")
                return None
        else:
            logging.warning("Non-Windows system detected! skipping...")
            return "Non-Windows system detected! skipping..."
    def modify(pid, address, new_value):
        '''
        Here is the actuall edit of memory
        '''
        if platform.system()=="Windows":
            new_value = ctypes.c_int(new_value)
            process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
            buffer = ctypes.create_string_buffer(SIZEOF_INT)
            bytes_read = ctypes.c_size_t(0)
            ctypes.windll.kernel32.ReadProcessMemory(process_handle, address, buffer, SIZEOF_INT, ctypes.byref(bytes_read))
            value = ctypes.c_int.from_buffer(buffer)
            ctypes.windll.kernel32.WriteProcessMemory(process_handle, address, ctypes.byref(new_value), SIZEOF_INT, None)
            ctypes.windll.kernel32.CloseHandle(process_handle)
            return 1
        else:
            logging.warning("Non-Windows system detected! skipping...")
            return "Non-windows system detected! skipping..."
    def check(pid, address):
        '''
        get current value
        '''
        if platform.system()=="Windows":
            process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_VM_READ, False, pid)
            buffer = ctypes.create_string_buffer(SIZEOF_INT)
            bytes_read = ctypes.c_size_t(0)
            ctypes.windll.kernel32.ReadProcessMemory(process_handle, address, buffer, SIZEOF_INT, ctypes.byref(bytes_read))
            value = ctypes.c_int.from_buffer(buffer).value
            ctypes.windll.kernel32.CloseHandle(process_handle)
            return value
        else:
            logging.warning("Non-Windows system detected! skipping...")
            return "Non-windows system detected! skipping..."
# github api things
class github_api:
    def get_last_info_raw(name,save_place=None,file_name=None):
        url = f"https://api.github.com/users/{name}/events/public"
        page = requests.get(url)
        if file_name is None:
            file_name = strftime(f"{name}%Y-%m-%d-%H-%M-%S-last-info-raw.json", gmtime())
        if save_place is not None and not save_place.endswith("/"):
            save_place = save_place + "/"
        if save_place is None:
            save_place = ""
        final = str(save_place+file_name)
        with open(final, "w") as f:
            json.dump(json.loads(page.text), f, indent=4)
        return 1
    def get_info_usr(name):
        url = f"https://api.github.com/users/{name}/events/public"
        page = requests.get(url)
        text = page.text
        text_json = json.loads(text)
        return text_json
    def pull_repo(repo_dir):
        if os.path.exists(repo_dir):
            repo = Repo(repo_dir)
            origin = repo.remote()
            pull_result = origin.pull()
            return 2  # Successful pull with merge
        else:
            return 404  # Repository does not exist
    def update_repo_files_http(owner, repo, branch, file_path):
        def compute_file_hash(file_content):
            # Compute the hash of the file content
            file_hash = hashlib.sha256(file_content.encode()).hexdigest()
            return file_hash
        def get_file_content(owner, repo, file_path):
            file_content=None
            # GitHub API endpoint to fetch the contents of a
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
            # Make a GET request to the GitHub API
            response = requests.get(url)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Extract the file content from the response
                try:
                    file_content = base64.b64decode(response.json()['content']).decode()
                    return file_content
                except KeyError:
                    logging.error("Failed to extract content from API response:", response.json())
                    return "KeyError"
            elif response.status_code == 404:
                logging.debug(f"Ignoring {file_content}")
            else:
                logging.error(f"Failed to fetch file '{file_path}' from the repository '{repo}'. Response code: {response.status_code}")
                return response.status_code
        file_content=None
        url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"
        
        # Make a GET request to the GitHub API
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Extract the latest commit hash
            latest_commit_hash = response.json().get('sha')
            if file_content:
                # Get the hash of the file content from GitHub
                file_content = get_file_content(owner, repo, file_path)
                if file_content is not None:
                    file_hash = compute_file_hash(file_content)
                    if file_hash != latest_commit_hash:
                        logging.info(f"Updates available for '{file_path}'. Downloading...")
                        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
                        response = requests.get(url)
        
                        # Check if the request was successful (status code 200)
                        if response.status_code == 200:
                            # Open the local file in binary write mode and write the content from the response
                            with open(file_path, 'wb') as f:
                                f.write(response.content)
                        else:
                            logging.error(f"Failed to download file from '{url}'. Response code: {response.status_code}")
                            return "Failed"
                        print(f"Updates for '{file_path}' downloaded successfully.")
                        return 2
                    else:
                        logging.info(f"No updates available for '{file_path}'.")
                        return 0
                else:
                    logging.warning("Unable to compute file hash. Check if the file exists.")
                    return 404
            else:
                # If no file path is specified, iterate through every file in the current directory
                try:
                    for file_name in os.listdir('.'):
                        if os.path.isfile(file_name):
                            logging.debug(f"Checking for updates to '{file_name}'...")
                            file_content = get_file_content(owner, repo, file_name)
                            if file_content is not None:
                                file_hash = compute_file_hash(file_content)
                                if file_hash != latest_commit_hash:
                                    logging.info(f"Updates available for '{file_name}'. Downloading...")
                                    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_name}"
                                    # Specify the local filename to save the downloaded file
                                    # Send a GET request to the URL
                                    response = requests.get(url)
                    
                                    # Check if the request was successful (status code 200)
                                    if response.status_code == 200:
                                        # Open the local file in binary write mode and write the content from the response
                                        with open(file_name, 'wb') as f:
                                            f.write(response.content)
                                    else:
                                        logging.error(f"Failed to download file from '{url}'. Response code: {response.status_code}")
                                        return "Failed"
                                    logging.info(f"Updates for '{file_name}' downloaded successfully.")
                                else:
                                    logging.info(f"No updates available for '{file_name}'.")
                            else:
                                logging.warning("Unable to compute file hash. Check if the file exists.")
                except:
                     logging.info("update successful")
                     return 2
        else:
            logging.error(f"Failed to fetch commit information from GitHub. Response code: {response.status_code}")
            logging.error("Response content:", response.text)
            return 404
# pokeAPI things
class PokeAPI:
    def get_pokemon_raw(name):
        url = f"https://pokeapi.co/api/v2/pokemon/{name}"
        page = requests.get(url)
        text = page.text
        return text
# tools only osinters use
class osint_framework:
    class universal:
        def check_username(username, service_name="All"):
            base_url = "http://api.instantusername.com"
            services = services_json["services"]

            results = []
            for service in services:
                current_service_name = service["service"]
                endpoint = service["endpoint"]

                if service_name != "All" and current_service_name != service_name:
                    continue

                check_url = f"{base_url}{endpoint}".replace("{username}", username)
                response = requests.get(check_url)

                result = {current_service_name: response.status_code == 200}
                results.append(result)

                if service_name != "All":
                    break
            return results

# OS Specific things
class OSspecific:
    class Linux:
        def get_linux_distro():
            try:
                with open('/etc/os-release', 'r') as f:
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
        def get_windows_product_key():
            try:
                import winreg
                key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
                value_name = "DigitalProductId"

                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    product_key_bytes = winreg.QueryValueEx(key, value_name)[0]
                
                product_key = ""
                for b in product_key_bytes[52:67]:
                    product_key += "%02x" % b
                    return product_key
            except:
                return platform.system()
# Networking tools
class Networking:
    def get_lan_ip():
        try:
            # Create a socket to the Google DNS server (8.8.8.8)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except socket.error:
            return None

    def check_ip_existence(ip, result_list):
        try:
            # Use the 'ping' command on Linux or Windows to check if the IP exists
            if platform.system() == "Linux":
                logging.debug(f"checking {ip}")
                output = subprocess.check_output(["ping", "-c", "1", ip], stderr=subprocess.STDOUT, text=True)
                if "1 packets transmitted," in output and "0 received" not in output:
                    result_list.append(ip)
                    logging.info(f"Checked IP: {ip}")
            elif platform.system() == "Windows":
                output = subprocess.check_output(["ping", "-n", "1", ip], stderr=subprocess.STDOUT, text=True)
                if "Received = 1" in output:
                    result_list.append(ip)
                    logging.info(f"Checked IP: {ip}")
        except subprocess.CalledProcessError as e:
            pass
        except Exception as e:
            logging.error(f"Error checking IP {ip}: {e}")

    def scan_lan_ips(subnet, num_threads=4,start_ip = 1,end_ip = 255):
        # Create a list to store results
        if end_ip - start_ip + 1 < num_threads:
            raise ValueError("Must be same or less threads than checked ip adresses")
        result_list = []

        # Calculate the number of IPs each thread should check
        ips_per_thread = (end_ip - start_ip + 1) // num_threads

        # Create and start threads
        threads = []
        for i in range(num_threads):
            start = start_ip + i * ips_per_thread
            end = start + ips_per_thread - 1
            thread = threading.Thread(target=Networking.check_ip_range, args=(subnet, start, end, result_list))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        return result_list

    def check_ip_range(subnet, start, end, result_list):
        for i in range(start, end + 1):
            ip = subnet + "." + str(i)
            Networking.check_ip_existence(ip, result_list)

    def get_gateway_ip():
        try:
            # Get the default gateway's IP address (cross-platform)
            gateways = netifaces.gateways()
            if 'default' in gateways and netifaces.AF_INET in gateways['default']:
                return gateways['default'][netifaces.AF_INET][0]
            return None
        except Exception as e:
            logging.error(f"Error getting router gateway IP: {e}")
            return None
# Other
class Other:
    def upload_to_transfer_sh(file_path):
        with open(file_path, 'rb') as file:
            response = requests.put('https://transfer.sh/' + file_path, data=file)
            return response.text.strip()
            

############   VARIABLES   ############

try:
    SIZEOF_INT = ctypes.sizeof(ctypes.c_int)
    PROCESS_ALL_ACCESS = 0x1F0FFF
    PROCESS_VM_READ = 0x0010
except:
    logging.warning("ctypes not workin/not a windows system, skipping...")


# services.json
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
    { "service": "Designspiration", "endpoint": "/check/designspiration/{username}" },
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
    { "service": "House-Mixes.com", "endpoint": "/check/house-mixes.com/{username}" },
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