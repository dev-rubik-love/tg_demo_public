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

from app.utils import StringFormatDefault  # Allow to use default arg for str.format
from app.postconfig import translators

"""
Some format values are accessible on this stage but python don't allow to fill only few of format placeholders.
For this case there a workaround - double brackets ( {{ PLACEHOLDER }} ).
See: https://stackoverflow.com/a/18343661/11277611
"""

MORE_ACTIONS = translators.shared("MORE_ACTIONS")

TMP_RESTRICTION = translators.shared("TMP_RESTRICTION")

# The same for posts and collections
USER_GOT_SHARE_PROPOSAL = translators.shared("USER_GOT_SHARE_PROPOSAL")  # format(USERNAME)
USER_GOT_REQUEST_PROPOSAL = translators.shared("USER_GOT_REQUEST_PROPOSAL")  # format(USER_ID, USERNAME )
USER_DECLINED_REQUEST_PROPOSAL = translators.shared("USER_DECLINED_REQUEST_PROPOSAL")  # format(USER_ID, )
# Common for many
USER_DECLINED_SHARE_PROPOSAL = translators.shared("USER_DECLINED_SHARE_PROPOSAL")  # format(USER_ID, )

REG_REQUIRED = translators.shared("REG_REQUIRED")  # format(REG_CMD, )
POSSIBLE_INACTIVE_ACCOUNT = translators.shared("POSSIBLE_INACTIVE_ACCOUNT")
ENTER_THE_NUMBER = translators.shared("ENTER_THE_NUMBER")

I_AM_BOT = translators.shared("I_AM_BOT")
EASTER_EGG = translators.shared("EASTER_EGG_KEYBOARD")

INTERNAL_ERROR = translators.shared("INTERNAL_ERROR")
HERE_PROFILE_PREVIEW = translators.user("HERE_PROFILE_PREVIEW")
USER_NOT_REGISTERED = translators.user("USER_NOT_REGISTERED")  # Rename to "USER_HAS_NOT_PROFILE" ?


class Profile:
    """Titles of the fields, aka keys"""
    NAME = translators.shared("NAME")
    GOAL = translators.shared("GOAL")
    GENDER = translators.shared("GENDER")
    AGE = translators.shared("AGE")
    LOCATION = translators.shared("LOCATION")
    ABOUT = translators.shared("ABOUT")


class Words:
    """Single words cls"""
    FROM = translators.shared("FROM")
    UNKNOWN = translators.shared("UNKNOWN")
    OK = translators.shared("OK")
    GO = translators.shared("GO")
    HELP = translators.shared("HELP")
    SEND = translators.shared("SEND")
    FORWARD = translators.shared("FORWARD")
    CONTINUE = translators.shared("CONTINUE")
    READY = FINISH = translators.shared("READY")
    COMPLETE = translators.shared("COMPLETE")
    COMPLETED = translators.shared("COMPLETED")
    CANCELED = translators.shared("CANCELED")
    GOODBYE = translators.shared("GOODBYE")
    SKIP = translators.shared("SKIP")
    BACK = translators.shared("BACK")
    CANCEL = translators.shared("CANCEL")
    PENDING = translators.shared("PENDING")
    # Kinda buttons
    ALLOW = translators.shared("ALLOW")
    DISALLOW = translators.shared("DISALLOW")
    ACCEPT = translators.shared("ACCEPT")
    WAIT = translators.shared("WAIT")
    DECLINE = translators.shared("DECLINE")
    HIDE = translators.shared("HIDE")
    SHOW_PROFILE = translators.shared("SHOW_PROFILE")


class Warn:
    UNSKIPPABLE_STEP = translators.shared("UNSKIPPABLE_STEP")
    UNCLICKABLE_BUTTON = translators.shared("UNCLICKABLE_BUTTON")
    UNKNOWN_BUTTON = translators.shared("UNKNOWN_BUTTON")
    MISUNDERSTAND = translators.shared("MISUNDERSTAND")
    ALAS_USER_NOT_FOUND = translators.shared("ALAS_USER_NOT_FOUND")
    TEXT_TOO_LONG = translators.shared("TEXT_TOO_LONG")  # format(MAX_TEXT_LEN, USED_TEXT_LEN, )
    ERROR_EXPLANATION = translators.shared("COMMON_ERROR_EXPLANATION")
    ERROR_LOCATION_SERVICE = translators.shared("ERROR_LOCATION_SERVICE")
    INCORRECT_FINISH = translators.shared("INCORRECT_FINISH")  # format(Words.FINISH, )
    INCORRECT_SEND = translators.shared("INCORRECT_SEND")
    INCORRECT_CONTINUE = translators.shared("INCORRECT_CONTINUE")
    INCORRECT_USER = translators.shared("INCORRECT_USER")


Warn.INCORRECT_CONTINUE = StringFormatDefault(
    string=Warn.INCORRECT_CONTINUE,
    defaults=dict(MISUNDERSTAND=Warn.MISUNDERSTAND, CONTINUE=Words.CONTINUE, CANCEL=Words.CANCEL, ),
)
Warn.INCORRECT_FINISH = Warn.INCORRECT_FINISH.format(MISUNDERSTAND=Warn.MISUNDERSTAND, READY=Words.READY)
FOR_READY = ASK_CONFIRM = StringFormatDefault(
    string=translators.shared("FOR_READY"),
    defaults={'READY': Words.READY},
)


class CmdDescriptions:
    HERE_COMMANDS = translators.cmd_descriptions("HERE_COMMANDS")
    FAQ = translators.cmd_descriptions("FAQ")
    BOT_USER_COMMANDS = translators.cmd_descriptions("BOT_USER_COMMANDS")
    PUBLIC_SEARCH = translators.cmd_descriptions("PUBLIC_SEARCH")
    START = translators.cmd_descriptions("START")
    SEARCH = translators.cmd_descriptions("SEARCH")
    REG = translators.cmd_descriptions("REG")
    PUBLIC_POST = translators.cmd_descriptions("PUBLIC_POST")
    PERSONAL_POST = translators.cmd_descriptions("PERSONAL_POST")
    SHARE_PERSONAL_POSTS = translators.cmd_descriptions("SHARE_PERSONAL_POSTS")
    REQUEST_PERSONAL_POSTS = translators.cmd_descriptions("REQUEST_PERSONAL_POSTS")
    GET_NEW_PUBLIC_POST = translators.cmd_descriptions("GET_NEW_PUBLIC_POST")
    GET_PERSONAL_POSTS = translators.cmd_descriptions("GET_PERSONAL_POSTS")
    GET_COLLECTIONS = translators.cmd_descriptions("GET_COLLECTIONS")
    GET_STAT = translators.cmd_descriptions("GET_STAT")
    PUBLIC_MODE = translators.cmd_descriptions("PUBLIC_MODE")
    PERSONAL_MODE = translators.cmd_descriptions("PERSONAL_MODE")
    SHOW_SAMPLE = translators.cmd_descriptions("SHOW_SAMPLE")
    DONATE = translators.cmd_descriptions("DONATE")
