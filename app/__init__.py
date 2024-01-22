from flask import Flask
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import os

from src.thread_manager import ThreadManager

load_dotenv(find_dotenv())

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.config['APPLICATION_ROOT'] = os.getenv('APP_ROOT', '/translapse')

def env_load_dir(env_key, default, config_key = None):
    directory = os.getenv(env_key, default)
    if not config_key is None:
        app.config[config_key] = directory
    if not os.path.isdir(directory):
        os.makedirs(directory)

def empty_dir_reqursive(dirpath):
    dirpath = Path(dirpath)
    for item in dirpath.iterdir():
        if item.is_dir():
            empty_dir_reqursive(item)
            item.rmdir()
        else:
            item.unlink()
# loading directory paths from .env file
env_load_dir('UPLOAD_DIR', 'data/archieves', 'UPLOAD_DIR')
env_load_dir('TMP_DIR', 'data/tmp', 'TMP_DIR')
env_load_dir('VID_DIR', 'data/renders', 'VID_DIR')
# cleaning temp directories
empty_dir_reqursive(app.config['UPLOAD_DIR'])
empty_dir_reqursive(app.config['TMP_DIR'])

thread_manager = ThreadManager(
    threads = 1,
    max_queue_size = 100,
    thread_wait_timeout = 5
)