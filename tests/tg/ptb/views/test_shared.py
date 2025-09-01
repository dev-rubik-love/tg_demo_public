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
from typing import TYPE_CHECKING, Any as typing_Any

from pytest import mark as pytest_mark, fixture as pytest_fixture
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.helpers import mention_html
from telegram import (
    InputMediaPhoto,
    MessageId,
    InlineKeyboardMarkup as tg_IKM,
    InlineKeyboardButton as tg_IKB,
    ReplyKeyboardMarkup as tg_RKM,
    ReplyKeyboardRemove,
)

from app.tg.ptb.entities.shared import view
from app.tg.ptb.entities.shared import texts

from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from telegram import SharedUser, Message

    from app.tg.ptb.entities.shared.view import IProfileBase
    from app.tg.ptb.entities.user.model import IUser


class TestWarn:
    @staticmethod
    async def test_incorrect_finish(mock_view_f: MagicMock, ):
        result = await view.Shared.Warn.incorrect_finish(self=mock_view_f.warn, )
        mock_view_f.warn.bot.send_message.acow(
            chat_id=mock_view_f.warn.id,
            text=texts.Warn.INCORRECT_FINISH,
        )
        assert result == mock_view_f.warn.bot.send_message.return_value

    @staticmethod
    async def test_text_too_long(mock_view_f: MagicMock, ):
        result = await view.Shared.Warn.text_too_long(self=mock_view_f.warn, max_symbols=123, used_symbols=123, )
        mock_view_f.warn.bot.send_message.acow(
            chat_id=mock_view_f.warn.id,
            text=texts.Warn.TEXT_TOO_LONG.format(
                MAX_TEXT_LEN=123,
                USED_TEXT_LEN=123,
            ),
            reply_markup=view.Keyboards.cancel
        )
        assert result == mock_view_f.warn.bot.send_message.return_value

    @staticmethod
    async def test_unskippable_step(mock_view_f: MagicMock, ):
        result = await view.Shared.Warn.unskippable_step(self=mock_view_f.warn, )
        mock_view_f.warn.bot.send_message.acow(
            chat_id=mock_view_f.warn.id,
            text=texts.Warn.UNSKIPPABLE_STEP,
        )
        assert result == mock_view_f.warn.bot.send_message.return_value

    @staticmethod
    async def test_incorrect_send(mock_view_f: MagicMock, ):
        result = await view.Shared.Warn.incorrect_send(self=mock_view_f.warn, )
        mock_view_f.warn.bot.send_message.acow(
            chat_id=mock_view_f.warn.id,
            text=texts.Warn.INCORRECT_SEND
        )
        assert result == mock_view_f.warn.bot.send_message.return_value

    @staticmethod
    async def test_incorrect_continue(mock_view_f: MagicMock, ):
        result = await view.Shared.Warn.incorrect_continue(self=mock_view_f.warn, )
        mock_view_f.warn.bot.send_message.acow(
            chat_id=mock_view_f.warn.id,
            text=texts.Warn.INCORRECT_CONTINUE.format(CONTINUE=texts.Words.CONTINUE, )
        )
        assert result == mock_view_f.warn.bot.send_message.return_value

    @staticmethod
    async def test_user_not_found(mock_view_f: MagicMock, ):
        result = await view.Shared.user_not_found(self=mock_view_f.warn, )
        mock_view_f.warn.bot.send_message.acow(
            chat_id=mock_view_f.warn.id,
            text=texts.Warn.ALAS_USER_NOT_FOUND.format(BOT_USERNAME=f'@{mock_view_f.warn.bot.username}'),
        )
        assert result == mock_view_f.warn.bot.send_message.return_value

    @staticmethod
    async def test_incorrect_user(mock_view_f: MagicMock, ):
        result = await view.Shared.Warn.incorrect_user(self=mock_view_f.warn, )
        mock_view_f.warn.bot.send_message.acow(
            chat_id=mock_view_f.warn.id,
            text=texts.Warn.INCORRECT_USER,
        )
        assert result == mock_view_f.warn.bot.send_message.return_value

    @staticmethod
    async def test_nan_help_msg(mock_view_f: MagicMock):
        result = await view.Shared.Warn.nan_help_msg(self=mock_view_f, )
        mock_view_f.bot.send_message.acow(
            text=f'{texts.Warn.MISUNDERSTAND}\n{texts.ENTER_THE_NUMBER}',
            chat_id=mock_view_f.id
        )
        assert result == mock_view_f.bot.send_message.return_value

    @staticmethod
    async def test_unclickable_button(mock_update: MagicMock, ):
        result = await view.Shared.unclickable_button(tooltip=mock_update.callback_query, )
        mock_update.callback_query.answer.acow(text=texts.Warn.UNCLICKABLE_BUTTON, )
        assert result == mock_update.callback_query.answer.return_value


async def test_say_user_got_share_proposal(mock_view_f: MagicMock, shared_user_s: SharedUser, ):
    result = await view.Shared.say_user_got_share_proposal(self=mock_view_f, shared_recipient=shared_user_s)
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=texts.USER_GOT_SHARE_PROPOSAL.format(
            USERNAME=mention_html(
                user_id=shared_user_s.user_id,
                name=view.extract_shared_user_name(shared_user=shared_user_s, ),
            ), ),
        parse_mode=ParseMode.HTML,  # HTML is a bit safer cuz not requiring escaping
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_say_user_got_request(mock_view_f: MagicMock, shared_user_s: SharedUser, ):
    result = await view.Shared.say_user_got_request_proposal(self=mock_view_f, shared_recipient=shared_user_s, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=texts.USER_GOT_REQUEST_PROPOSAL.format(
            USERNAME=mention_html(
                user_id=shared_user_s.user_id,
                name=view.extract_shared_user_name(shared_user=shared_user_s, ),
            ), ),
        parse_mode=ParseMode.HTML,
    )
    assert result == mock_view_f.bot.send_message.return_value


@pytest_mark.parametrize(
    argnames='keyword, keyboard',
    argvalues=[
        ('foo', view.Keyboards.cancel_factory(buttons=['foo', ])),
        (texts.Words.READY, view.Keyboards.ready_cancel),
    ], )
async def test_notify_ready_keyword(mock_view_f: MagicMock, keyword: str, keyboard: tg_RKM, ):
    result = await view.Shared.notify_ready_keyword(self=mock_view_f, keyword=keyword, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=texts.FOR_READY.format(READY=keyword, ),
        reply_markup=keyboard,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_cancel(mock_view_f: MagicMock, ):
    result = await view.Shared.cancel(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=texts.Words.CANCELED,
        reply_markup=view.Keyboards.remove(),
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_easter_egg(mock_view_f: MagicMock, ):
    await view.Shared.easter_egg(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=texts.EASTER_EGG,
        reply_markup=view.Keyboards.remove(),
    )
    mock_view_f.bot.delete_message(
        chat_id=mock_view_f.bot.send_message.return_value.chat_id,
        message_id=mock_view_f.bot.send_message.return_value.message_id,
    )


async def test_location_service_error(mock_view_f: MagicMock, ):
    result = await view.Shared.location_service_error(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=texts.Warn.ERROR_LOCATION_SERVICE,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_user_declined_share_proposal(mock_view_f: MagicMock, ):
    result = await view.Shared.user_declined_share_proposal(
        self=mock_view_f,
        id=1,
        decliner_username='foo',
    )
    mock_view_f.bot.send_message.acow(
        chat_id=1,
        text=texts.USER_DECLINED_SHARE_PROPOSAL.format(DECLINER_USERNAME='foo'),
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_user_declined_request_proposal(mock_view_f: MagicMock, ):
    result = await view.Shared.user_declined_request_proposal(self=mock_view_f, id=2, decliner_username='name', )
    mock_view_f.bot.send_message.acow(
        chat_id=2,
        text=texts.USER_DECLINED_REQUEST_PROPOSAL.format(DECLINER_USERNAME='name'),
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_remove_sharing_message(mock_message: MagicMock, ):
    result = await view.Shared.remove_sharing_message(message=mock_message, )
    mock_message.delete.acow()
    assert result == mock_message.delete.return_value


class TestCheckMessageExistence:
    """test_check_message_existence"""

    @staticmethod
    async def test_exist(mock_view_f: MagicMock, ):
        result = await view.Shared.check_message_existence(self=mock_view_f, chat_id=1, message_id=2, )
        mock_view_f.bot.copy_message.acow(
            chat_id=view.PostsChannels.STORE.value,
            from_chat_id=1,
            message_id=2,
        )
        mock_view_f.bot.delete_message.acow(
            chat_id=view.PostsChannels.STORE.value,
            message_id=mock_view_f.bot.copy_message.return_value.message_id,
        )
        assert result is True

    @staticmethod
    async def test_not_exist(mock_view_f: MagicMock, ):
        mock_view_f.bot.copy_message.side_effect = TelegramError('')
        result = await view.Shared.check_message_existence(self=mock_view_f, chat_id=1, message_id=2, )
        assert result is False


class TestInternalError:
    """test_internal_error"""

    @staticmethod
    @pytest_mark.parametrize(argnames='force_alert', argvalues=(True, False,))
    async def test_tooltip(mock_view_f: MagicMock, mock_callback_query: MagicMock, force_alert: bool, ):
        result = await view.Shared.internal_error(
            self=mock_view_f, tooltip=mock_callback_query, force_alert=force_alert, )
        mock_callback_query.answer.acow(text=texts.INTERNAL_ERROR, show_alert=force_alert, )
        assert result == mock_callback_query.answer.return_value

    @staticmethod
    async def test_regular(mock_view_f: MagicMock, ):
        result = await view.Shared.internal_error(self=mock_view_f, )
        mock_view_f.bot.send_message.acow(
            chat_id=mock_view_f.id,
            text=texts.INTERNAL_ERROR,
            reply_markup=ReplyKeyboardRemove()
        )
        assert result == mock_view_f.bot.send_message.return_value


async def test_say_ok(mock_view_f: MagicMock, ):
    result = await view.Shared.say_ok(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        text=texts.Words.OK,
        chat_id=mock_view_f.id,
    )
    assert result == mock_view_f.bot.send_message.return_value


class TestAddCloseBtn:
    """test_add_close_btn"""

    @staticmethod
    @pytest_mark.parametrize(argnames='message_ids_to_close', argvalues=(1, 2, 3), )
    async def test_add_close_btn(
            mock_view_f: MagicMock,
            message_ids_to_close: int,
            message_s: Message,
    ):
        """Any of type: Message, MessageId, int"""
        match message_ids_to_close:
            case 1:
                message_ids_to_close = (1, 1,)
            case 2:
                message_ids_to_close = (MessageId(message_id=1, ), MessageId(message_id=1, ),)
            case 3:
                message_ids_to_close = (message_s, message_s,)
        keyboard = tg_IKM.from_button(button=tg_IKB(text='foo', callback_data='bar', ), )
        await view.Shared.add_close_btn(
            self=mock_view_f,
            message_ids_to_close=message_ids_to_close,
            keyboard=keyboard,
        )
        mock_view_f.bot.edit_message_reply_markup.acow(
            chat_id=mock_view_f.id,
            message_id=1,
            reply_markup=view.Keyboards.add_btn(
                keyboard=keyboard,
                btn=view.Keyboards.get_close_btn(message_ids_to_close=(1, 1,), )  # Accepted any type
            ),
        )


class TestProfileBase:
    @staticmethod
    @pytest_fixture(scope='function', )
    def profile(mock_bot: MagicMock, user_s: IUser, ):
        result = view.ProfileBase(bot=mock_bot, data_source=user_s, id=user_s.id, )
        result.data.photos = ['foo', 'bar']
        result.TranslationsMap = {
            # Simplified to use value as translation
            result.Goal: {item: str(item.value) for item in view.ProfileBase.Goal},
            result.Gender: {item: str(item.value) for item in view.ProfileBase.Gender},
        }
        yield result

    @staticmethod
    def test_translate_goal(profile: IProfileBase, ):
        """Simplified to use value as translation"""
        for current_goal in list(view.ProfileBase.Goal):
            profile.data.goal = current_goal
            result = view.ProfileBase.translate_goal(self=profile, )
            assert result == profile.TranslationsMap[view.ProfileBase.Goal][current_goal]

    @staticmethod
    def test_translate_gender(profile: IProfileBase, ):
        """Simplified to use value as translation"""
        for current_gender in list(view.ProfileBase.Gender):
            profile.data.gender = current_gender
            result = view.ProfileBase.translate_gender(self=profile, )
            assert result == profile.TranslationsMap[view.ProfileBase.Gender][current_gender]

    @staticmethod
    def test_get_data(profile: IProfileBase, ):
        result = view.ProfileBase.get_payload(self=profile, )
        assert result == view.ProfileBase.Payload(
            text=profile.get_profile_text(),
            photos=profile.data.photos,
        )

    @staticmethod
    def test_translate_text(profile: IProfileBase, ):
        result = view.ProfileBase.translate_text(self=profile, )
        nickname_link = f"<a href='tg://user?id={profile.id}'>{profile.data.fullname}</a>"
        assert result == {
            texts.Profile.NAME: nickname_link,
            texts.Profile.GOAL: profile.translate_goal(),
            texts.Profile.GENDER: profile.translate_gender(),
            texts.Profile.AGE: profile.data.age,
            texts.Profile.LOCATION: profile.translate_location(),
            texts.Profile.ABOUT: profile.data.comment,
        }
        assert None not in result.values()

    @staticmethod
    def test_get_profile_text(profile: IProfileBase, ):
        result = view.ProfileBase.get_profile_text(self=profile, )
        nickname_link = f"<a href='tg://user?id={profile.id}'>{profile.data.fullname}</a>"
        assert result == (
            f"<b>{texts.Profile.NAME}</b> - <code><i>{nickname_link}</i></code>.\n"
            f"<b>{texts.Profile.GOAL}</b> - <code><i>{profile.translate_goal()}</i></code>.\n"
            f"<b>{texts.Profile.GENDER}</b> - <code><i>{profile.translate_gender()}</i></code>.\n"
            f"<b>{texts.Profile.AGE}</b> - <code><i>{profile.data.age}</i></code>.\n"
            f"<b>{texts.Profile.LOCATION}</b> - <code><i>{profile.translate_location()}</i></code>.\n"
            f"<b>{texts.Profile.ABOUT}</b> - <code><i>{profile.data.comment}</i></code>."
        )

    @staticmethod
    def test_prepare_photos(profile: IProfileBase, ):
        result = view.ProfileBase.prepare_photos_to_send(self=profile, caption='bar', )
        assert result[0].caption == 'bar'
        assert result == [
            InputMediaPhoto(media='foo', parse_mode=ParseMode.HTML),
            InputMediaPhoto(media='bar', parse_mode=ParseMode.HTML),
        ]

    @staticmethod
    async def test_send(profile: IProfileBase, ):
        with (
            patch_object(target=profile, attribute='get_payload', ) as mock_get_payload,
            patch_object(target=profile, attribute='prepare_photos_to_send', ) as mock_prepare_photos_to_send,
        ):
            mock_get_payload.return_value.photos = [typing_Any, typing_Any, ]
            await view.ProfileBase.send(self=profile, )
        mock_get_payload.acow()
        mock_prepare_photos_to_send.acow(caption=mock_get_payload.return_value.text, )
        profile.bot.send_media_group.acow(
            chat_id=profile.id,
            media=mock_prepare_photos_to_send.return_value,
            parse_mode=ParseMode.HTML,
        )
        profile.bot.send_message.acow(
            chat_id=profile.id,
            text=mock_get_payload.return_value.text,
            parse_mode=ParseMode.HTML,
        )


class TestKeyboards:
    @staticmethod
    def test_get_close_btn(mock_view_f: MagicMock, ):
        result = view.Keyboards.get_close_btn(message_ids_to_close=[1, MessageId(message_id=2, ), ])
        assert result == tg_IKB(
            text=texts.Words.HIDE,
            callback_data=f'{view.HIDE_S} 1 2'
        )

    @staticmethod
    def test_add_btn(mock_view_f: MagicMock, ikm: tg_IKM, ):
        """Test keyboard, not the send method"""
        btn = tg_IKB(text='foo', callback_data='bar')
        result = view.Keyboards.add_btn(keyboard=ikm, btn=btn, )
        assert result == tg_IKM((*ikm.inline_keyboard, (btn,),), )
