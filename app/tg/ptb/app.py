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
from typing import TYPE_CHECKING, Callable, Literal, Coroutine
from json import load as json_load  # Parse file
from asyncio import sleep as asyncio_sleep

from telegram.error import TelegramError
from telegram.constants import ParseMode
from telegram.ext import ExtBot, ContextTypes, Application, ApplicationBuilder, PicklePersistence

from rubik_core.db import manager as db_manager
from rubik_core.entities.mix.model import Photo as AppPhotoModel
from rubik_core.shared.structures import Gender

"""Dots is relative path to app"""
from ...config import (
    PROJECT_ROOT_PATH,
    PICKLE_PATH,
    MAIN_ADMIN,
    LANGUAGE,
    CREATE_PUBLIC_DEFAULT_COLLECTIONS,
    CREATE_PERSONAL_DEFAULT_COLLECTIONS,
    DEBUG,
    PERSISTENT,
)
from ...postconfig import httpx_client, app_logger  # To close on shutdown

from app.tg import telethon

from .structures import CustomUserData, CustomBotData
from .entities.post.constants import PostsChannels
from .entities.post.forms import (
    Public as PublicPostForm,
    Personal as PersonalPostForm,
)
from .entities.collection.services import Collection as CollectionService
from .entities.mix.services import System as SystemService
# Handlers
from .entities.mix.handlers import error_handler as mix_error_handler
from .entities import available_handlers as entities_available_handlers
from .store_manager import available_handlers as store_manager_available_handlers
from .inline_mode import available_handlers as inline_mode_available_handlers
from custom_ptb.callback_context import CallbackContext

if TYPE_CHECKING:
    from pathlib import PosixPath
    from app.sctructures import LocalPost
    from app.tg.entities.collection.model import ICollection

COLLECTIONS_PATH: PosixPath = PROJECT_ROOT_PATH / 'app' / 'assets' / 'default_posts' / LANGUAGE


def read_file_data(path: PosixPath, mode: str = 'rb', ) -> bytes | str:
    with open(path, mode) as f:
        return f.read()


def collect_posts(path: PosixPath | str, ) -> list[tuple[PosixPath, dict]]:
    collected_dir_posts = []
    for post_dir_path in (list(path.iterdir())[:3] if DEBUG else list(path.iterdir())):
        with open(post_dir_path / 'data.json', 'rb') as file:
            post: LocalPost = json_load(file)
            collected_dir_posts.append((post_dir_path, post))
    return collected_dir_posts


async def get_food_collection_posts(bot: ExtBot, ) -> list:
    result = []
    for posts_dir_path, post_data in collect_posts(path=COLLECTIONS_PATH / 'еда', ):
        sent_message = await bot.send_photo(
            chat_id=PostsChannels.STORE.value,
            photo=read_file_data(path=posts_dir_path / post_data['image']),
            caption=post_data['text'],
            disable_notification=True,
        )
        result.append(sent_message)
    return result


async def get_art_collection_posts(bot: ExtBot, ) -> list:
    result = []
    for post_dir_path, post_data in collect_posts(COLLECTIONS_PATH / 'живопись'):
        sent_message = await bot.send_photo(
            chat_id=PostsChannels.STORE.value,
            caption=(
                f'{post_data["title"]}, - {post_data["artist"]}, {post_data["year"]}.\n'
                f'{post_data["description"]}\n'
                f'{post_data["location"]}.'
            ),
            photo=read_file_data(path=post_dir_path / post_data['image']),
            disable_notification=True,
        )
        result.append(sent_message, )
    return result


async def get_films_collection_posts(bot: ExtBot, ) -> list:
    result = []
    for post_dir_path, post_data in collect_posts(COLLECTIONS_PATH / 'кино'):
        sent_message = await bot.send_photo(
            chat_id=PostsChannels.STORE.value,
            caption=f'{post_data["title"]}, {post_data["year"]}, {post_data["country"]}.\n',
            photo=read_file_data(path=post_dir_path / post_data['image']),
            disable_notification=True,
        )
        result.append(sent_message, )
    return result


async def get_persons_collection_posts(bot: ExtBot, ) -> list:
    result = []
    for post_dir_path, post_data in collect_posts(COLLECTIONS_PATH / 'личности'):
        sent_message = await bot.send_photo(
            chat_id=PostsChannels.STORE.value,
            caption=read_file_data(path=post_dir_path / post_data['text'], mode='r', ),
            photo=read_file_data(path=post_dir_path / post_data['image']),
            disable_notification=True,
        )
        result.append(sent_message, )
    return result


async def get_animals_collection_posts(bot: ExtBot, ) -> list:
    result = []
    for post_dir_path, post_data in collect_posts(COLLECTIONS_PATH / 'животные'):
        sent_message = await bot.send_photo(
            chat_id=PostsChannels.STORE.value,
            caption=read_file_data(path=post_dir_path / post_data['text'], mode='r', ),
            photo=read_file_data(path=post_dir_path / post_data['image']),
            disable_notification=True,
        )
        result.append(sent_message, )
    return result


async def get_memes_collection_posts(bot: ExtBot, ) -> list:
    result = []
    for post_dir_path, post_data in collect_posts(COLLECTIONS_PATH / 'мемы'):
        sent_message = await bot.send_photo(
            chat_id=PostsChannels.STORE.value,
            photo=read_file_data(path=post_dir_path / post_data['image']),
            disable_notification=True,
        )
        result.append(sent_message, )
    return result


async def get_places_collection_posts(bot: ExtBot, ) -> list:
    result = []
    for post_dir_path, post_data in collect_posts(COLLECTIONS_PATH / 'места'):
        sent_message = await bot.send_photo(
            chat_id=PostsChannels.STORE.value,
            caption=(
                f'{post_data["name"]} - {post_data["location"]}.\n'
                f'{post_data["description"]}\n'
                f'координаты: {post_data["coordinates"]["latitude"]}, {post_data["coordinates"]["longitude"]}.'
            ),
            photo=read_file_data(path=post_dir_path / post_data['image']),
            disable_notification=True,
        )
        result.append(sent_message, )
    return result


async def get_music_collection_posts(bot: ExtBot, ) -> list:
    result = []
    for post_dir_path, post_data in collect_posts(COLLECTIONS_PATH / 'музыка'):
        sent_message = await bot.send_message(
            chat_id=PostsChannels.STORE.value,
            text=(
                f'{post_data["url"]}\n'
                f'{post_data["title"]} - {post_data["band"]}.\n'
                f'{post_data.get("album")}.\n'
                f'{post_data["year"]}.\n'
            ),
            disable_notification=True,
        )
        result.append(sent_message, )
    return result


async def get_poems_collection_posts(bot: ExtBot, ) -> list:
    result = []
    for post_dir_path, post_data in collect_posts(COLLECTIONS_PATH / 'стихи'):

        text = read_file_data(path=post_dir_path / post_data["текст"], mode="r", )
        sent_message = await bot.send_message(
            chat_id=PostsChannels.STORE.value,
            text=(  # TG requires escaping
                f'<b>{post_data["название"]} - {post_data["автор"]}.</b>\n\n'
                f'<blockquote>{text}</blockquote>\n\n'
                f'{post_data["год"]}.'
            ),
            parse_mode=ParseMode.HTML,
            disable_notification=True,
        )
        result.append(sent_message, )

    return result


def get_create_collection_funcs() -> dict[str, Callable[[ExtBot], Coroutine[None, None, list]]]:
    """Need for both, public and personal"""
    # TODO make translations; just map between stored and created collections
    return {
        'еда': get_food_collection_posts,
        'живопись': get_art_collection_posts,
        'животные': get_animals_collection_posts,
        'кино': get_films_collection_posts,
        'личности': get_persons_collection_posts,
        'мемы': get_memes_collection_posts,
        'места': get_places_collection_posts,
        'музыка': get_music_collection_posts,
        'стихи': get_poems_collection_posts,
    }


async def create_public_collections(bot: ExtBot, ) -> list[ICollection]:

    result = []

    already_created_collection_names = CollectionService.get_defaults_names(
        prefix=CollectionService.NamePrefix.PUBLIC,
    )
    local_collections = get_create_collection_funcs()
    [local_collections.pop(name, None) for name in already_created_collection_names]
    app_logger.info(msg=f'Collected collections: {", ".join(local_collections.keys()) or 0}.')
    for collection_name, send_collection_func in local_collections.items():
        created_collection_posts = []
        for sent_message in await send_collection_func(bot=bot, ):  # Call here to a bit reduce flooding
            post_form = PublicPostForm(
                author=SystemService.user,
                channel_id=PostsChannels.STORE.value,  # Or bot.id?
                message=sent_message,  # New feature (online mode) requires full message
                message_id=sent_message.message_id,
            )
            created_collection_posts.append(post_form.create(), )
            await asyncio_sleep(delay=1, )  # To preserve limits for future and prevent possible flood limit.
        SystemService.set_bots_votes_to_posts(posts=created_collection_posts, )
        collection = CollectionService.create_default(
            name=collection_name,
            posts=created_collection_posts,
            prefix=CollectionService.NamePrefix.PUBLIC,
        )
        result.append(collection, )
        app_logger.info(
            msg=(
                f'Created collection "{collection_name}", {len(created_collection_posts)} posts, ids: '
                f'{", ".join(str(post.id) for post in created_collection_posts)}.'
            )
        )
    return result


async def create_personal_collections(bot: ExtBot, ) -> None:

    already_created_collection_names = CollectionService.get_defaults_names(
        prefix=CollectionService.NamePrefix.PERSONAL,
    )
    for collection_name, send_collection_func in get_create_collection_funcs().items():
        if collection_name in already_created_collection_names:  # TODO need tests with a clear
            continue
        created_collection_posts = []
        for sent_message in await send_collection_func(bot=bot, ):  # Call here to a bit reduce flooding
            post_form = PersonalPostForm(
                author=SystemService.user,
                channel_id=PostsChannels.STORE.value,  # Or bot.id?
                message_id=sent_message.message_id,
            )
            created_collection_posts.append(post_form.create(), )
        SystemService.set_bots_votes_to_posts(posts=created_collection_posts, )
        CollectionService.create_default(
            name=collection_name,
            posts=created_collection_posts,
            prefix=CollectionService.NamePrefix.PERSONAL,
        )
    return


async def create_bots_default_photos(bot: ExtBot, ):
    for gender in Gender:
        try:
            gender_photos = (PROJECT_ROOT_PATH / 'app' / 'assets' / 'photos' / 'bots' / gender.name.lower()).iterdir()
        except FileNotFoundError:  # If no folder with a such gender
            continue
        already_created_photos = await validate_photos(
            bot=bot,
            photos=AppPhotoModel.CRUD.read_many(
                category=gender.name.lower(),
                connection=SystemService.connection,
            ),
            return_type='validated',
        )
        already_created_photos = {photo['key'] for photo in already_created_photos}
        for photo in gender_photos:
            if photo.name not in already_created_photos:
                message = await bot.send_photo(chat_id=MAIN_ADMIN, photo=photo, disable_notification=True, )
                AppPhotoModel.CRUD.create(
                    key=photo.name,
                    category=gender.name.lower(),
                    storage_type=AppPhotoModel.CRUD.StorageType.FILE_ID,
                    link=message.photo[-1].file_id,
                    connection=SystemService.connection,
                )


async def validate_photos(
        bot: ExtBot,
        photos: list[dict],
        return_type: Literal['all', 'validated', 'unvalidated'],
        raise_: bool = False,
) -> tuple[list[dict], list[dict]] | list[dict]:
    """Returns first validated photos, then missed photos"""
    result = ([], [])  # First list is validated photos, second list is missed
    for photo in photos:
        try:
            await bot.get_file(photo['link'])
            result[0].append(photo)
        except TelegramError as e:  # Invalid file_id
            if raise_:
                raise Exception(
                    f'file id of photo with index {photo} was obsolete and need to be replaced\n'
                    f'Try to use _set_cls_photos cls method to access new file ids\n'
                    f'Original error: {e}'
                )
            result[1].append(photo)
    if return_type.lower() == 'validated':
        return result[0]
    elif return_type.lower() == 'unvalidated':
        return result[1]
    else:
        return result


async def check_is_bot_has_access_to_posts_store(bot: ExtBot, ) -> None:
    try:
        await bot.get_chat(chat_id=PostsChannels.STORE.value, )
    except TelegramError:
        raise Exception(f'This bot has no access to posts channel store chat, channel: {PostsChannels.STORE.value}')
    return None


async def configure_app(
        bot: ExtBot,
        bot_data: CustomBotData,
        create_public_default_collections: bool,
        create_personal_default_collections: bool,
) -> None:  # Pass the class directly?
    db_manager.Postgres.init()
    await telethon.initialize_client()
    await create_bots_default_photos(bot=bot, )
    await check_is_bot_has_access_to_posts_store(bot=bot, )
    if create_public_default_collections is True:
        created_collections = await create_public_collections(bot=bot, )
        bot_data.inline_data.collections.extend(created_collections)  # Fill inline_data.
    if create_personal_default_collections is True:
        await create_personal_collections(bot=bot, )


async def post_init(application: Application, ):
    """Run this code after bot creation"""
    app_logger.info(msg='Staring post init', )
    await configure_app(
        bot=application.bot,
        bot_data=application.bot_data,
        create_public_default_collections=CREATE_PERSONAL_DEFAULT_COLLECTIONS,
        create_personal_default_collections=CREATE_PUBLIC_DEFAULT_COLLECTIONS,
    )
    print(await application.bot.get_me())


async def post_shutdown(app: Application, ):
    await telethon.shutdown_client()
    await httpx_client.aclose()
    if getattr(db_manager.Postgres, 'connection_pool', False, ):  # not exists if DB not initialized
        db_manager.Postgres.connection_pool.closeall()


def create_ptb_app_bone(bot: ExtBot, ) -> Application:
    context_types = ContextTypes(
        context=CallbackContext,
        user_data=CustomUserData,
        bot_data=CustomBotData,
    )
    application = (
        ApplicationBuilder()
        .bot(bot=bot, )
        .post_init(post_init=post_init, )
        .post_shutdown(post_shutdown=post_shutdown)
        .context_types(context_types=context_types, )
        # # .read_timeout()
        # .write_timeout()
    )
    if PERSISTENT:
        application.persistence(persistence=PicklePersistence(filepath=PICKLE_PATH, context_types=context_types), )
    application = application.build()
    app_logger.info(msg='PTB app bone created', )
    return application


def create_ptb_app(
        bot: ExtBot,
        handlers: list | tuple | dict | None = None,
        error_handler: Callable | None = None,
) -> Application:
    application = create_ptb_app_bone(bot=bot, )
    if handlers:
        application.add_handlers(handlers=handlers, )
    else:
        for entity_handlers in (
                inline_mode_available_handlers,
                store_manager_available_handlers,
                *entities_available_handlers,
        ):
            application.add_handlers(handlers=entity_handlers, )
    if error_handler:
        application.add_error_handler(callback=error_handler, block=False, )
    else:
        application.add_error_handler(callback=mix_error_handler, block=False, )
    app_logger.info(msg='PTB app complete created', )
    return application
