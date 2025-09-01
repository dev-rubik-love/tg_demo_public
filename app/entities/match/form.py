from __future__ import annotations
from typing import TYPE_CHECKING, Protocol, Type
from abc import ABC, abstractmethod

# To inherit restrict properties
from rubik_core.entities.match.model import Matcher as CoreMatcher
from rubik_core.entities.user.exceptions import IncorrectProfileValue
from rubik_core.shared.utils import get_num_from_text

from .texts import Search as SearchTexts
from ..shared.constants import BACK_R
from ..shared.exceptions import NoVotes, NoSources, NoCovotes

if TYPE_CHECKING:
    from rubik_core.entities.user.model import IUser as ICoreUser
    from rubik_core.entities.match.model import IMatcher as ICoreMatcher


# noinspection PyTypeChecker
class TargetProtocol(Protocol):
    """Instance attrs"""
    user: ICoreUser
    goal: ICoreMatcher.Filters.Goal | None
    gender: ICoreMatcher.Filters.Gender | None
    age_range: tuple[int, int] | None
    country: str | None
    city: str | None
    filters: ICoreMatcher.Filters | None
    sources: dict[int, bool]


class ITarget(ABC, TargetProtocol, ):

    class Mapper(ABC, ):
        Matcher: Type[ICoreMatcher]

    # noinspection PyTypeChecker
    Goal: ICoreMatcher.Filters.Goal | None
    # noinspection PyTypeChecker
    Gender: ICoreMatcher.Filters.Gender | None
    # noinspection PyTypeChecker
    Age: ICoreMatcher.Filters.Age | None
    sources: dict

    back_btn_disabled: bool

    @abstractmethod
    def handle_start_search(self, text: str, ):
        pass

    @abstractmethod
    def handle_target_sources(self, ):
        pass

    @abstractmethod
    def handle_source_cbk(self, channel_id: int, is_chosen: bool, ) -> None:
        pass

    @abstractmethod
    def handle_goal(self, text: str, ):
        pass

    @abstractmethod
    def handle_gender(self, text: str, ):
        pass

    @abstractmethod
    def handle_age(self, text: str, ):
        pass

    @abstractmethod
    def handle_show_option(self, text: str, ):
        pass


class Target(ITarget, ):

    class Mapper:
        Matcher = CoreMatcher

    Goal = CoreMatcher.Filters.Goal
    Gender = CoreMatcher.Filters.Gender
    Age = CoreMatcher.Filters.Age

    back_btn_disabled: bool = True

    def __init__(
            self,
            user: ICoreUser,
            goal: Goal | None = None,
            gender: Gender | None = None,
            age_range: tuple[int, int] | None = None,
            country: str | None = None,
            city: str | None = None,
            filters: CoreMatcher.Filters | None = None,
    ):
        self.user = user
        self.goal = goal
        self.gender = gender
        self._age_range = age_range
        self.country = country
        self.city = city
        self.filters: ICoreMatcher.Filters = filters or self.Mapper.Matcher.Filters()
        self.sources: dict[int, bool] = {}

    def __repr__(self, ):
        d = {
            'self': object.__repr__(self, ),
            'goal': self.goal,
            'gender': self.gender,
            'age_range': self.age_range,
            'country': self.country,
            'city': self.city,
            'filters': self.filters,
        }
        return repr({k: v for k, v in d.items() if v is not None}) + '\n'

    @property  # Just to sort values, no validation
    def age_range(self, ) -> tuple[int, int] | None:
        return self._age_range

    @age_range.setter
    def age_range(self, value: tuple[int, int] | None, ) -> None:
        self._age_range = value
        if value is not None:
            # Mypy unable to detect that sorted(value) returns the same len as value
            self._age_range = tuple(sorted(value))  # type: ignore[assignment]

    @classmethod
    def get_age_from_text(cls, text: str, ) -> int | bool:
        num = get_num_from_text(text=text, )
        if num is None or not cls.Age.MIN <= num <= cls.Age.MAX:
            return False
        return num

    def handle_start_search(self, text: str, ) -> None:
        text = text.lower().strip()
        if not BACK_R.match(text) or self.back_btn_disabled:
            self.user.matcher.search_user_votes()
            self.sources = {source: True for source in self.user.matcher.get_user_votes_sources()}
            if self.user.matcher.is_user_has_votes is False:
                raise NoVotes

    def handle_target_sources(self, ) -> None:
        if all(is_chosen is False for is_chosen in self.sources.values()):
            raise NoSources
        self.user.matcher.search_user_covotes(
            channel_ids={source for source, is_chosen in self.sources.items() if is_chosen},
        )
        if self.user.matcher.is_user_has_covotes is False:
            raise NoCovotes

    def handle_source_cbk(self, channel_id: int, is_chosen: bool, ) -> None:
        if channel_id == 0 and is_chosen is True:  # Set all to True
            self.sources.update({channel_id: True for channel_id in self.sources.keys()})
        elif channel_id == 0 and is_chosen is False:  # Set all to False
            # Don't use clear(), we need keep true and false for keyboard selected/unselected buttons
            self.sources.update({channel_id: False for channel_id in self.sources.keys()})
        else:
            self.sources[channel_id] = is_chosen

    def handle_goal(self, text: str, ) -> None:
        text = text.lower().strip()
        if not BACK_R.match(text) or self.back_btn_disabled:
            if text == SearchTexts.Buttons.I_WANNA_CHAT.lower():
                self.goal = self.Goal.CHAT
            elif text == SearchTexts.Buttons.I_WANNA_DATE.lower():
                self.goal = self.Goal.DATE
            elif text == SearchTexts.Buttons.I_WANNA_CHAT_AND_DATE.lower():
                self.goal = self.Goal.BOTH
            else:
                raise IncorrectProfileValue

    def handle_gender(self, text: str, ) -> None:
        text = text.lower().strip()
        if not BACK_R.match(text) or self.back_btn_disabled:
            if text == SearchTexts.Buttons.MALE.lower():
                self.gender = self.Gender.MALE
            elif text == SearchTexts.Buttons.FEMALE.lower():
                self.gender = self.Gender.FEMALE
            elif text == SearchTexts.Buttons.ANY_GENDER.lower():
                self.gender = self.Gender.BOTH
            else:
                raise IncorrectProfileValue

    def handle_age(self, text: str, ) -> None:
        text = text.lower().strip()
        if not BACK_R.match(text) or self.back_btn_disabled:
            if age := self.get_age_from_text(text=text, ):
                self.age_range = (age, age)
            elif all(
                    (  # Just as "and"
                            min_age := self.get_age_from_text(text=text[:2], ),
                            max_age := self.get_age_from_text(text=text[2:], )
                    )
            ):
                self.age_range = (min_age, max_age,)
            elif text == SearchTexts.Buttons.ANY_AGE.lower():
                self.age_range = (self.Age.MIN, self.Age.MAX)
            else:
                raise IncorrectProfileValue

    def handle_show_option(self, text: str, ) -> None:
        """
        This func is called after actual search and only sets results without affecting the real search or crud
        Notice: don't confuse target form filters and matcher filter
        """
        text = text.lower().strip()
        if not BACK_R.match(text) or self.back_btn_disabled:
            # Use startswith cuz text contain num of matches too
            if text.startswith(SearchTexts.Buttons.SHOW_ALL.lower()):
                self.filters.match_type = self.filters.MatchType.ALL_MATCHES
            elif text.startswith(SearchTexts.Buttons.SHOW_NEW.lower()):
                self.filters.match_type = self.filters.MatchType.NEW_MATCHES
            else:
                raise IncorrectProfileValue
        self.user.matcher.filters.match_type = self.filters.match_type
