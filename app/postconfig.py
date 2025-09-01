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
from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Callable
import gettext
import logging
import polib  # https://github.com/izimobil/polib/
from types import SimpleNamespace

from geopy.geocoders import Yandex  # For location
from httpx import AsyncClient as httpx_AsyncClient

from app import config

if TYPE_CHECKING:
    from os import PathLike

if config.DEBUG:
    # Not sure that this does anything
    logging.raiseExceptions = True  # https://docs.python.org/3/library/logging.html#logging.raiseExceptions


locator = Yandex(api_key=config.YANDEX_API_KEY, timeout=3)  # for location


def setup_logger(
        logger: logging.Logger,
        filename: str | PathLike,
        level: int | str = logging.INFO,
) -> logging.Logger:
    handler = logging.FileHandler(filename=filename, encoding='utf-8', )
    handler.setFormatter(logging.Formatter(fmt='[%(asctime)s] %(pathname)s:%(lineno)d %(levelname)s - %(message)s', ))
    handler.setLevel(level, )
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


class CustomFilter(logging.Filter, ):
    """App only filter (no site packages)"""
    def filter(self, record) -> bool:
        try:
            if getattr(record, 'exc_info', False):
                last_tb = current_tb = record.exc_info[-1]
                while 'site-packages' not in str(current_tb.tb_frame):
                    last_tb = current_tb
                    current_tb = current_tb.tb_next
                else:  # When loop eventually ended with 'site-packages'
                    last_tb.tb_next = None
        finally:
            return True


app_logger = setup_logger(logger=logging.getLogger(), filename=config.LOG_ERROR_FILEPATH, )

# KNOWN EXCEPTIONS LOGGER CONFIG
known_exceptions_logger = logging.getLogger('known_exceptions')
known_exceptions_log_handler = logging.FileHandler(filename=config.LOG_KNOWN_EXCEPTIONS_FILEPATH, encoding='utf-8', )
known_exceptions_logger.addFilter(CustomFilter())
known_exceptions_log_handler.setFormatter(logging.Formatter('[%(asctime)s] - %(message)s'))
known_exceptions_logger.addHandler(known_exceptions_log_handler)
known_exceptions_logger.setLevel(logging.INFO, )  # Really need?
known_exceptions_logger.propagate = True  # Really need?

telethon_logger = logging.getLogger('telethon')
graspil_logger = logging.getLogger('graspil')
httpx_logger = logging.getLogger('httpx')

shared_log_handler = logging.FileHandler(filename=config.LOG_OTHER_FILEPATH, encoding='utf-8', )
shared_log_handler.setFormatter(logging.Formatter('[%(asctime)s] %(module)s %(levelname)s - %(message)s'))

telethon_logger.addHandler(shared_log_handler)
graspil_logger.addHandler(shared_log_handler)
httpx_logger.addHandler(shared_log_handler)

telethon_logger.propagate = False
graspil_logger.propagate = False
httpx_logger.propagate = False

telethon_logger.setLevel(logging.INFO, )
graspil_logger.setLevel(logging.INFO, )
httpx_logger.setLevel(logging.WARNING, )


def create_translations(
        filename: Literal['shared', 'user', 'search', 'collections', 'posts', 'votes', 'mix', 'cmd_descriptions'],
) -> Callable:
    """Create translations for all strings but return translation only for one lang"""
    po = polib.pofile(pofile=f'{config.LOCALES_PATH}/{config.LANGUAGE}/LC_MESSAGES/{filename}.po', )
    po.save_as_mofile(fpath=f'{config.LOCALES_PATH}/{config.LANGUAGE}/LC_MESSAGES/{filename}.mo', )
    lang = gettext.translation(domain=filename, localedir=config.LOCALES_PATH, languages=[config.LANGUAGE, ])
    return lang.gettext


translators = SimpleNamespace(
    shared=create_translations(filename='shared', ),
    user=create_translations(filename='user', ),
    search=create_translations(filename='search', ),
    collections=create_translations(filename='collections', ),
    posts=create_translations(filename='posts', ),
    votes=create_translations(filename='votes', ),
    mix=create_translations(filename='mix', ),
    cmd_descriptions=create_translations(filename='cmd_descriptions', ),
)

httpx_client: httpx_AsyncClient = httpx_AsyncClient()
