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
from typing import TYPE_CHECKING, Callable

import pytest
from telegram.ext import Application

from app.tg.ptb.entities.post import texts, handlers_definition, constants

from tests.tg.ptb.triggers.conftest import check_is_all_mock_handlers_called, cancel_body
from tests.tg.ptb.conftest import get_text_cases


if TYPE_CHECKING:
    from faker import Faker
    from telegram import Location, PhotoSize, Update, User as PtbUser


@pytest.fixture(scope='module', autouse=True, )
def check_is_all_called():
    """Internal test to check that all handlers was called"""
    gen = check_is_all_mock_handlers_called(handlers=(handlers_definition.available_handlers,))
    next(gen, )  # Executes before tests
    yield
    next(gen, None)  # Executes after all the tests. None to prevent StopIteration


class TestCreatePublicPost:
    cls_to_test = handlers_definition.CreatePublicPostCH

    async def test_entry_point(
            self,
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
    ):
        update = update_fabric_s(message_kwargs=dict(cmd_text=constants.CREATE_PUBLIC_POST_S, ), )
        assert (update.effective_chat.id, update.effective_user.id,) not in self.cls_to_test.CH._conversations
        await app_s_with_mock_handlers.process_update(update=update, )
        self.cls_to_test.entry_point.callback.assert_called_once()

    # TODO different_post content, not only text
    async def test_sample_handler(
            self,
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
    ):
        update = update_fabric_s(message_kwargs=dict(text='foo', ), )
        self.cls_to_test.CH._conversations[(update.effective_chat.id, update.effective_user.id,)] = 0
        await app_s_with_mock_handlers.process_update(update=update, )
        self.cls_to_test.sample_handler.callback.assert_called_once()

    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=[texts.Posts.Public.Buttons.SEND]))
    async def test_confirm_handler(
            self,
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        self.cls_to_test.confirm_handler.callback.reset_mock()
        update = update_fabric_s(message_kwargs=dict(text=text, ), )
        self.cls_to_test.CH._conversations[(update.effective_chat.id, update.effective_user.id,)] = 1
        await app_s_with_mock_handlers.process_update(update=update, )
        self.cls_to_test.confirm_handler.callback.assert_called_once()

    async def test_cancel(
            self,
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            monkeypatch,
    ):
        await cancel_body(
            update_fabric=update_fabric_s,
            ptb_app=app_s_with_mock_handlers,
            ch=self.cls_to_test.CH,
            callback=self.cls_to_test.cancel_handler.callback,
            monkeypatch=monkeypatch,
        )


class TestCreatePersonalPost:

    class AttrsForInnerClasses:
        cls_to_test = handlers_definition.CreatePersonalPostCH

    cls_to_test = AttrsForInnerClasses.cls_to_test

    async def test_entry_point(
            self,
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
    ):
        update = update_fabric_s(message_kwargs=dict(cmd_text=constants.CREATE_PERSONAL_POST_S, ), )
        assert (update.effective_chat.id, update.effective_user.id,) not in self.cls_to_test.CH._conversations
        await app_s_with_mock_handlers.process_update(update=update, )
        self.cls_to_test.entry_point.callback.assert_called_once()
        pytest.skip()
        key = (update.effective_chat.id, update.effective_user.id,)
        assert self.cls_to_test.CH._conversations[key] == self.cls_to_test.entry_point.callback()

    class TestEntryPointHandler(AttrsForInnerClasses, ):
        """entry_point_handler"""

        async def body(self, ptb_app: Application, update: Update, ):
            self.cls_to_test.entry_point_handler.callback.reset_mock()
            self.cls_to_test.CH._conversations[(update.effective_chat.id, update.effective_user.id,)] = 0
            await ptb_app.process_update(update=update, )
            self.cls_to_test.entry_point_handler.callback.assert_called_once()
            pytest.skip()
            key = (update.effective_chat.id, update.effective_user.id,)
            assert self.cls_to_test.CH._conversations[key] == self.cls_to_test.entry_point_handler.callback()

        async def test_location(
                self,
                update_fabric_s: Callable[..., Update],
                app_s_with_mock_handlers: Application,
                tg_location: Location,
        ):
            update = update_fabric_s(message_kwargs={'location': tg_location, }, )
            await self.body(ptb_app=app_s_with_mock_handlers, update=update, )

        async def test_photo(
                self,
                update_fabric_s: Callable[..., Update],
                app_s_with_mock_handlers: Application,
                photo_s: PhotoSize,
        ):
            update = update_fabric_s(message_kwargs={'photo': photo_s, }, )
            await self.body(ptb_app=app_s_with_mock_handlers, update=update, )

        @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['foo']))
        async def test_text(
                self,
                update_fabric_s: Callable[..., Update],
                app_s_with_mock_handlers: Application,
                text: str,
        ):
            """entry_point"""
            update = update_fabric_s(message_kwargs={'text': text})
            # self.cls_to_test.CH._conversations[(update.effective_chat.id, update.effective_user.id,)] = 0
            await self.body(ptb_app=app_s_with_mock_handlers, update=update, )

    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['foo']))
    async def test_text(
            self,
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        self.cls_to_test.sample_handler.callback.reset_mock()
        update = update_fabric_s(message_kwargs={'text': text, }, )
        self.cls_to_test.CH._conversations[(update.effective_chat.id, update.effective_user.id,)] = 1
        await app_s_with_mock_handlers.process_update(update=update, )
        self.cls_to_test.sample_handler.callback.assert_called_once()
        pytest.skip()
        key = (update.effective_chat.id, update.effective_user.id,)
        assert self.cls_to_test.CH._conversations[key] == self.cls_to_test.sample_handler.callback()

    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['foo']))
    async def test_collection_handler(
            self,
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        self.cls_to_test.collections_handler.callback.reset_mock()
        update = update_fabric_s(message_kwargs={'text': text, }, )
        self.cls_to_test.CH._conversations[(update.effective_chat.id, update.effective_user.id,)] = 2
        await app_s_with_mock_handlers.process_update(update=update, )
        self.cls_to_test.collections_handler.callback.assert_called_once()
        pytest.skip()
        key = (update.effective_chat.id, update.effective_user.id,)
        assert self.cls_to_test.CH._conversations[key] == self.cls_to_test.collections_handler.callback()

    @pytest.mark.parametrize(argnames='flag', argvalues=['0', '1'])
    async def test_collection_name_cbk_handler(
            self,
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            ptb_user_s: PtbUser,
            faker: Faker,
            flag: str,
    ):
        for _ in range(3):
            for text in get_text_cases(texts=faker.words()):
                self.cls_to_test.collection_name_cbk_handler.callback.reset_mock()
                """update_post_status"""
                update = update_fabric_s(
                    callback_kwargs={'data': f'{handlers_definition.CollectionCbks.CHOOSE_COLLECTION} {text} {flag}', },
                )
                self.cls_to_test.CH._conversations[(update.effective_chat.id, update.effective_user.id,)] = 2
                await app_s_with_mock_handlers.process_update(update=update, )
                self.cls_to_test.collection_name_cbk_handler.callback.assert_called_once()
                pytest.skip()
                key = (update.effective_chat.id, update.effective_user.id,)
                assert self.cls_to_test.CH._conversations[key] == self.cls_to_test.collection_name_cbk_handler.callback()

    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=[texts.Posts.Public.Buttons.SEND]))
    async def test_confirm_handler(
            self,
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        self.cls_to_test.confirm_handler.callback.reset_mock()
        # The same with "TestCreatePublicPost.post_confirm_handler"
        update = update_fabric_s(message_kwargs={'text': texts.Posts.Personal.Buttons.READY, }, )
        self.cls_to_test.CH._conversations[(update.effective_chat.id, update.effective_user.id,)] = 2
        await app_s_with_mock_handlers.process_update(update=update, )
        self.cls_to_test.confirm_handler.callback.assert_called_once()
        pytest.skip()
        key = (update.effective_chat.id, update.effective_user.id,)
        assert self.cls_to_test.CH._conversations[key] == self.cls_to_test.confirm_handler.callback()

    async def test_cancel(
            self,
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            monkeypatch,
    ):
        await cancel_body(
            update_fabric=update_fabric_s,
            ptb_app=app_s_with_mock_handlers,
            ch=self.cls_to_test.CH,
            callback=self.cls_to_test.cancel_handler.callback,
            monkeypatch=monkeypatch,
        )


class TestSharePersonalPosts:
    cls_to_test = handlers_definition.SharePersonalPostsCh

    async def test_entry_point(
            self, update_fabric_s: Callable[..., Update], app_s_with_mock_handlers: Application, ):
        update = update_fabric_s(message_kwargs={'cmd_text': constants.SHARE_PERSONAL_POSTS_S, }, )
        assert (update.effective_chat.id, update.effective_user.id,) not in self.cls_to_test.CH._conversations
        await app_s_with_mock_handlers.process_update(update=update, )
        self.cls_to_test.entry_point.callback.assert_called_once()
        pytest.skip()
        key = (update.effective_chat.id, update.effective_user.id,)
        assert self.cls_to_test.CH._conversations[key] == self.cls_to_test.entry_point.callback()

    async def test_recipient_handler(
            self,
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            monkeypatch,
    ):
        update = update_fabric_s(message_kwargs={'cmd_text': '1', }, )
        self.cls_to_test.CH._conversations[update.effective_chat.id, update.effective_user.id] = 0
        await app_s_with_mock_handlers.process_update(update=update, )
        self.cls_to_test.recipient_handler.callback.assert_called_once()
        pytest.skip()
        key = (update.effective_chat.id, update.effective_user.id,)
        assert self.cls_to_test.CH._conversations[key] == self.cls_to_test.recipient_handler.callback()

    async def test_cancel(
            self,
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            monkeypatch,
    ):
        await cancel_body(
            update_fabric=update_fabric_s,
            ptb_app=app_s_with_mock_handlers,
            ch=self.cls_to_test.CH,
            callback=self.cls_to_test.cancel_handler.callback,
            monkeypatch=monkeypatch,
        )


class TestRequestPersonalPosts:
    cls_to_test = handlers_definition.RequestPersonalPostsCH

    async def test_entry_point(
            self,
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
    ):
        update = update_fabric_s(message_kwargs={'cmd_text': constants.REQUEST_PERSONAL_POSTS_S, }, )
        assert (update.effective_chat.id, update.effective_user.id,) not in self.cls_to_test.CH._conversations
        await app_s_with_mock_handlers.process_update(update=update, )
        self.cls_to_test.entry_point.callback.assert_called_once()
        pytest.skip()
        key = (update.effective_chat.id, update.effective_user.id,)
        assert self.cls_to_test.CH._conversations[key] == self.cls_to_test.entry_point.callback()

    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['1', '2', 'sdfs%W']))  # users ids
    async def test_recipient_handler(
            self,
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        self.cls_to_test.recipient_handler.callback.reset_mock()
        update = update_fabric_s(message_kwargs={'text': text, }, )
        self.cls_to_test.CH._conversations[(update.effective_chat.id, update.effective_user.id,)] = 0
        await app_s_with_mock_handlers.process_update(update=update, )
        self.cls_to_test.recipient_handler.callback.assert_called_once()
        pytest.skip()
        key = (update.effective_chat.id, update.effective_user.id,)
        assert self.cls_to_test.CH._conversations[key] == self.cls_to_test.recipient_handler.callback()

    async def test_cancel(
            self,
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            monkeypatch,
    ):
        await cancel_body(
            update_fabric=update_fabric_s,
            ptb_app=app_s_with_mock_handlers,
            ch=self.cls_to_test.CH,
            callback=self.cls_to_test.cancel_handler.callback,
            monkeypatch=monkeypatch,
        )


async def test_get_my_personal_posts_cmd(
        update_fabric_s: Callable[..., Update],
        app_s_with_mock_handlers: Application,
):
    update = update_fabric_s(message_kwargs={'cmd_text': constants.GET_MY_PERSONAL_POSTS_S, }, )
    await app_s_with_mock_handlers.process_update(update=update, )
    handlers_definition.get_my_personal_posts_cmd.callback.assert_called_once()


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=[constants.GET_PUBLIC_POST_S], ))
async def test_get_public_post_cmd(
        update_fabric_s: Callable[..., Update],
        app_s_with_mock_handlers: Application,
        text: str,
):
    handlers_definition.get_public_post_cmd.callback.reset_mock()
    update = update_fabric_s(message_kwargs={'cmd_text': text, }, )
    await app_s_with_mock_handlers.process_update(update=update, )
    handlers_definition.get_public_post_cmd.callback.assert_called_once()


@pytest.mark.parametrize(argnames='flag', argvalues=['0', '1'])
async def test_request_personal_post_cbk(
        update_fabric_s: Callable[..., Update],
        app_s_with_mock_handlers: Application,
        ptb_user_s: PtbUser,
        flag: str,
):
    handlers_definition.request_personal_post_cbk.callback.reset_mock()
    update = update_fabric_s(
        callback_kwargs={'data': f'{constants.Cbks.REQUEST_PERSONAL_POSTS} {ptb_user_s.id} {flag}', },
    )
    await app_s_with_mock_handlers.process_update(update=update, )
    handlers_definition.request_personal_post_cbk.callback.assert_called_once()


async def test_update_public_post_status_cbk(
        update_fabric_s: Callable[..., Update],
        app_s_with_mock_handlers: Application,
        ptb_user_s: PtbUser,
):
    """update_post_status"""
    update = update_fabric_s(callback_kwargs={'data': constants.Cbks.UPDATE_PUBLIC_POST_STATUS, }, )
    await app_s_with_mock_handlers.process_update(update=update, )
    handlers_definition.update_public_post_status_cbk.callback.assert_called_once()


async def test_share_personal_post_cbk(
        update_fabric_s: Callable[..., Update],
        app_s_with_mock_handlers: Application,
):
    update = update_fabric_s(callback_kwargs={'data': constants.Cbks.ACCEPT_PERSONAL_POSTS, }, )
    await app_s_with_mock_handlers.process_update(update=update, )
    handlers_definition.share_personal_posts_cbk.callback.assert_called_once()
