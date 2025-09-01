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
from typing import TYPE_CHECKING

import pytest

from rubik_core.generation import generator

from app.entities.match.texts import Search as SearchTexts
from app.entities.match.form import Target, IncorrectProfileValue, NoVotes, NoCovotes, NoSources

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from faker import Faker
    from app.entities.match.form import ITarget


class TestTarget:

    @staticmethod
    def test_repr(target_s: Target):
        assert target_s.__repr__()

    @staticmethod
    def test_handle_start_search_no_votes(mock_target: MagicMock, faker: Faker, ):
        mock_target.user.matcher.is_user_has_votes = False
        with pytest.raises(expected_exception=NoVotes):
            Target.handle_start_search(self=mock_target, text=faker.word())
        mock_target.user.matcher.search_user_votes.acow()
        mock_target.user.matcher.get_user_votes_sources.acow()

    @staticmethod
    def test_handle_target_sources_no_sources(mock_target: MagicMock, ):
        mock_target.user.matcher.is_user_has_covotes = False
        with pytest.raises(expected_exception=NoSources):
            Target.handle_target_sources(self=mock_target, )

    @staticmethod
    def test_handle_target_sources_no_covotes(mock_target: MagicMock, ):
        mock_target.sources = {'foo': 1, 'bar': True, 'egg': False, }
        mock_target.user.matcher.is_user_has_covotes = False
        with pytest.raises(expected_exception=NoCovotes):
            Target.handle_target_sources(self=mock_target, )
        mock_target.user.matcher.search_user_covotes.acow(channel_ids={'foo', 'bar', })

    @staticmethod
    def test_handle_source_cbk(mock_target: MagicMock, ):
        mock_target.sources = {1: False, 2: True, 3: False, }
        Target.handle_source_cbk(self=mock_target, channel_id=123, is_chosen=False, )
        mock_target.sources = mock_target.sources = {1: False, 2: True, 3: False, 123: False}
        Target.handle_source_cbk(self=mock_target, channel_id=0, is_chosen=True, )
        assert mock_target.sources == {1: True, 2: True, 3: True, 123: True, }
        Target.handle_source_cbk(self=mock_target, channel_id=0, is_chosen=False, )
        assert mock_target.sources == {1: False, 2: False, 3: False, 123: False, }

    @staticmethod
    def test_handle_goal(target_s: ITarget, faker: Faker, ) -> None:
        for _ in range(5):
            with pytest.raises(IncorrectProfileValue):  # Try incorrect values
                expected = target_s.goal
                target_s.handle_goal(text=faker.word())
            assert target_s.goal == expected  # Assert that goal is not changed
        for enum_goal, text_goal in zip(target_s.Goal, SearchTexts.TARGET_GOALS, strict=True):
            target_s.handle_goal(text=text_goal.lower())
            assert target_s.goal == enum_goal

    @staticmethod
    def test_handle_gender(target_s: ITarget, faker: Faker, ):
        """NewUser.handle_gender and TargetUser.handle_gender not identical"""
        [target_s.handle_gender(text=gender) for gender in SearchTexts.TARGET_GENDERS]  # Will raise on error
        # Test failed success
        for _ in range(5):  # Use variable
            with pytest.raises(IncorrectProfileValue):
                target_s.handle_gender(text=faker.word())

    @staticmethod
    def test_handle_age(target_s: ITarget, faker: Faker, ):
        """NewUser.handle_age and TargetUser.handle_age are not identical"""
        for age in [
            '', 'qwerty', faker.paragraph(), '01wrqw', SearchTexts.Buttons.SKIP, '4', '0', '9lk&^*',
            SearchTexts.Buttons.BACK,
        ]:
            with pytest.raises(IncorrectProfileValue):
                target_s.handle_age(text=age)
        for age in ['25', '2525', '5025', '9999', 'sad4fs2', ]:  # True
            target_s.handle_age(text=age)
            target_s.handle_age(text=''.join([str(x) for x in generator.gen_age_range()]))  # Will be sorted anyway
        target_s.handle_age(text=SearchTexts.Buttons.ANY_AGE)
        assert target_s.age_range == (target_s.Age.MIN, target_s.Age.MAX)

    @staticmethod
    def test_handle_show_option(target_s: ITarget, faker: Faker, ):
        target_s.handle_show_option(text=SearchTexts.Buttons.SHOW_ALL)
        target_s.handle_show_option(text=SearchTexts.Buttons.SHOW_NEW)
        with pytest.raises(IncorrectProfileValue):
            target_s.handle_show_option(text=faker.word())
