# Copyright (C) 2023 David Shiko
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# os_environ raises if missed and os_getenv returns None
from os import getenv as os_getenv, environ as os_environ
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

MAIN_ADMIN = 177381168
# @david_shiko, @david_neshiko, @Alex_vochis, @dubrovin_vladimir
ADMINS = [MAIN_ADMIN, 5064404775, 157218637, 790503987]
MAIN_ADMIN_NAME = '@david_shiko'

LANGUAGE = os_getenv('LANGUAGE_', "en")  # Don't use "LANGUAGE" name cuz it's already used by unix system

YANDEX_API_KEY = os_getenv('YANDEX_API_KEY')
GRASPIL_ANALYTICS_API_KEY = os_getenv('GRASPIL_ANALYTICS_API_KEY', "")
DONATE_URL = os_getenv('DONATE_URL')
DEBUG = os_getenv('DEBUG', 'false').lower() == 'true'  # True only if 'True' passed

# TG
API_ID = os_environ['API_ID']
API_HASH = os_environ['API_HASH']
BOT_NAME = os_environ['BOT_NAME']
BOT_ID = os_environ['BOT_ID']
TG_BOT_TOKEN = os_environ['TG_BOT_TOKEN']
TG_POSTS_CHANNEL = int(os_environ["TG_POSTS_CHANNEL"])
TG_POSTS_STORE = int(os_environ["TG_POSTS_STORE"])
TG_POSTS_STORE_MANAGER = int(os_environ["TG_POSTS_STORE_MANAGER"])
TG_POSTS_CHANNEL_LINK = os_environ["TG_POSTS_CHANNEL_LINK"]

CREATE_PERSONAL_DEFAULT_COLLECTIONS = os_getenv('CREATE_PERSONAL_DEFAULT_COLLECTIONS', 'false', ).lower() == 'true'
CREATE_PUBLIC_DEFAULT_COLLECTIONS = os_getenv('CREATE_PUBLIC_DEFAULT_COLLECTIONS', 'false', ).lower() == 'true'
PERSISTENT = not DEBUG

# PATHS
PROJECT_ROOT_PATH = Path(f'{Path(__file__).parent.parent}')
LOCALES_PATH = Path(__file__).parent / 'locales'
# Create parent dirs if not exists. parents - not create if not exists, exist_ok - not raise if exists
Path(f'{PROJECT_ROOT_PATH}/logs/').mkdir(parents=True, exist_ok=True)

LOG_ERROR_FILENAME = 'error.log'
LOGS_PATH = Path(f'{PROJECT_ROOT_PATH}/logs')
LOG_OTHER_FILEPATH = Path(f'{LOGS_PATH}/other_stuff.log')
LOG_ERROR_FILEPATH = Path(f'{LOGS_PATH}/{LOG_ERROR_FILENAME}')
LOG_KNOWN_EXCEPTIONS_FILEPATH = Path(f'{LOGS_PATH}/known_exceptions.log')

# This folder will contain pickled bot data (CH?) if bot unexpectedly stopped
PICKLE_PATH = Path(f'{PROJECT_ROOT_PATH}/pickle_persistence.pkl')
DEFAULT_PHOTO_PATH = PROJECT_ROOT_PATH / 'app/assets/photos/default_photo.png'
DONATE_IMAGE_PATH = PROJECT_ROOT_PATH / 'app/assets/photos/donate_qr.png'
# https://docs.telethon.dev/en/stable/modules/client.html#telethon.client.telegramclient.TelegramClient
TELETHON_AUTH_CACHE_PATH = PROJECT_ROOT_PATH / 'app/tg/telethon_auth_cache'
