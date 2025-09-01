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
from app.tg.entities.match.form import (
    Target as TgTargetForm,
    ITarget as ITgTargetForm,  # Need to inheritance
)


if TYPE_CHECKING:
    pass


class ITarget(ITgTargetForm, ABC, ):
    pass


class Target(TgTargetForm, ITarget, ):
    pass
