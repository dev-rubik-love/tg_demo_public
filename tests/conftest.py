from __future__ import annotations
from unittest import mock
# from unittest.mock import create_autospec, patch, Mock, CallableMixin  # For isintance check
from typing import TYPE_CHECKING, Any as typing_Any
from functools import wraps
import tracemalloc
import datetime

import pytest

from rubik_core.shared import structures as core_shared_structures

from rubik_core.entities.match import structures as match_structures

from rubik_core.entities.user.model import User as AppUser

from app.entities.user.form import NewUser as AppNewUserForm
from app.entities.match.form import Target as AppTargetForm
from app.entities.post.form import PublicPost as AppPublicPostForm, PersonalPost as AppPersonalPostForm

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from app.entities.post.form import IPublicPost as IAppPublicPostForm, IPersonalPost as IAppPersonalPostForm

"""
# 1 https://docs.python.org/3/faq/programming.html#
    why-do-lambdas-defined-in-a-loop-with-different-values-all-return-the-same-result
"""


@pytest.fixture(autouse=True, scope='session', )
def patch_mock() -> None:
    """ Set alias Mock.assert_called_once_with -> Mock.acow"""

    # noinspection PyUnresolvedReferences
    orig_setup_func = mock._setup_func  # Exists but not listed in `__all__`

    def wrapper(funcopy, mock_object, sig):
        """
        unittest.mock just extends function with set of mock methods in the similar way
        """
        funcopy.acow = mock_object.assert_called_once_with
        return orig_setup_func(funcopy, mock_object, sig)

    mock._setup_func = wrapper  # Set alias for crete_autospec result function
    mock.CallableMixin.acow = mock.Mock.assert_called_once_with  # Set alias for mock base class
    yield


@wraps(mock.patch.object)  # Keep original annotations
def patch_object(*args, **kwargs, ):
    """Automatically add `spec_set=True` and `autospec=True` to the patch.object call"""

    kwargs = kwargs | {k: v for k, v in zip(('target', 'attribute', 'new',), (*args,), )}
    if 'create' not in kwargs:
        if 'new' not in kwargs:  # autospec creates the mock for you. Can't specify autospec and new.
            kwargs.setdefault('spec_set', True, )
        if (  # Can't autospec already mock
                'new_callable' not in kwargs
                and not isinstance(getattr(kwargs['target'], kwargs['attribute'], ), mock.Mock, )
        ):
            kwargs.setdefault('autospec', True, )
    return mock.patch.object(**kwargs, )


def get_total_memory_usage(start: tracemalloc.Snapshot, end: tracemalloc.Snapshot, ):  # pragma: no cover
    top_stats = end.compare_to(start, 'lineno')
    total_memory = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0) / (1024 * 1024)
    return total_memory


def trace_memory_deco(func):  # pragma: no cover
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_snapshot = tracemalloc.take_snapshot()
        result = func(*args, **kwargs)  # Execute the wrapped function
        total_memory_usage = get_total_memory_usage(start=start_snapshot, end=tracemalloc.take_snapshot(), )
        print(f"\nA Summary memory used in {func.__qualname__}:\n{total_memory_usage} MB\n")
        return result

    return wrapper


@pytest.fixture(scope='session', autouse=False, )
def tracemalloc_s():  # pragma: no cover
    """For modules, classes, etc"""
    tracemalloc.start()
    yield
    tracemalloc.stop()


def trace_memory_logic(scope_name: str, ):  # pragma: no cover
    start_snapshot = tracemalloc.take_snapshot()
    yield start_snapshot
    total_memory_usage = get_total_memory_usage(start=start_snapshot, end=tracemalloc.take_snapshot())
    print(f"\nTotal memory used in {scope_name}:\n{total_memory_usage} MB")


@pytest.fixture(scope='module', )  # pragma: no cover
def trace_memory_module():
    yield from trace_memory_logic(scope_name="module", )


@pytest.fixture(scope='class', )  # pragma: no cover
def trace_memory_class():
    yield from trace_memory_logic(scope_name="class", )


@pytest.fixture(scope='function', )  # pragma: no cover
def trace_memory_func(request, ):
    yield from trace_memory_logic(scope_name=f"func {request.node.name}", )


@pytest.fixture(scope='session')
def frozen_datetime() -> datetime.datetime:
    result = datetime.datetime(2022, 10, 21, 14, 6, 29, 271546)
    yield result


def get_photos() -> list[str]:
    return ['1', '2', '3', '4', '5', ]


def get_user_config() -> core_shared_structures.UserRaw:
    return core_shared_structures.UserRaw(
        user_id=1,
        fullname='firstname1 lastname1',
        goal=1,
        gender=1,
        age=25,
        country='country',
        city='city',
        comment='bot',
        photos=get_photos(),
    )


@pytest.fixture(scope='session')
def user_config() -> core_shared_structures.UserRaw:
    yield get_user_config()


@pytest.fixture(scope='session')
def public_post_form_s(user_s: AppUser, ) -> AppPublicPostForm:
    yield AppPublicPostForm(author=user_s, channel_id=2, message_id=2, )


@pytest.fixture(scope='session')
def personal_post_form_s(user_s: AppUser, ) -> IAppPublicPostForm:
    yield AppPersonalPostForm(author=user_s, channel_id=2, message_id=2, )


@pytest.fixture(scope='function')
def personal_post_form_f(user_s: AppUser, ) -> IAppPublicPostForm:
    yield AppPersonalPostForm(author=user_s, channel_id=2, message_id=2, )


@pytest.fixture(scope='function')
def mock_public_post_form(public_post_form_s: IAppPublicPostForm, ) -> MagicMock:
    yield mock.create_autospec(spec=public_post_form_s, spec_set=True, )


@pytest.fixture(scope='function')
def mock_personal_post_form(personal_post_form_s: IAppPersonalPostForm, ) -> MagicMock:
    mock_form = mock.create_autospec(
        spec=personal_post_form_s,
        spec_set=True,
        MAX_COLLECTIONS_COUNT=personal_post_form_s.MAX_COLLECTIONS_COUNT,
        user_collections_count=0,
    )
    yield mock_form


def get_user(user_config: core_shared_structures.UserRaw, ) -> AppUser:
    user_config = user_config or get_user_config()
    user = AppUser(
        connection=typing_Any,
        id=user_config['user_id'],
        fullname=user_config['fullname'],
        goal=AppUser.Goal(user_config['goal']),
        gender=AppUser.Gender(user_config['gender']),
        age=user_config['age'],
        country=user_config['country'],
        city=user_config['city'],
        comment=user_config['comment'],
        is_registered=True,
    )
    return user


@pytest.fixture(scope='session')
def target_s(user_s, ) -> AppTargetForm:
    yield AppTargetForm(
        user=user_s,
        goal=core_shared_structures.Goal.BOTH,
        gender=AppTargetForm.Mapper.Matcher.Filters.Gender.BOTH,
        age_range=(core_shared_structures.Age.MIN, core_shared_structures.Age.MAX),
        country=user_s.country,
        city=user_s.city,
    )


@pytest.fixture(scope='function')
def mock_target(target_s: AppTargetForm, ) -> MagicMock:
    yield mock.create_autospec(spec=target_s, spec_set=True, )


@pytest.fixture(scope='session')
def user_s(user_config: core_shared_structures.UserRaw, ) -> AppUser:
    result = get_user(user_config=user_config, )
    yield result


@pytest.fixture(scope='session')
def new_user_s(user_s: AppUser, ) -> AppNewUserForm:
    yield AppNewUserForm(
        user=user_s,
        fullname=user_s.fullname,
        goal=user_s.goal,
        gender=user_s.gender,
        age=user_s.age,
        country=user_s.country,
        city=user_s.city,
        comment=user_s.comment,
    )


@pytest.fixture(scope='function')
def mock_new_user(new_user_s: AppNewUserForm, ):
    result = mock.create_autospec(spec=new_user_s, spec_set=True, )
    yield result


@pytest.fixture(scope='session')
def covote() -> match_structures.Covote:
    covote = match_structures.Covote(id=1, user_id=2, count_common_interests=10, )
    yield covote
