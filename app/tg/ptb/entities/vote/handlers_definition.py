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

from telegram.ext import CallbackQueryHandler

from . import handlers
from .constants import Cbks


def create_accept_public_vote_cbk() -> CallbackQueryHandler:
    result = CallbackQueryHandler(
        callback=handlers.public_vote_cbk_handler,
        pattern=Cbks.PUBLIC_VOTE_R,
    )
    return result


def create_accept_channel_public_vote_cbk() -> CallbackQueryHandler:
    result = CallbackQueryHandler(
        callback=handlers.channel_public_vote_cbk_handler,
        pattern=Cbks.CHANNEL_PUBLIC_VOTE_R,  # Different vote behavior with regular public vote
    )
    return result


def create_accept_personal_vote_cbk() -> CallbackQueryHandler:
    result = CallbackQueryHandler(
        callback=handlers.personal_vote_cbk_handler,
        pattern=Cbks.PERSONAL_VOTE_R,
    )
    return result


accept_public_vote_cbk = create_accept_public_vote_cbk()
accept_personal_vote_cbk = create_accept_personal_vote_cbk()
accept_channel_public_vote_cbk = create_accept_channel_public_vote_cbk()

available_handlers = (
    accept_public_vote_cbk,
    accept_personal_vote_cbk,
    accept_channel_public_vote_cbk,
)
