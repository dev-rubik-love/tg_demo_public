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

from app.entities.user.texts import Reg as RegTexts
from app.entities.user.form import IncorrectProfileValue, NewUser

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from faker import Faker
    from app.entities.user.form import INewUser


class TestNewUser:

    @staticmethod
    def test_repr(new_user_s: INewUser):
        assert new_user_s.__repr__()

    @staticmethod
    def test_handle_name(new_user_s: INewUser, faker: Faker, ) -> None:
        """No need to make call assertions on setters if actual == expected"""
        expected = faker.first_name()
        new_user_s.handle_name(text=expected)
        assert new_user_s.fullname == expected
        expected = f'{faker.first_name()} {faker.last_name()}'
        new_user_s.handle_name(text=expected)
        assert new_user_s.fullname == expected

    @staticmethod
    def test_handle_goal(new_user_s: INewUser, faker: Faker, ) -> None:
        for _ in range(5):
            with pytest.raises(IncorrectProfileValue):  # Try incorrect values
                expected = new_user_s.goal
                new_user_s.handle_goal(text=faker.word())
            assert new_user_s.goal == expected  # Assert that goal is not changed
        for enum_goal, text_goal in zip(new_user_s.Goal, RegTexts.REG_GOALS, strict=True):
            new_user_s.handle_goal(text=text_goal.lower())
            assert new_user_s.goal == enum_goal

    @staticmethod
    def test_handle_gender(new_user_s: INewUser, faker: Faker, ):
        for _ in range(5):
            with pytest.raises(IncorrectProfileValue):  # Try incorrect values
                expected = new_user_s.gender
                new_user_s.handle_gender(text=faker.word())
            assert new_user_s.gender == expected  # Assert that goal is not changed

        for enum_gender, text_gender in zip(new_user_s.Gender, RegTexts.REG_GENDERS, strict=True):
            new_user_s.handle_gender(text=text_gender)
            assert new_user_s.gender == enum_gender

    @staticmethod
    def test_handle_age(new_user_s: INewUser, faker: Faker, ) -> None:
        for age in ['4', '999', 'qwerty', faker.paragraph(), '01', '00wrqw',
                    RegTexts.Buttons.BACK, ]:  # TODO another source
            with pytest.raises(IncorrectProfileValue):
                new_user_s.handle_age(text=age)
        for expected_age, input_age in [
            (10, 'e1e0'), (42, 'sad4fs2'),
            (None, RegTexts.Buttons.SKIP),
            (99, '99lk&^*'),
        ]:
            new_user_s.handle_age(text=input_age, )
            assert new_user_s.age == expected_age

    @staticmethod
    def test_handle_location_text(new_user_s: INewUser, monkeypatch, ):
        for location_text, expected_country, expected_city in [
            ('France, Paris', 'France', 'Paris',),
            ('Italy', 'Italy', 'Paris',),  # Paris saved from the last iteration
            (RegTexts.Buttons.SKIP, None, None, ),
            (RegTexts.Buttons.BACK, RegTexts.Buttons.BACK, None, ),
        ]:
            new_user_s.handle_location_text(text=location_text)
            assert new_user_s.country == expected_country
            assert new_user_s.city == expected_city

    @staticmethod
    def test_add_photo(new_user_s: INewUser, ):
        for i in range(new_user_s.MAX_PHOTOS_COUNT):
            assert len(new_user_s.photos) == i
            assert new_user_s.add_photo(photo='foo', ) is True
        assert new_user_s.add_photo(photo='foo') is False
        assert len(new_user_s.photos) == new_user_s.MAX_PHOTOS_COUNT

    class TestRemovePhotos:
        @staticmethod
        def test_no_added_photos(mock_new_user: MagicMock, ):
            mock_new_user.photos = []
            result = NewUser.remove_photos(self=mock_new_user, )
            assert result is False

        @staticmethod
        def test_success(mock_new_user: MagicMock, ):
            mock_new_user.photos = ['foo']
            result = NewUser.remove_photos(self=mock_new_user, )
            assert mock_new_user.photos == []
            assert result is True

    @staticmethod
    def test_handle_comment(new_user_s: INewUser, faker: Faker, ) -> None:
        new_user_s.handle_comment(text=RegTexts.Buttons.SKIP)
        assert new_user_s.comment is None
        for _ in range(5):
            correct_comment = faker.paragraph()
            new_user_s.handle_comment(text=correct_comment)
            assert new_user_s.comment == correct_comment

    @staticmethod
    def test_create_user(mock_new_user: MagicMock, ):
        mock_new_user.photos = ['foo', ]
        NewUser.create(self=mock_new_user, )
        mock_new_user.user.CRUD.upsert.acow(
            user_id=mock_new_user.user.id,
            fullname=mock_new_user.fullname,
            goal=mock_new_user.goal,
            gender=mock_new_user.gender,
            age=mock_new_user.age,
            country=mock_new_user.country,
            city=mock_new_user.city,
            comment=mock_new_user.comment,
            connection=mock_new_user.user.connection,
        )
        mock_new_user.user.Photo.create.acow(user=mock_new_user.user, photo='foo', )
        assert mock_new_user.user.is_registered is True
