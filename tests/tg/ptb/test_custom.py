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

from typing import TYPE_CHECKING, Callable, Iterable, Any as typing_Any
from re import compile as re_compile, match as re_match
from unittest.mock import create_autospec, ANY

import pytest
from telegram.constants import ChatType
from telegram import InlineKeyboardMarkup as tg_IKM, InlineKeyboardButton as tg_IKB, SharedUser

from app.tg.ptb.entities.match.constants import Cbks  # Just random cbk that have groups and matches by pattern
from app.tg.ptb import custom
from custom_ptb import callback_context

from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from telegram import UsersShared


@pytest.fixture(scope='module', )
def patched_db() -> MagicMock:
    with patch_object(target=callback_context, attribute='Postgres', ) as result:
        yield result


class TestUsernameToId:
    """test_username_to_id"""

    @staticmethod
    @pytest.fixture(scope='function', )
    def username_to_telethon_user():
        with patch_object(target=custom, attribute='username_to_telethon_user', ) as mock_telethon_username_to_user:
            yield mock_telethon_username_to_user

    @staticmethod
    @pytest.fixture(scope='function', )
    def patched_asyncio_wait_for():
        with patch_object(
                target=custom,
                attribute='asyncio_wait_for',

        ) as mock_asyncio_wait_for:
            yield mock_asyncio_wait_for

    @staticmethod
    async def test_success(
            mock_app: MagicMock,
            username_to_telethon_user: MagicMock,
            patched_asyncio_wait_for: MagicMock,
    ):
        result = await custom.username_to_id(app=mock_app, username='@foo', )
        username_to_telethon_user.acow(username='@foo', raise_=True, )
        patched_asyncio_wait_for.acow(fut=mock_app.create_task.return_value, timeout=5, )
        assert result == patched_asyncio_wait_for.return_value.id

    @staticmethod
    async def test_exception(
            mock_app: MagicMock,
            username_to_telethon_user: MagicMock,
            patched_asyncio_wait_for: MagicMock,
    ):
        patched_asyncio_wait_for.side_effect = custom.asyncio_TimeoutError
        await custom.username_to_id(app=mock_app, username='@foo', raise_=True, )
        username_to_telethon_user.acow(username='@foo', raise_=True, )
        patched_asyncio_wait_for.acow(fut=mock_app.create_task.return_value, timeout=5, )


async def test_get_chat(mock_bot: MagicMock, ):
    result = await custom.get_chat(chat_id=1, bot=mock_bot, )
    mock_bot.get_chat.acow(chat_id=1, read_timeout=None, )
    assert result == mock_bot.get_chat.return_value


class TestAcceptUser:
    """ test_accept_user """

    @staticmethod
    async def test_users_shared(mock_message: MagicMock, users_shared: UsersShared, ):
        mock_message.users_shared = users_shared
        result = await custom.accept_user(message=mock_message, app=typing_Any, )
        assert result == 2

    @staticmethod
    async def test_contact(mock_update: MagicMock, ):
        mock_update.message.users_shared = None  # Suppress other attrs check
        mock_update.message.contact.user_id = True  # Just for style
        result = await custom.accept_user(message=mock_update.message, app=typing_Any, )
        assert result == int(mock_update.message.from_user.id)

    @staticmethod
    async def test_username(mock_update: MagicMock, ):
        mock_update.message.users_shared = mock_update.message.contact = None  # Suppress other attrs check
        mock_update.message.text = '@foo'
        with patch_object(
                target=custom,
                attribute='username_to_id',

        ) as mock_username_to_id:
            result = await custom.accept_user(message=mock_update.message, app=typing_Any, )
        mock_username_to_id.acow(
            app=typing_Any,
            username=mock_update.message.text,
            raise_=False,
        )
        assert result == mock_username_to_id.return_value

    @staticmethod
    async def test_text_channel(mock_update: MagicMock, ):
        mock_update.message.users_shared = mock_update.message.contact = None  # Suppress other attrs check
        mock_update.message.chat.type = ChatType.CHANNEL
        mock_update.message.text = f'foo123bar'
        result = await custom.accept_user(message=mock_update.message, app=typing_Any, )
        assert result == -100123

    @staticmethod
    async def test_text(mock_update: MagicMock, ):
        mock_update.message.users_shared = mock_update.message.contact = None  # Suppress other attrs check
        mock_update.message.text = f'foo123bar'
        result = await custom.accept_user(message=mock_update.message, app=typing_Any, )
        assert result == 123

    @staticmethod
    async def test_none(mock_update: MagicMock, ):
        mock_update.message.text = mock_update.message.users_shared = mock_update.message.contact = None
        result = await custom.accept_user(message=mock_update.message, app=typing_Any, )
        assert result is None

    @staticmethod
    async def test_check(mock_update: MagicMock, ):
        await custom.accept_user(message=mock_update.message, check=True, app=typing_Any, )
        mock_update.message.get_bot.return_value.get_chat.acow(chat_id=ANY, )


class TestRequestUser:
    """test_request_user"""

    @staticmethod
    async def test_delegate_to_accept_users_result_not_none(mock_message: MagicMock, ):
        mock_message.users_shared = None
        with patch_object(target=custom, attribute='accept_user', ) as mock_accept_user:
            result = await custom.request_user(app=typing_Any, message=mock_message, )
        mock_accept_user.acow(app=typing_Any, message=mock_message, check=False, )
        mock_message.get_bot.return_value.get_chat.acow(
            chat_id=mock_accept_user.return_value,
        )
        assert result == SharedUser(
            user_id=mock_message.get_bot.return_value.get_chat.return_value.id,
            username=mock_message.get_bot.return_value.get_chat.return_value.username,
            first_name=mock_message.get_bot.return_value.get_chat.return_value.first_name,
            last_name=mock_message.get_bot.return_value.get_chat.return_value.last_name,
        )

    @staticmethod
    async def test_delegate_to_accept_users_result_none(mock_message: MagicMock, ):
        mock_message.users_shared = None
        with patch_object(
                target=custom,
                attribute='accept_user',

                return_value=None,
        ) as mock_accept_user:
            result = await custom.request_user(app=typing_Any, message=mock_message, )
        mock_accept_user.acow(app=typing_Any, message=mock_message, check=False, )
        assert result is None


class TestExtractSharedUserName:
    """test_extract_shared_user_name"""

    @staticmethod
    def test_username(mock_shared_user: MagicMock, ):
        mock_shared_user.username = 'username'
        result = custom.extract_shared_user_name(shared_user=mock_shared_user)
        assert result == f'@{mock_shared_user.username}'

    @staticmethod
    def test_first_and_last_name(mock_shared_user: MagicMock, ):
        mock_shared_user.last_name = mock_shared_user.first_name = 'name'
        result = custom.extract_shared_user_name(shared_user=mock_shared_user)
        assert result == f'{mock_shared_user.first_name} {mock_shared_user.last_name}'

    @staticmethod
    def test_id(mock_shared_user: MagicMock, ):
        """Multiple return variants via `or` condition, nothing to assert"""
        mock_shared_user.last_name = None
        custom.extract_shared_user_name(shared_user=mock_shared_user)


class TestCustomInlineKeyboardMarkup:
    test_cls = custom.CustomInlineKeyboardMarkup

    def test_to_list(self, ikm):
        expected = [
            [ikm.inline_keyboard[0][0], ikm.inline_keyboard[0][1], ],
            [ikm.inline_keyboard[1][0], ikm.inline_keyboard[1][1], ],
        ]
        assert self.test_cls.to_list(inline_keyboard=ikm.inline_keyboard, ) == expected

    def test_find_btn_by_cbk(self, ikm: tg_IKM, ):
        """ikm.inline_keyboard[0][0], 0, 0 - found btn, row and column indexes"""
        keyboard = ikm.inline_keyboard
        assert self.test_cls.find_btn_by_cbk(inline_keyboard=keyboard, cbk='00') == (ikm.inline_keyboard[0][0], 0, 0,)
        assert self.test_cls.find_btn_by_cbk(inline_keyboard=keyboard, cbk='01') == (ikm.inline_keyboard[0][1], 0, 1,)
        assert self.test_cls.find_btn_by_cbk(inline_keyboard=keyboard, cbk='10') == (ikm.inline_keyboard[1][0], 1, 0,)
        assert self.test_cls.find_btn_by_cbk(inline_keyboard=keyboard, cbk='11') == (ikm.inline_keyboard[1][1], 1, 1,)
        assert self.test_cls.find_btn_by_cbk(inline_keyboard=keyboard, cbk='foo') is None  # Not found

    def test_get_keyboard_buttons(self, ikm: tg_IKM, ):
        """ikm.inline_keyboard[0][0], 0, 0 - found btn, row and column indexes"""
        expected = [
            ikm.inline_keyboard[0][0],
            ikm.inline_keyboard[0][1],
            ikm.inline_keyboard[1][0],
            ikm.inline_keyboard[1][1],
        ]
        assert self.test_cls.get_keyboard_buttons(inline_keyboard=ikm.inline_keyboard, ) == expected

    class TestSplit:
        """test_split"""
        test_cls = custom.CustomInlineKeyboardMarkup

        def test_inline_keyboard_param(self, ikm: tg_IKM, ):
            """ikm.inline_keyboard[0][0], 0, 0 - found btn, row and column indexes"""
            expected = [
                [ikm.inline_keyboard[0][0], ],
                [ikm.inline_keyboard[0][1], ],
                [ikm.inline_keyboard[1][0], ],
                [ikm.inline_keyboard[1][1], ],
            ]
            result = self.test_cls.split(inline_keyboard=ikm.inline_keyboard, btns_in_row=1, )
            assert result == expected

        class TestBtnsParam:
            """test_btns_param"""

            markup = custom.CustomInlineKeyboardMarkup
            test_cls = markup

            def test_equal_buttons_in_row(self, ikm: tg_IKM, ):
                """ikm.inline_keyboard[0][0], 0, 0 - found btn, row and column indexes"""
                buttons = [
                    ikm.inline_keyboard[0][0],
                    ikm.inline_keyboard[0][1],
                    ikm.inline_keyboard[1][0],
                    ikm.inline_keyboard[1][1],
                ]
                expected = [
                    [ikm.inline_keyboard[0][0], ikm.inline_keyboard[0][1], ],
                    [ikm.inline_keyboard[1][0], ikm.inline_keyboard[1][1], ],
                ]
                result = self.test_cls.split(buttons=buttons, btns_in_row=2, )
                assert result == expected

            def test_not_equal_buttons_in_row(self, ikm: tg_IKM, ):
                buttons = [
                    ikm.inline_keyboard[0][0],
                    ikm.inline_keyboard[0][1],
                    ikm.inline_keyboard[1][0],
                    ikm.inline_keyboard[1][1],
                ]
                expected = [
                    [ikm.inline_keyboard[0][0], ikm.inline_keyboard[0][1], ikm.inline_keyboard[1][0], ],
                    [ikm.inline_keyboard[1][1], ],
                ]
                result = self.test_cls.split(buttons=buttons, btns_in_row=3, )
                assert result == expected

            def test_not_enough_buttons_in_row(self, ikm: tg_IKM, ):
                buttons = [
                    ikm.inline_keyboard[0][0],
                    ikm.inline_keyboard[0][1],
                    ikm.inline_keyboard[1][0],
                    ikm.inline_keyboard[1][1],
                ]
                expected = [buttons]
                result = self.test_cls.split(buttons=buttons, btns_in_row=len(buttons) + 1, )
                assert result == expected


class TestChooseKeyboardFabric:
    @staticmethod
    @pytest.fixture(scope="class")
    def keyboard():
        return custom.ChoseKeyboardFabric(
            cbk_prefix=Cbks.CHOOSE_CHANNELS,
            pattern=re_compile(pattern=Cbks.CHOOSE_CHANNELS_R, ),
            all_btn_text='all items',
            checked_symbol='[.]',
            unchecked_symbol='[]',
            btns_in_row=2,
        )

    @staticmethod
    @pytest.fixture(scope="function")
    def mock_keyboard(keyboard: custom.ChoseKeyboardFabric, ) -> MagicMock:
        yield create_autospec(spec=keyboard, )

    @staticmethod
    @pytest.fixture
    def get_inline_keyboard(
            keyboard: custom.ChoseKeyboardFabric,
    ) -> Callable[[Iterable[bool,]], list[list[tg_IKB]]]:
        def inner(choices: Iterable[bool], ) -> list[list[tg_IKB]]:
            choices = iter(choices)
            return [
                [keyboard.build_button(text='btn1', cbk_key='123', is_chosen=next(choices), ), ],
                [
                    keyboard.build_button(text='btn2', cbk_key='456', is_chosen=next(choices), ),
                    keyboard.build_button(text='btn3', cbk_key='789', is_chosen=next(choices), ),

                ],
                [keyboard.build_button(text='btn4', cbk_key='012', is_chosen=next(choices), ), ],
            ]

        yield inner

    @staticmethod
    @pytest.mark.parametrize(argnames='flag', argvalues=(True, False,), )
    def test_build_callback(keyboard: custom.ChoseKeyboardFabric, flag: bool):
        expected = f'{keyboard.cbk_prefix} 1 {int(flag)}'
        result = keyboard.build_callback(cbk_key='1', is_chosen=flag, )
        assert result == expected

    @staticmethod
    @pytest.mark.parametrize(argnames='flag', argvalues=(True, False,), )
    def test_extract_cbk_data(keyboard: custom.ChoseKeyboardFabric, flag: bool, ):
        result = keyboard.extract_cbk_data(
            cbk_data=re_match(
                pattern=keyboard.pattern,
                string=f'{keyboard.cbk_prefix} foo bar egg 123 {int(flag)}'
            ),
        )
        assert result == ('foo bar egg 123', not int(flag))

    @staticmethod
    @pytest.mark.parametrize(argnames=('flag', 'symbol',), argvalues=((True, '[.]'), (False, '[]',),), )
    def test_build_button(keyboard: custom.ChoseKeyboardFabric, flag: bool, symbol: str):
        """Missed mini case when unchecked_symbol is None"""
        expected = tg_IKB(
            text=f'{symbol} foo',
            callback_data=f'{keyboard.cbk_prefix} 1 {int(flag)}',
        )
        result = keyboard.build_button(text='foo', cbk_key='1', is_chosen=flag, )
        assert result == expected

    @staticmethod
    @pytest.mark.parametrize(argnames=('flag', 'symbol',), argvalues=((True, '[.]'), (False, '[]',),), )
    def test_create_btn_check_all(keyboard: custom.ChoseKeyboardFabric, flag: bool, symbol: str):
        expected = tg_IKB(
            text=f'{keyboard.all_btn_text} {symbol}',
            callback_data=f'{keyboard.cbk_prefix} {keyboard.all_btn_key} {int(flag)}'
        )
        result = keyboard.create_btn_check_all(items=[{'is_chosen': flag}])
        assert result == expected

    class TestBuild:
        """test_build"""

        @staticmethod
        def test_all_selected(
                keyboard: custom.ChoseKeyboardFabric,
                get_inline_keyboard: Callable[[Iterable[bool,]], list[list[tg_IKB]]],
        ):
            expected = [
                # [1:] - to remove first row cuz such buttons order can't be repeated via build()
                *get_inline_keyboard(choices=[True, ] * 4, )[1:],
                [tg_IKB(
                    callback_data=f'{keyboard.cbk_prefix} {keyboard.all_btn_key} 1',
                    text=f'{keyboard.all_btn_text} {keyboard.checked_symbol}', ),
                ],
            ]
            result = keyboard.build(
                items=[
                    {'text': 'btn2', 'cbk_key': '456', 'is_chosen': True, },
                    {'text': 'btn3', 'cbk_key': '789', 'is_chosen': True, },
                    {'text': 'btn4', 'cbk_key': '012', 'is_chosen': True, },
                ],
                add_all_btn=True,
            )
            assert result == expected

        @staticmethod
        def test_not_all_selected(
                keyboard: custom.ChoseKeyboardFabric,
                get_inline_keyboard: Callable[[Iterable[bool,]], list[list[tg_IKB]]],
        ):
            expected = [
                # [1:] - to remove first row cuz such buttons order can't be repeated via build()
                *get_inline_keyboard(choices=[True, False, True, False, ], )[1:],
                [tg_IKB(
                    callback_data=f'{keyboard.cbk_prefix} {keyboard.all_btn_key} 0',
                    text=f'{keyboard.all_btn_text} {keyboard.unchecked_symbol}', ),
                ],
            ]
            result = keyboard.build(
                items=[
                    {'text': 'btn2', 'cbk_key': '456', 'is_chosen': False, },
                    {'text': 'btn3', 'cbk_key': '789', 'is_chosen': True, },
                    {'text': 'btn4', 'cbk_key': '012', 'is_chosen': False, },
                ],
                add_all_btn=True,
            )
            assert result == expected

    class TestUpdateAllBtn:
        """test_update_all_btn"""

        @staticmethod
        @pytest.mark.parametrize(argnames='flag', argvalues=(True, False,))
        def test_all_btn_checked(
                keyboard: custom.ChoseKeyboardFabric,
                get_inline_keyboard: Callable[[Iterable[bool,]], list[list[tg_IKB]]],
                flag: bool,  # Just for reliability, flag shouldn't matter
        ):
            """ Test should set itself to true cuz all buttons are true"""
            inline_keyboard = get_inline_keyboard(choices=[True, ] * 4)
            inline_keyboard[0].insert(0, keyboard.get_all_btn(is_chosen=flag, ), )
            result = keyboard.update_all_btn(keyboard=inline_keyboard, )
            assert result[0][0].text == f'{keyboard.all_btn_text} {keyboard.checked_symbol}'
            assert result[0][0].callback_data == f'{keyboard.cbk_prefix} {keyboard.all_btn_key} 1'

        @staticmethod
        @pytest.mark.parametrize(argnames='flag', argvalues=(True, False,))
        def test_all_btn_unchecked(
                keyboard: custom.ChoseKeyboardFabric,
                get_inline_keyboard: Callable[[Iterable[bool,]], list[list[tg_IKB]]],
                flag: bool,  # Just for reliability, flag shouldn't matter
        ):
            """ Test should set itself to false cuz at least one button is false"""
            inline_keyboard = get_inline_keyboard(choices=[False, ] * 4)
            inline_keyboard[0].insert(0, keyboard.get_all_btn(is_chosen=flag, ), )
            result = keyboard.update_all_btn(keyboard=inline_keyboard, )
            assert result[0][0].text == f'{keyboard.all_btn_text} {keyboard.unchecked_symbol}'
            assert result[0][0].callback_data == f'{keyboard.cbk_prefix} {keyboard.all_btn_key} 0'

    @staticmethod
    @pytest.mark.parametrize(argnames=('btn_text', 'flag',), argvalues=(('!123', True), ('123!', False,)))
    def test_check_btn(mock_keyboard: MagicMock, btn_text: str, flag: bool, ):
        mock_keyboard.checked_symbol = '!'
        mock_keyboard.unchecked_symbol = '!'
        btn = tg_IKB(text=btn_text, callback_data=f'foo', )
        result = custom.ChoseKeyboardFabric.check_btn(self=mock_keyboard, btn=btn, flag=flag, )
        mock_keyboard.build_button.acow(
            text=btn.text,
            cbk_key=mock_keyboard.get_cbk_key.return_value,
            is_chosen=flag,
            checkbox_on_left=flag,
            replace_old_symbol=True,
        )
        assert result == mock_keyboard.build_button.return_value

    @staticmethod
    @pytest.mark.parametrize(argnames='flag', argvalues=(True, False,))
    def test_invert_btn(mock_keyboard: MagicMock, flag: bool, ):
        btn = tg_IKB(text='foo', callback_data=f'bar{int(not flag)}', )
        result = custom.ChoseKeyboardFabric.invert_btn(self=mock_keyboard, btn=btn)
        mock_keyboard.check_btn.acow(btn=btn, flag=flag, )
        assert result == mock_keyboard.check_btn.return_value

    @staticmethod
    def test_is_all_btn(keyboard: custom.ChoseKeyboardFabric, ):
        for cbk_data, expected in [
            (keyboard.get_all_btn().callback_data, True),
            (tg_IKB(text=f'foo', callback_data=f'foo 0 bar', ).callback_data, True),
            (tg_IKB(text=f'foo', callback_data=f'foo 1 bar', ).callback_data, False),
            (keyboard.build_callback(cbk_key='0', is_chosen=False, ), True),
            (keyboard.build_callback(cbk_key=f'foo', is_chosen=False, ), False),
            (keyboard.build_callback(cbk_key='123', is_chosen=False, ), False),
        ]:
            result = keyboard.is_all_btn(cbk_data=cbk_data, )
            assert result == expected

    class TestUpdateKeyboard:
        """test_update_keyboard"""

        @staticmethod
        def test_all_btn_checked(
                keyboard: custom.ChoseKeyboardFabric,
                get_inline_keyboard: Callable[[Iterable[bool,]], list[list[tg_IKB]]],
        ):
            inline_keyboard = get_inline_keyboard(choices=[True, ] * 4)
            inline_keyboard.append([keyboard.get_all_btn(is_chosen=False, )])
            expected = get_inline_keyboard(choices=[True, ] * 4)
            expected.append([keyboard.get_all_btn(is_chosen=True, )])
            result = keyboard.update_keyboard(
                btn_cbk_data=inline_keyboard[-1][-1].callback_data,
                keyboard=tg_IKM(inline_keyboard=inline_keyboard),
            )
            assert result == expected

        @staticmethod
        def test_all_btn_unchecked(
                keyboard: custom.ChoseKeyboardFabric,
                get_inline_keyboard: Callable[[Iterable[bool,]], list[list[tg_IKB]]],
        ):
            inline_keyboard = get_inline_keyboard(choices=[False, ] * 4)
            inline_keyboard.append([keyboard.get_all_btn(is_chosen=True, )])
            expected = get_inline_keyboard(choices=[False, ] * 4)
            expected.append([keyboard.get_all_btn(is_chosen=False, )])
            result = keyboard.update_keyboard(
                btn_cbk_data=inline_keyboard[-1][-1].callback_data,
                keyboard=tg_IKM(inline_keyboard=inline_keyboard),
            )
            assert result == expected

        @staticmethod
        def test_not_all_btn(
                keyboard: custom.ChoseKeyboardFabric,
                get_inline_keyboard: Callable[[Iterable[bool,]], list[list[tg_IKB]]],
        ):
            inline_keyboard = get_inline_keyboard(choices=[False, ] * 4)
            inline_keyboard.append([keyboard.get_all_btn()])
            expected = get_inline_keyboard(choices=[True, False, False, False, ])
            expected.append([keyboard.get_all_btn()])
            result = keyboard.update_keyboard(
                btn_cbk_data=inline_keyboard[0][0].callback_data,
                keyboard=tg_IKM(inline_keyboard=inline_keyboard),
            )
            assert result == expected


class TestCallbackContext:
    @staticmethod
    def test_from_update(
            mock_update: MagicMock,
            mock_context: MagicMock,
            mock_app: MagicMock,
            patched_db: MagicMock,
    ):
        with patch_object(
                target=callback_context.CallbackContext,
                attribute='from_update',

                return_value=mock_context,
        ) as mock_from_update:
            mock_context.view = mock_context.user = None
            result = callback_context.CallbackContext.from_update(update=mock_update, application=mock_app, )
            mock_from_update.acow(update=mock_update, application=mock_app, )
            assert result == mock_context
