import json
import logging
import os
import shutil
import subprocess
import zipfile
from typing import Optional, Tuple

import requests
from colorlog import ColoredFormatter

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIG_FILE = os.path.join(BASE_DIR, "updater_config.json")

def load_config() -> dict:
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def get_remote_version_and_zip_url(user: str, repo: str) -> Tuple[Optional[str], Optional[str]]:
    releases_url = f"https://api.github.com/repos/{user}/{repo}/releases/latest"
    response = requests.get(releases_url)
    if response.status_code == 200:
        try:
            latest_release = response.json()
            version = latest_release['tag_name']
            zip_url = f"https://github.com/{user}/{repo}/archive/refs/tags/{version}.zip"
            
            return version, zip_url
        
        except (ValueError, KeyError, AttributeError) as e:
            logging.error(f"Error parsing JSON response: {e}")
            return None, None
    
    logging.error(f"Failed to fetch the latest release information. Status code: {response.status_code}")
    return None, None

def download_and_extract_zip(url: str, extract_to: str) -> str:
    local_filename = url.split('/')[-1] + ".zip"
    logging.info(f"Downloading {url}")
    
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    logging.info(f"Extracting {local_filename}")
    
    with zipfile.ZipFile(local_filename, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
    os.remove(local_filename)
    extracted_dir = os.path.join(extract_to, zip_ref.namelist()[0].split('/')[0])
    
    return extracted_dir

def is_user_dir(dirpath: str, user_dir_prefix: str) -> bool:
    return any(part.startswith(user_dir_prefix) for part in dirpath.split(os.sep))

def clean_old_version(app_dir: str, exclude_dirs: list, merge_dirs: list, user_dir_prefix: str, script_name: str) -> None:
    for item in os.listdir(app_dir):
        item_path = os.path.join(app_dir, item)
        if item not in exclude_dirs and item != script_name:
            if os.path.isdir(item_path):
                if item in merge_dirs:
                    for subitem in os.listdir(item_path):
                        subitem_path = os.path.join(item_path, subitem)
                        if os.path.isdir(subitem_path) and not is_user_dir(subitem_path, user_dir_prefix):
                            shutil.rmtree(subitem_path)
                            logging.info(f"Removed directory: {subitem_path}")
            
                else:
                    shutil.rmtree(item_path)
                    logging.info(f"Removed directory: {item_path}")
            
            else:
                os.remove(item_path)
                logging.info(f"Removed file: {item_path}")

def merge_directories(src_dir: str, dest_dir: str) -> None:
    for item in os.listdir(src_dir):
        src_item = os.path.join(src_dir, item)
        dest_item = os.path.join(dest_dir, item)
        if os.path.isdir(src_item):
            if not os.path.exists(dest_item):
                shutil.copytree(src_item, dest_item)
                logging.info(f"Copied directory: {src_item} to {dest_item}")
        
            else:
                merge_directories(src_item, dest_dir)
        
        else:
            shutil.copy2(src_item, dest_item)
            logging.info(f"Copied file: {src_item} to {dest_item}")

def version_tuple(version: str) -> Tuple[int, ...]:
    return tuple(map(int, (version.split("."))))

def needs_update() -> Tuple[bool, Optional[str], Optional[str]]:
    config = load_config()
    current_version = config["VERSION"]
    user = config["USER"]
    repo = config["REPO"]
    
    remote_version, _ = get_remote_version_and_zip_url(user, repo)
    if remote_version and version_tuple(current_version) < version_tuple(remote_version):
        return True, current_version, remote_version
    
    return False, current_version, remote_version

def update_application(zip_url: str, temp_dir: str, app_dir: str, exclude_dirs: list, merge_dirs: list, user_dir_prefix: str, script_name: str) -> None:
    logging.info("Starting application update...")
    extracted_dir = download_and_extract_zip(zip_url, extract_to=temp_dir)
    
    logging.info("Removing old version...")
    clean_old_version(app_dir, exclude_dirs, merge_dirs, user_dir_prefix, script_name)
    
    logging.info("Installing new version...")
    merge_directories(extracted_dir, app_dir)
    
    shutil.rmtree(temp_dir)
    logging.info("Update complete.")

def run_main_script(main_script: str) -> None:
    logging.info(f"Running main script: {main_script}")
    subprocess.run(["python", main_script])

def run_update(main_script: str) -> None:
    config = load_config()

    user = config["USER"]
    repo = config["REPO"]
    exclude_dirs = config["EXCLUDE_DIRS"]
    merge_dirs = config["MERGE_DIRS"]
    user_dir_prefix = config["USER_DIR_PREFIX"]
    current_version = config["VERSION"]

    current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    app_dir = current_dir
    temp_dir = os.path.join(current_dir, "temp")
    script_name = os.path.basename(__file__)

    remote_version, zip_url = get_remote_version_and_zip_url(user, repo)

    logging.info(f"Updating from version {current_version} to {remote_version}")
    update_application(zip_url, temp_dir, app_dir, exclude_dirs, merge_dirs, user_dir_prefix, script_name)

    run_main_script(main_script)

if __name__ == "__main__":
    logger = logging.getLogger()
    console_handler = logging.StreamHandler()
    formatter = ColoredFormatter(
        "[%(asctime)s] [%(log_color)s%(levelname)s%(reset)s] - %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'purple',
        },
        secondary_log_colors={},
        style='%'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    logging.basicConfig(level=logging.INFO)
    MAIN_SCRIPT = os.path.join(BASE_DIR, "Code", "main.py")
    run_update(MAIN_SCRIPT)
