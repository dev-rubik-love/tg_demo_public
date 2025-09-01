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
from abc import ABC

from rubik_core.entities.mix.service import System as CoreSystem, ISystem as ICoreSystem

from ..vote.model import PublicVote as PtbPublicVote
from ..user.model import User as PtbUser

if TYPE_CHECKING:
    from ..user.model import IUser as IPtbUser
    from ..vote.model import IPublicVote as IPtbPublicVote


class ISystem(ICoreSystem, ABC):

    class Mapper(ABC):
        User: IPtbUser
        PublicVote: IPtbPublicVote


class System(CoreSystem, ISystem, ):
    class Mapper:
        User = PtbUser
        PublicVote = PtbPublicVote

    # user = Mapper.User(id=CoreSystem.user.id, connection=CoreSystem.user.connection, )
