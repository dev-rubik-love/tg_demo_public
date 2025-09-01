from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Any as typing_Any
from unittest.mock import create_autospec, patch, AsyncMock
from functools import partial
from datetime import datetime as datetime_datetime

import pytest
from pytest import fixture
from telegram.constants import ChatType
from telegram import (
    Update,
    Chat,
    User as PtbUser,
    UsersShared,
    SharedUser,
    Message,
    CallbackQuery,
    InlineQuery,
    PhotoSize,
    UserProfilePhotos,
    MessageEntity,
    InlineKeyboardButton as tg_IKB,
    InlineKeyboardMarkup as tg_IKM,
    ChatFullInfo,
)
from telegram.ext import (
    Defaults as Defaults,
    ExtBot,
)

from app.tg.ptb.structures import CustomUserData
from app.tg.ptb.entities.vote import model as vote_model
from app.tg.ptb.entities.post import model as post_model
from app.tg.ptb.entities.collection import model as collection_model
from app.tg.ptb.entities.match import model as match_model
from app.tg.ptb.entities.user import model as user_model

from app.tg.ptb.entities.user.forms import NewUser as NewUserForm
from app.tg.ptb.entities.match.forms import Target as TargetForm
from app.tg.ptb.entities.post.forms import Public as PublicPostForm, Personal as PersonalPostForm

from app.tg.ptb.entities.view import View
from app.tg.ptb.app import create_ptb_app_bone
from custom_ptb import callback_context

from tests.conftest import patch_object


if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from telegram.ext import ExtBot as ExtBot
    from rubik_core.shared.structures import UserRaw
    from app.tg.ptb.entities.match.forms import ITarget as ITargetForm
    from app.tg.ptb.entities.user.forms import INewUser as INewUserForm


def get_text_cases(texts: list[str], upper: bool = True, lower: bool = True) -> set[str]:
    result = set()
    if isinstance(texts, str):
        raise TypeError('Expected list or tuple, got str')  # pragma: no cover
    for text in texts:
        if upper is True:
            result.add(text.upper())
        if lower is True:
            result.add(text.lower())
        result.add(text.capitalize())
        result.add(text.title())
    return result


@pytest.fixture(scope='function', )
def mock_app(mock_bot: ExtBot, ) -> MagicMock:
    result = create_autospec(spec=create_ptb_app_bone(bot=mock_bot, ), spec_set=True, )
    yield result


def get_user_profile_photos() -> UserProfilePhotos:
    return UserProfilePhotos(
        total_count=2,
        photos=[  # It's 2 photos, not 8
            [PhotoSize(file_id='1', file_unique_id='1', width=10, height=10),
             PhotoSize(file_id='2', file_unique_id='2', width=20, height=20),
             PhotoSize(file_id='1', file_unique_id='1', width=10, height=10),
             PhotoSize(file_id='2', file_unique_id='2', width=20, height=20), ],
            [PhotoSize(file_id='1', file_unique_id='1', width=10, height=10),
             PhotoSize(file_id='2', file_unique_id='2', width=20, height=20),
             PhotoSize(file_id='1', file_unique_id='1', width=10, height=10),
             PhotoSize(file_id='2', file_unique_id='2', width=20, height=20), ],
        ]
    )


@fixture(scope='session')
def photo_s() -> list[PhotoSize]:
    """photo (message.photo) represents list of photos with different sizes (the last one is the best quality)"""
    yield get_user_profile_photos().photos[-1]


@fixture(scope='session')  # Session cuz anyway immutable
def ikm() -> tg_IKM:
    keyboard = tg_IKM(
        inline_keyboard=(
            (tg_IKB(text='00', callback_data='00'), tg_IKB(text='01', callback_data='01'),),
            (tg_IKB(text='10', callback_data='10'), tg_IKB(text='11', callback_data='11'),),
        )
    )
    yield keyboard


def get_callback_query(
        callback_id: str,
        ptb_user: PtbUser,
        chat_id: str,
        message: Message,
        *args,
        **kwargs
) -> CallbackQuery:
    callback_query = CallbackQuery(
        id=callback_id,
        from_user=ptb_user,
        chat_instance=chat_id,
        message=message,
        *args,
        **kwargs
    )
    return callback_query


@fixture(scope='session')
def callback_fabric_s(
        ptb_user_s: PtbUser,
        message_s: Message,
        chat_s: Chat,
) -> Callable[..., CallbackQuery]:
    callback_query = partial(
        get_callback_query,
        callback_id=1,
        ptb_user=ptb_user_s,
        chat_id=chat_s.id,
        message=message_s,
    )
    return callback_query


@fixture(scope='session')
def callback_query_s(callback_fabric_s, ) -> CallbackQuery:
    yield callback_fabric_s()


@fixture(scope='function')
def mock_callback_query(callback_query_s: CallbackQuery, ) -> MagicMock:
    mock_callback_query = create_autospec(spec=callback_query_s, spec_set=True, )
    yield mock_callback_query


def get_chat(ptb_user_s: PtbUser, ) -> Chat:
    return Chat(id=ptb_user_s.id, type='private', username=ptb_user_s.username, )


@fixture(scope='session')
def chat_s(ptb_user_s: PtbUser, ):
    yield get_chat(ptb_user_s=ptb_user_s, )


def get_message(
        ptb_user: PtbUser,
        chat: Chat,
        date: datetime_datetime,
        bot: ExtBot,
        message_id: int = 1,
        cmd_text: str = None,
        *args,
        **kwargs,
) -> Message:
    if cmd_text:
        command_text = f'/{cmd_text}' if not cmd_text.startswith('/') else cmd_text
        kwargs['entities'] = [MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len(command_text))]
        kwargs['text'] = command_text
    result = Message(
        from_user=ptb_user,
        message_id=message_id,
        chat=chat,  # Required
        date=date,
        *args,
        **kwargs,
    )
    result.set_bot(bot=bot, )
    return result


@fixture(scope='session')
def message_fabric_s(
        ptb_user_s: PtbUser,
        chat_s: Chat,
        mock_bot_s: ExtBot,
        frozen_datetime: datetime_datetime,
) -> Message:
    result = partial(
        get_message,
        ptb_user=ptb_user_s,
        chat=chat_s,
        date=frozen_datetime,
        bot=mock_bot_s,
    )
    return result


@fixture(scope='session')
def message_s(
        message_fabric_s: Callable,
        mock_bot_s: MagicMock,
) -> Message:
    # User "get_message" because message need to dependency (mock_bot), direct usage will cause an infinite loop
    message = message_fabric_s()
    yield message


@fixture(scope='function')
def mock_message(message_s: Message, mock_bot: MagicMock, ) -> MagicMock:
    message = create_autospec(spec=message_s, spec_set=True, _bot=mock_bot)
    message.get_bot.return_value = mock_bot
    yield message


@fixture(scope='function', )
def mock_chat(chat_s: Chat, ) -> MagicMock:
    result = create_autospec(spec=chat_s, spec_set=True, )
    yield result


@fixture(scope='session', )
def chat_full_info_s() -> ChatFullInfo:
    result = ChatFullInfo(id=1, type=ChatType.GROUP, accent_color_id=0, max_reaction_count=100, )
    yield result


@fixture(scope='function', )
def mock_chat_full_info(chat_full_info_s: ChatFullInfo, ) -> MagicMock:
    result = create_autospec(spec=chat_full_info_s, spec_set=True, )
    yield result


def get_ptb_user(user_config: UserRaw, **kwargs, ) -> get_ptb_user:
    # In telegram username are with (@ and underscore), full_name are with space
    first_name, last_name = user_config['fullname'].split(' ')
    data = {
        'id': user_config['user_id'],
        # Telegram username is without "@" sign unlike "user.name"
        'username': user_config['fullname'].replace(' ', '_'),
        'first_name': first_name,
        'last_name': last_name,
        'is_bot': False,
        **kwargs,  # Override user_config with kwargs if collision
    }
    return PtbUser(**data, )


@fixture(scope='session')
def ptb_user_fabric_s(user_config: UserRaw, ) -> get_ptb_user:
    # In telegram username are with (@ and underscore), full_name are with space
    yield partial(get_ptb_user, user_config=user_config, )


@fixture(scope='session')
def ptb_user_s(user_config: UserRaw, ) -> PtbUser:
    """In telegram username are with underscore, full_name are with space"""
    yield get_ptb_user(user_config=user_config, )


@fixture(scope='function')
def ptb_tg_user_f(user_config: UserRaw, ) -> PtbUser:
    """In telegram username are with underscore, full_name are with space"""
    yield get_ptb_user(user_config=user_config, )


def get_update(
        update_id: int,
        message_fabric: Callable[..., Message],
        callback_fabric: Callable[..., CallbackQuery],
        ptb_user_fabric: Callable[..., PtbUser],
        message_kwargs: dict = None,
        callback_kwargs: dict = None,
        user_kwargs: dict = None,
        *args,
        **kwargs,
) -> Update:
    """
    Order of building update: bot + user_config -> user -> chat -> message + callback -> update
    """
    ptb_user = ptb_user_fabric(**user_kwargs or {}, )
    if message_kwargs:
        kwargs['message'] = message_fabric(ptb_user=ptb_user, **message_kwargs, )
    if callback_kwargs:
        kwargs['callback_query'] = callback_fabric(ptb_user=ptb_user, **callback_kwargs, )
    update = Update(
        update_id=update_id,
        *args,
        **kwargs,
    )
    update._effective_user = ptb_user
    return update


@fixture(scope='session')
def update_fabric_s(
        message_fabric_s: Callable[..., Message],
        callback_fabric_s: Callable[..., CallbackQuery],
        ptb_user_fabric_s: Callable[..., PtbUser],
        mock_bot_s: MagicMock,
) -> Callable[..., Update]:
    """Some old test uses preconfigured dynamically configurable update"""
    update = partial(
        get_update,
        update_id=1,
        message_fabric=message_fabric_s,
        callback_fabric=callback_fabric_s,
        ptb_user_fabric=ptb_user_fabric_s,
    )
    yield update


@fixture(scope='session')
def update_s(update_fabric_s: Callable, ) -> Update:
    update = update_fabric_s()
    yield update


@fixture(scope='function')
def mock_update(
        update_s: Update,
        mock_callback_query: MagicMock,
        mock_message: MagicMock,
) -> MagicMock:
    mock_update = create_autospec(
        spec=update_s,
        spec_set=True,
        callback_query=mock_callback_query,
        inline_query=create_autospec(
            spec=InlineQuery(id='1', from_user=mock_message.from_user, query='2', offset='0', ),
            spec_set=True,
        ),
        message=mock_message,
        effective_message=mock_message,
        effective_chat=mock_message.chat,
    )
    yield mock_update


@fixture(scope='function')
def mock_view_f(user_s: user_model.IUser, ) -> MagicMock:
    result = create_autospec(spec=View(user=user_s, ), spec_set=True, )
    yield result


@pytest.fixture(scope='function', )
def mock_context(
        mock_bot: MagicMock,
        mock_view_f: MagicMock,
        mock_user: MagicMock,
        mock_new_user: MagicMock,
        mock_public_post_form: MagicMock,
        mock_personal_post_form: MagicMock,
        mock_target: MagicMock,
) -> MagicMock:
    """
    Required in: inline_mode, store_manager, handlers, triggers (they may use own custom version)
    Already mocked can't be used with autospec
    Use already created mock bot and other objects?
    """
    # TODO python 3.10 create_autospec not stacks with dataclass(slots=True) without additional tricks,
    #  3.11, 3.12 does stacks
    # with patch.object(target=callback_context, attribute='Postgres', autospec=True, spec_set=True, ):
    #     context = callback_context.CallbackContext.from_update(
    #         update=update_s,
    #         application=create_ptb_app_bone(bot=ptb_bot_s, ),
    #     )
    with patch_object(target=callback_context.CallbackContext, attribute='connection', create=True, new=None, ):
        connection=AsyncMock()
        result = create_autospec(
            spec=callback_context.CallbackContext,
            instance=False,
            bot=mock_bot,
            connection=connection,
            db_params=callback_context.DbParams(connection=connection, )
        )
    result.application.persistence.flush = AsyncMock()
    result.view = mock_view_f
    user_data = CustomUserData()
    user_data.tmp_data.collections_to_share = CustomUserData.TmpData.CollectionsToShare(message_id_with_collections=1, )
    result.user_data.tmp_data = user_data.tmp_data
    result.user_data.forms = user_data.Forms(  # Fill the forms valid case if user jumps from form to form
        new_user=mock_new_user,
        target=mock_target,
        public_post=mock_public_post_form,
        personal_post=mock_personal_post_form,
    )
    result.user = mock_user
    yield result


@fixture(scope='session', autouse=True, )  # Have no idea why autouse fails without autouse
def ptb_bot_s(ptb_user_s: PtbUser, ) -> ExtBot:
    ext_bot = ExtBot(token='123:4:5', )  # Exactly such token to bypass token pre-validation
    ext_bot._commands = []  # In reality filled with telegram.botcommand.BotCommand; Assign manually to avoid api call
    ext_bot._initialized = True  # Bypass creating the real bot
    ExtBot._bot_user = ptb_user_s  # Bypass creating the real bot
    yield ext_bot


def get_ptb_bot(bot: ExtBot, ) -> MagicMock:
    mock_ext_bot = create_autospec(spec=bot, spec_set=True, )
    mock_ext_bot.defaults = Defaults(block=True)  # Some internal real bot config
    return mock_ext_bot


@fixture(scope='session', )
def mock_bot_s(ptb_bot_s: ExtBot, ) -> MagicMock:
    """Need for ptb tg session objects with bot"""
    mock_bot = get_ptb_bot(bot=ptb_bot_s, )
    yield mock_bot


@fixture(scope='function')
def mock_bot(ptb_bot_s: ExtBot, ) -> MagicMock:
    yield get_ptb_bot(bot=ptb_bot_s, )


@fixture(scope='package')
def mock_bot_p(ptb_bot_s: ExtBot, ) -> MagicMock:
    yield get_ptb_bot(bot=ptb_bot_s, )


def get_user(user_config: UserRaw, ptb_user: PtbUser, ):
    """init with "vars" can't be used because of properties (_connection, etc.) are unexpected args"""
    user = user_model.User(
        id=1,
        ptb=ptb_user,
        connection=typing_Any,
        photos=user_config['photos'],
        fullname=user_config['fullname'],
        goal=user_config['goal'],
        gender=user_config['gender'],
        age=user_config['age'],
        city=user_config['city'],
        country=user_config['country'],
        comment=user_config['comment'],
        is_registered=False,
    )
    return user


@fixture(scope='function', )
def user_f(user_config: UserRaw, ptb_tg_user_f: PtbUser, ) -> user_model.User:
    user = get_user(user_config=user_config, ptb_user=ptb_tg_user_f, )
    yield user


@fixture(scope='session', )
def user_s(user_config: UserRaw, ptb_user_s: PtbUser, ) -> user_model.User:
    user = get_user(user_config=user_config, ptb_user=ptb_user_s, )
    yield user


@fixture(scope='session', )
def ptb_user_s2(user_config: UserRaw, ptb_user_s: PtbUser, ) -> user_model.User:
    user = get_user(user_config=user_config, ptb_user=ptb_user_s)
    user.name = '@firstname2 lastname2'
    yield user


@fixture(scope='function', )
def mock_matcher(user_s: user_model.IUser, ) -> MagicMock:
    yield create_autospec(spec=user_s.matcher, spec_set=True, )


@fixture(scope='session', )
def match_s(
        user_s: user_model.IUser,
        ptb_user_s2: user_model.IUser,
) -> match_model.Match:
    match = match_model.Match(
        id=1,
        owner=user_s,
        user=ptb_user_s2,
        common_posts_perc=10,
        common_posts_count=80,
    )
    yield match


@fixture(scope='function', )
def mock_match(match_s: match_model.Match, ) -> MagicMock:
    yield create_autospec(spec=match_s, spec_set=True, )


@fixture(scope='function', )
def mock_user(user_s: user_model.IUser, ) -> MagicMock:
    mock_user = create_autospec(spec=user_s, collections=[], connection=user_s.connection, spec_set=True, )
    # mock_user.get_collections.return_value = [collection]  # Not all collections
    mock_user.matcher.is_user_has_covotes = False
    yield mock_user


@fixture(scope='session', )  # Rename me
def mock_user_s(user_s: user_model.User, ) -> MagicMock:
    mock_user = create_autospec(spec=user_s, collections=[], connection=user_s.connection, spec_set=True, )
    mock_user.matcher.is_user_has_covotes = False
    yield mock_user


@fixture(scope='function', )
def new_user_f(user_f: user_model.IUser, ) -> INewUserForm:
    yield NewUserForm(
        fullname=user_f.fullname,
        goal=user_f.goal,
        gender=user_f.gender,
        age=user_f.age,
        country=user_f.country,
        city=user_f.city,
        comment=user_f.comment,
        photos=user_f.photos,
        user=user_f,
    )


@fixture(scope='function', )
def mock_new_user(new_user_f: INewUserForm, ) -> MagicMock:
    yield create_autospec(spec=new_user_f, spec_set=True, )


@fixture(scope='function', )
def mock_public_post_form(user_s: user_model.User, ) -> MagicMock:
    post_form = PublicPostForm(author=user_s, channel_id=2, message_id=2, )
    mock_post_form = create_autospec(spec=post_form, spec_set=True, )
    yield mock_post_form


@fixture(scope='session', )
def public_post_s(user_s: user_model.User, message_s: Message, ) -> post_model.PublicPost:
    post = post_model.PublicPost(
        id=1,
        author=user_s,
        channel_id=2,
        message_id=3,
        message=message_s,
    )
    yield post


@fixture(scope='function', )
def mock_public_post(public_post_s: post_model.PublicPost, ) -> MagicMock:
    mock_post = create_autospec(spec=public_post_s, spec_set=True, )
    yield mock_post


@fixture(scope='session', )
def voted_public_post(
        public_post_s: post_model.IPublicPost,
        public_vote_s: vote_model.IPublicVote
) -> post_model.IVotedPublicPost:
    return post_model.VotedPublicPost(
        post=public_post_s,
        clicker_vote=public_vote_s,
    )


@fixture(scope='function', )
def mock_voted_public_post(
        voted_public_post: post_model.IVotedPublicPost,
) -> MagicMock:
    yield create_autospec(spec=voted_public_post, spec_set=True, )


@fixture(scope='session', )
def channel_public_post_s(
        public_post_s: post_model.PublicPost,
) -> post_model.ChannelPublicPost:
    attrs = vars(public_post_s).copy()
    del attrs['message']
    post = post_model.ChannelPublicPost(**attrs)
    yield post


@fixture(scope='function', )
def channel_public_post_f(
        public_post_s: post_model.PublicPost,
) -> post_model.ChannelPublicPost:
    attrs = vars(public_post_s).copy()
    del attrs['message']
    post = post_model.ChannelPublicPost(**attrs)
    yield post


@fixture(scope='function', )
def mock_channel_public_post(channel_public_post_f: post_model.ChannelPublicPost, ) -> MagicMock:
    mock_post = create_autospec(spec=channel_public_post_f, spec_set=True, )
    yield mock_post


@fixture(scope='session', )
def personal_post_s(user_s: user_model.User, ) -> post_model.PersonalPost:
    post = post_model.PersonalPost(
        id=1,
        author=user_s,
        channel_id=2,
        message_id=3,
    )
    yield post


@fixture(scope='function', )
def mock_personal_post(personal_post_s: post_model.PersonalPost) -> MagicMock:
    mock_post = create_autospec(spec=personal_post_s, spec_set=True, )
    yield mock_post


@fixture(scope='function', )
def mock_personal_post_form(user_s: user_model.User, ) -> MagicMock:
    post_form = PersonalPostForm(
        author=user_s,
        channel_id=1,
        message_id=1,
    )
    mock_sample = create_autospec(spec=post_form, spec_set=True, )
    yield mock_sample


@fixture(scope='session', )
def voted_personal_post(
        personal_post_s: post_model.PersonalPost,
        personal_vote_s: vote_model.PersonalVote
) -> post_model.VotedPersonalPost:
    return post_model.VotedPersonalPost(
        post=personal_post_s,
        clicker_vote=personal_vote_s,
        opposite_vote=personal_vote_s,
    )


@fixture(scope='function', )
def mock_voted_personal_post(
        voted_personal_post: post_model.VotedPersonalPost, ) -> MagicMock:
    yield create_autospec(spec=voted_personal_post, spec_set=True, )


@fixture(scope='session')
def public_vote_s(
        user_s: user_model.User,
) -> vote_model.PublicVote:
    yield vote_model.PublicVote(
        user=user_s,
        post_id=1,
        channel_id=2,
        message_id=3,
        value=vote_model.PublicVote.Value.POSITIVE,
    )


@fixture(scope='session')
def personal_vote_s(
        user_s: user_model.User,
) -> vote_model.PersonalVote:
    yield vote_model.PersonalVote(
        user=user_s,
        post_id=1,
        channel_id=2,
        message_id=3,
        value=vote_model.PersonalVote.Value.POSITIVE,
    )


@fixture(scope='session')
def collection_s(
        user_s: user_model.IUser,
        public_post_s: post_model.IPublicPost,
) -> collection_model.Collection:
    collection = collection_model.Collection(author=user_s, id=1, posts=[public_post_s, ], )
    yield collection


@fixture(scope='session')
def mock_collection_factory(collection_s: collection_model.Collection, ) -> Callable[[], [MagicMock]]:
    result = lambda: create_autospec(spec=collection_s, spec_set=True, )
    yield result


@fixture(scope='function')
def mock_collection(mock_collection_factory: Callable[[], [MagicMock]], ) -> MagicMock:
    result = mock_collection_factory()
    yield result


@fixture(scope='session')
def target_s(user_s: user_model.User, ) -> ITargetForm:
    yield TargetForm(
        user=user_s,
        goal=user_s.Matcher.Filters.Goal.BOTH,
        gender=user_s.Matcher.Filters.Gender.BOTH,
        age_range=(user_s.Age.MIN, user_s.Age.MAX),
        country=user_s.country,
        city=user_s.city,
    )


@fixture(scope='function')
def mock_target(target_s: TargetForm, ) -> MagicMock:
    mock_target = create_autospec(spec=target_s, spec_set=True, )
    yield mock_target


@fixture(scope='session', )
def bot_public_post_s(public_post_s: post_model.IPublicPost, ) -> post_model.IBotPublicPost:
    params = vars(public_post_s).copy()
    del params['posts_channel_message_id']  # Bot post doesn't have posts_channel_message_id
    yield post_model.BotPublicPost(**params, )


@fixture(scope='function', )
def mock_bot_public_post(bot_public_post_s: post_model.BotPublicPost, ) -> MagicMock:
    """User in test_post and test_system"""
    yield create_autospec(spec=bot_public_post_s, spec_set=True, )


@fixture(scope='function', )
def bot_personal_post_s(
        personal_post_s: post_model.IPersonalPost,
) -> post_model.IBotPersonalPost:
    yield post_model.BotPersonalPost(**vars(personal_post_s), )


@fixture(scope='function')
def mock_match_stats(user_s: user_model.User, ) -> MagicMock:
    spec = match_model.MatchStats(
        user=user_s,
        with_user_id=2,
        set_statistic=False,
    )
    result = create_autospec(spec=spec, spec_set=True, )
    yield result


# # # PATCHED # # #
@fixture(scope='function', )  # Will patch for entire scope (module) were was called
def patched_ptb_channel_public_post() -> MagicMock:
    with patch_object(post_model, 'ChannelPublicPost', ) as mock_post_cls:
        yield mock_post_cls


@fixture(scope='function', )
def patched_personal_post_cls(mock_user: MagicMock, ) -> MagicMock:
    with patch_object(post_model, 'PersonalPost', ) as mock_post_cls:
        yield mock_post_cls


@fixture(scope='function')  # Will patch during all the test
def patched_ptb_collection() -> MagicMock:
    with patch_object(collection_model, 'Collection', ) as m:
        yield m


@fixture(scope='session')
def matcher_s(user_s: user_model.User, ) -> match_model.IMatcher:
    result = user_s.matcher
    yield result


@fixture(scope='function')
def mock_matcher(matcher_s: match_model.IMatcher) -> MagicMock:
    result = create_autospec(spec=matcher_s, spec_set=True, )
    result.Filters.Age = match_model.Matcher.Filters.Age
    result._is_unfiltered_matches_already_set = False  # Set explicitly
    yield result


@pytest.fixture(scope='session', )
def shared_user_s() -> SharedUser:
    result = SharedUser(user_id=2, first_name='first_name', last_name='last_name', username='username', )
    yield result


@pytest.fixture(scope='function', )
def mock_shared_user(shared_user_s: SharedUser, ) -> MagicMock:
    result = create_autospec(spec=shared_user_s, spec_set=True, )
    yield result


@pytest.fixture(scope='session', )
def users_shared(shared_user_s: SharedUser, ) -> UsersShared:
    users_shared = UsersShared(request_id=1, users=(shared_user_s,), )
    yield users_shared
