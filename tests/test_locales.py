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
from typing import Callable

from importlib import reload as importlib_reload  # To reload python loaded module
from pathlib import Path
from subprocess import run as subprocess_run, CalledProcessError as subprocess_CalledProcessError

import pytest
from polib import pofile as polib_pofile

from app.config import LOCALES_PATH
from app.postconfig import translators

from app.entities.user import texts as user_texts
from app.entities.match import texts as match_texts
from app.entities.collection import texts as collection_texts
from app.entities.post import texts as post_texts
from app.entities.vote import texts as vote_texts
from app.entities.mix import texts as mix_texts
from app.entities.shared import texts as shared_texts

lang_dirs = [directory.name for directory in Path(LOCALES_PATH).iterdir() if directory.is_dir()]


def translator_decorator(gettext_func, used_msg_ids: set, lang: str, filename: str, ):
    excluded = {"OK", }  # Global exclude, indeed should be personal for every translator

    def wrapper(message: str, ):
        translated = gettext_func(message=message, )
        if translated == message and message not in excluded:  # If not translated and text kept the same
            raise Exception(
                f"Missing translation for string: {message}. Lang: {lang}, file: {filename}",  # pragma: no cover
            )
        used_msg_ids.add(message, )
        return translated

    return wrapper


@pytest.mark.parametrize(argnames="filename, translator", argvalues=vars(translators).items(), )
@pytest.mark.parametrize(argnames="lang", argvalues=lang_dirs, )
def test_translations(lang: str, filename: str, translator: Callable, ):
    used_msg_ids = set()
    po_file_path = f'{LOCALES_PATH}/{lang}/LC_MESSAGES/{filename}.po'
    setattr(
        # 1 - namespace with translators, 2 - key, 3 - new decorator
        translators, filename, translator_decorator(
            gettext_func=translator,
            used_msg_ids=used_msg_ids,
            lang=lang,
            filename=filename,
        )
    )
    for module in [
        user_texts,
        match_texts,
        collection_texts,
        post_texts,
        vote_texts,
        mix_texts,
        shared_texts,
    ]:  # Reloading only required is harder cuz single texts module uses multiple translations, reload all is ok
        importlib_reload(module)  # Apply decorated translators
    all_msg_ids = set(entry.msgid for entry in polib_pofile(po_file_path))  # Get total strings
    unused_translations = all_msg_ids - used_msg_ids  # Check that all translations from file was used
    error_str = (
        f'Not all translations were used in constants (unused {len(unused_translations)}).\n'
        f'Lang: {lang}. File: "{filename}" Unused: {unused_translations}'
    )
    assert not unused_translations, error_str


@pytest.mark.parametrize(argnames="lang", argvalues=lang_dirs, )
@pytest.mark.parametrize(argnames="attr_name", argvalues=vars(translators).keys(), )
def test_msg_fmt(attr_name: str, lang: str, ):
    """Check errors with msgfmt utility"""
    po_file_path = f'{LOCALES_PATH}/{lang}/LC_MESSAGES/{attr_name}.po'
    try:  # Try-except here helps to catch the key error rather than just call exit status 1
        subprocess_run(["msgfmt", "-c", po_file_path], check=True, capture_output=True, text=True, )
    except subprocess_CalledProcessError as e:  # pragma: no cover
        pytest.fail(e.stderr)  # Explicit raise target error
