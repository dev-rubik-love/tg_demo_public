from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC

from rubik_core.entities.match.model import (
    Match as AppMatch,
    IMatch as IAppMatch,
    Matcher as AppMatcher,
    IMatcher as IAppMatcher,
    MatchStats as AppMatchStats,
    IMatchStats as IAppMatchStats,
)

if TYPE_CHECKING:
    pass


class IMatch(IAppMatch, ABC, ):
    pass


class Match(AppMatch, IMatch, ):
    pass


class IMatcher(IAppMatcher, ABC, ):
    pass


class Matcher(AppMatcher, IMatcher, ):
    pass


class IMatchStats(IAppMatchStats, ABC, ):
    pass


class MatchStats(AppMatchStats, IMatchStats, ):
    pass
