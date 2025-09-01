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
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    pass


class StringFormatDefault(str):
    """Implement str.format method with default value (the first passed param to format method"""

    # Don't use keyword style cuz it will be passed to __new__ and will fail
    def __new__(cls, string: str, defaults: dict | Iterable, ) -> StringFormatDefault:
        if isinstance(defaults, dict, ):
            formatted_instance: StringFormatDefault = super().__new__(cls, string.format(**defaults), )
            formatted_instance.default_args = []
            formatted_instance.default_kwargs = defaults
        else:
            formatted_instance = super().__new__(cls, string.format(*defaults), )
            formatted_instance.default_args = defaults
            formatted_instance.default_kwargs = {}
        formatted_instance.original = string
        return formatted_instance

    def format(self: StringFormatDefault, *args, **kwargs) -> str:
        if self.default_args == args or self.default_kwargs == kwargs:
            return self
        return self.original.format(*(*self.default_args, *args,), **{**self.default_kwargs, **kwargs, })


def calculate_average_distributions(items: list[int], limit: int, ) -> list[int]:
    if not items:
        return items
    result = [0] * len(items)
    queue = items[:]
    while limit:
        average = max(limit // len(items), 1)
        for i, item in enumerate(queue):
            if item:
                if item <= average:
                    result[i] += item
                    limit -= item
                else:
                    result[i] += average
                    limit -= average
                if not limit:
                    return result
                queue[i] = max(item - average, 0)
        else:
            return result
