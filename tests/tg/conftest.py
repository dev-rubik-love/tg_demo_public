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
from unittest.mock import create_autospec

from pytest import fixture

from telegram import Location

from app.tg.entities.user.model import User
from app.tg.entities.user.form import NewUser as NewUserForm

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from rubik_core.shared.structures import UserRaw
    from app.tg.entities.user.form import INewUser as INewUserForm


@fixture(scope='session', )
def tg_location() -> Location:
    location = Location(45, 45, )
    yield location


@fixture(scope='function')
def tg_user_f(user_config: UserRaw, ) -> User:
    """Need for the form"""
    yield User(
        id=1,
        fullname=user_config['fullname'],
        goal=User.Goal(user_config['goal']),
        gender=User.Gender(user_config['gender']),
        age=user_config['age'],
        country=user_config['country'],
        city=user_config['city'],
        comment=user_config['comment'],
        photos=user_config['photos'],
    )


@fixture(scope='function')
def tg_new_user_f(tg_user_f: User, ) -> NewUserForm:
    yield NewUserForm(
        fullname=tg_user_f.fullname,
        goal=tg_user_f.goal,
        gender=tg_user_f.gender,
        age=tg_user_f.age,
        country=tg_user_f.country,
        city=tg_user_f.city,
        comment=tg_user_f.comment,
        photos=tg_user_f.photos,
        user=tg_user_f,
    )


@fixture(scope='function', )
def mock_tg_new_user(tg_new_user_f: INewUserForm, ) -> MagicMock:
    yield create_autospec(spec=tg_new_user_f, spec_set=True, )

