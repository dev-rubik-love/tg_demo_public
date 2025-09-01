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
from typing import TYPE_CHECKING, Callable


if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from telegram import CallbackQuery
    from app.tg.ptb.entities.user.model import IUser
    from app.tg.ptb.entities.vote.model import PublicVote, PersonalVote


class TestVote:

    class TestCallbackToVote:
        """ test_callback_to_vote """

        @staticmethod
        def test_callback_to_vote(
                user_s: IUser,
                public_vote_s: PublicVote,
                personal_vote_s: PersonalVote,
                callback_fabric_s: Callable[..., CallbackQuery],
        ):
            for vote in (public_vote_s, personal_vote_s):
                assert vote.from_callback(user=user_s, callback=callback_fabric_s(data='1'), )

        @staticmethod
        def test_channel_id(
                user_s: IUser,
                public_vote_s: PublicVote,
                mock_callback_query: MagicMock,
        ):
            """ Test channel_id source if btn pressed in channel when user is undefined"""
            mock_callback_query.data = '1 2 3'
            for from_user in (mock_callback_query.message.from_user, None):
                mock_callback_query.message.from_user = from_user
                public_vote_s.from_callback(user=user_s, callback=mock_callback_query, )
