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
from unittest.mock import patch
from pytest import fixture
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest import FixtureRequest


@fixture(scope='function', )
def patched_logger(request: FixtureRequest, ):
    """
    The dynamic version of a simple logger patching implementation to adhere to DRY principles.
    Each test witch uses this fixture should have app_logger in the target (test) function.
    The `request` provides context for the currently testing module, allowing the patching of
    the `app_logger` in the `handlers` variable.
    """
    with patch.object(target=request.module.handlers, attribute='app_logger', autospec=True, spec_set=True, ) as result:
        yield result
