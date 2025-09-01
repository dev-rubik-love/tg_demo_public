from __future__ import annotations

from typing import TYPE_CHECKING, Any as typing_Any

import pytest
from telegram.constants import ChatType, ParseMode
from telegram import (
    InlineKeyboardMarkup as Ikm,
    ReplyKeyboardMarkup as Rkm,
    InlineKeyboardButton as Ikb,
    KeyboardButton,
    KeyboardButtonRequestChat,
    ReplyKeyboardRemove,
    Chat,
)
from telegram.ext import ApplicationHandlerStop

from app.tg.ptb import store_manager

from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from telegram import ChatFullInfo, User as PtbUser
    from app.tg.ptb.entities.post.model import IChannelPublicPost


@pytest.fixture(scope='function', )
def patched_model():
    with patch_object(target=store_manager, attribute='Model', ) as result:
        yield result


@pytest.fixture(scope='function', )  # Will patch for entire scope (module) were was called
def patched_post_cls(mock_channel_public_post: MagicMock, ) -> MagicMock:
    with patch_object(target=store_manager, attribute='ChannelPublicPost', ) as MockChannelPublicPost:
        MockChannelPublicPost.read.return_value = mock_channel_public_post  # Failed to autospec correctly
        MockChannelPublicPost.create.return_value = mock_channel_public_post  # Failed to autospec correctly
        yield MockChannelPublicPost


class TestModel:

    @staticmethod
    @pytest.fixture(scope='function', )
    def patched_db() -> MagicMock:
        with patch_object(target=store_manager.Model, attribute='db', ) as mock_db:
            yield mock_db

    class TestSave:
        """ test_save """

        @staticmethod
        def test_chat(chat_s: Chat, patched_db: MagicMock, ):
            store_manager.Model.save(source=chat_s, target=chat_s, db_params=typing_Any, )
            patched_db.create.acow(
                statement=store_manager.Model.SQLS.CREATE,
                values=(chat_s.id, chat_s.id, str(chat_s.type), str(chat_s.type), True, True,),
                db_params=typing_Any,
            )

        @staticmethod
        def test_chat_full_info(chat_full_info_s: ChatFullInfo, patched_db: MagicMock, ):
            source = target = chat_full_info_s
            store_manager.Model.save(source=source, target=target, db_params=typing_Any, )
            patched_db.create.acow(
                statement=store_manager.Model.SQLS.CREATE,
                values=(source.id, target.id, str(source.type), str(target.type), False, False,),
                db_params=typing_Any,
            )

    @staticmethod
    def test_read_target(patched_db: MagicMock, ):
        result = store_manager.Model.read_target(source=1, db_params=typing_Any, )
        patched_db.read.acow(
            statement=store_manager.Model.SQLS.READ_TARGET_BY_SOURCE,
            values=(1,),
            db_params=typing_Any,
        )
        assert result == patched_db.read.return_value

    class TestPostMetaData:
        @staticmethod
        def test_new():
            result = store_manager.Model.PostMetaData()
            expected_pending_status = store_manager.Model.PostMetaData.Status.PENDING.name.capitalize()
            assert result == f"Post status: <b>{expected_pending_status}</b>\n\n"


class TestSharedViewKeyboardRequestChat:
    """TestRequestChat"""

    @staticmethod
    def test_build():
        result = store_manager.SharedViewKeyboards.RequestChat.build()
        expected_result = Rkm(
            keyboard=(
                (
                    KeyboardButton(
                        text='Откуда постить (ваши чаты)',
                        request_chat=KeyboardButtonRequestChat(request_id=1, chat_is_channel=False, ),
                    ),
                    KeyboardButton(
                        text='Откуда постить (ваши каналы)',
                        request_chat=KeyboardButtonRequestChat(request_id=2, chat_is_channel=True, ),
                    ),
                ),
                (
                    KeyboardButton(
                        text='Куда постить (ваши чаты)',
                        request_chat=KeyboardButtonRequestChat(request_id=~11, chat_is_channel=False, ),
                    ),
                    KeyboardButton(
                        text='Куда постить (ваши каналы)',
                        request_chat=KeyboardButtonRequestChat(request_id=~12, chat_is_channel=True, ),
                    ),),
            ),
            resize_keyboard=True,
            one_time_keyboard=True,

        )
        assert result == expected_result


class TestSharedViewKeyboardControl:
    """TestControl"""

    @staticmethod
    @pytest.mark.parametrize(argnames='action', argvalues=store_manager.SharedViewKeyboards.Control.BtnStruct, )
    def test_build_callback(action: store_manager.SharedViewKeyboards.Control.BtnStruct, ):
        result = store_manager.SharedViewKeyboards.Control.build_callback(
            post_id=1,
            action=action,
        )
        assert result == f'{store_manager.SharedViewKeyboards.Control.CBK_S} {action.value} 1'

    @staticmethod
    @pytest.mark.parametrize(argnames='action', argvalues=store_manager.SharedViewKeyboards.Control.BtnStruct, )
    def test_build_inline_button(action: store_manager.SharedViewKeyboards.Control.BtnStruct, ):
        result = store_manager.SharedViewKeyboards.Control.build_inline_button(post_id=1, action=action, )
        assert result == Ikb(
            text=action.name.capitalize(),
            callback_data=store_manager.SharedViewKeyboards.Control.build_callback(post_id=1, action=action, ),
        )

    @staticmethod
    def test_build():
        result = store_manager.SharedViewKeyboards.Control.build(post_id=1, )
        expected_result = [
            [  # Row 1
                store_manager.SharedViewKeyboards.Control.build_inline_button(
                    action=store_manager.SharedViewKeyboards.Control.BtnStruct.UNPUBLISH,
                    post_id=1,
                ),
                store_manager.SharedViewKeyboards.Control.build_inline_button(
                    action=store_manager.SharedViewKeyboards.Control.BtnStruct.PUBLISH,
                    post_id=1,
                ),
            ],
            # Row 2
            [store_manager.SharedViewKeyboards.Control.build_inline_button(
                action=store_manager.SharedViewKeyboards.Control.BtnStruct.DELETE,
                post_id=1,
            )]
        ]
        assert result == Ikm(inline_keyboard=expected_result, )

    @staticmethod
    def test_extract_cbk_data():
        result = store_manager.SharedViewKeyboards.Control.extract_cbk_data(cbk_data='1 1 1', )
        assert result == 1


class TestSharedView:
    @staticmethod
    async def test_success_setup(mock_message: MagicMock, ):
        await store_manager.SharedView.success_setup(message=mock_message, )
        mock_message.reply_text.acow(text=f'Настройка успешно проведена!', )

    @staticmethod
    async def test_no_access(mock_message: MagicMock, ):
        await store_manager.SharedView.no_access(message=mock_message, )
        mock_message.reply_text.acow(
            text='У бота нет доступа к этому чату (сперва нужно добавить туда бота).',
        )

    @staticmethod
    async def test_no_permission(mock_message: MagicMock, ):
        await store_manager.SharedView.no_permission(message=mock_message, )
        mock_message.reply_text.acow(text='У бота недостаточно прав для отправки сообщений.', )

    class TestUpdateStatus:
        """test_update_status"""

        @staticmethod
        async def test_caption_content(mock_message: MagicMock, channel_public_post_s: IChannelPublicPost, ):
            mock_message.text = None
            await store_manager.SharedView.update_status(message=mock_message, post=channel_public_post_s, )
            mock_message.edit_caption.acow(
                reply_markup=store_manager.SharedView.Keyboards.Control.build(post_id=1, ),
                caption=store_manager.Model.PostMetaData(status=channel_public_post_s.status, ),
                parse_mode=ParseMode.HTML,
            )

        @staticmethod
        async def test_text_content(mock_message: MagicMock, channel_public_post_s: IChannelPublicPost, ):
            mock_message.text = 'foo'
            await store_manager.SharedView.update_status(message=mock_message, post=channel_public_post_s, )
            mock_message.edit_text.acow(
                reply_markup=store_manager.SharedView.Keyboards.Control.build(post_id=1, ),
                text=store_manager.Model.PostMetaData(status=channel_public_post_s.status, ),
                parse_mode=ParseMode.HTML,
            )

        @staticmethod
        async def test_exception(mock_message: MagicMock, channel_public_post_s: IChannelPublicPost, ):
            mock_message.edit_text.side_effect = store_manager.TelegramError(message='', )
            await store_manager.SharedView.update_status(message=mock_message, post=channel_public_post_s, )


class TestBotAddedToChatTrigger:
    class TestView:
        class TestGreeting:
            """test_greeting"""

            @staticmethod
            async def test_greeting(mock_chat: MagicMock, ) -> None:
                add_chat_instruction_text = store_manager.HandleStoreTrigger.View.ADD_CHAT_INSTRUCTION
                await store_manager.BotAddedToChatTrigger.View.greeting(chat=mock_chat, )
                mock_chat.send_message.acow(
                    text=(
                        f'Спасибо, что используете нашего бота!\n'
                        f'{add_chat_instruction_text.format(BOT_NAME=mock_chat.get_bot().username)}'
                    ),
                    reply_markup=store_manager.BotAddedToChatTrigger.View.SharedKeyboards.RequestChat.build(),
                    parse_mode=ParseMode.HTML,
                )

            @staticmethod
            async def test_personal_greeting(ptb_user_s: PtbUser, ) -> None:
                with patch_object(
                        target=store_manager.BotAddedToChatTrigger.View,
                        attribute='greeting',
                ) as mock_greeting:
                    await store_manager.BotAddedToChatTrigger.View.personal_greeting(channel_admin=ptb_user_s, )
                mock_greeting.acow(chat=ptb_user_s, )

    class TestCallback:
        """test_callback"""

        @staticmethod
        async def test_success(mock_update: MagicMock, ):
            mock_update.effective_chat.get_member_count.return_value = 1
            with (
                pytest.raises(expected_exception=ApplicationHandlerStop, ),
                patch_object(
                    target=store_manager.BotAddedToChatTrigger.View,
                    attribute='greeting',
                ) as mock_greeting,
            ):
                await store_manager.BotAddedToChatTrigger.callback(update=mock_update, _=typing_Any, )
            mock_greeting.acow(chat=mock_update.effective_chat, )

        @staticmethod
        async def test_exception(mock_update: MagicMock, ):
            mock_update.effective_chat.get_member_count.return_value = 1
            with (
                pytest.raises(expected_exception=ApplicationHandlerStop, ),
                patch_object(
                    target=store_manager.BotAddedToChatTrigger.View,
                    attribute='greeting',
                    side_effect=store_manager.TelegramError(''),
                ) as mock_greeting,
            ):
                await store_manager.BotAddedToChatTrigger.callback(update=mock_update, _=typing_Any, )
            mock_greeting.acow(chat=mock_update.effective_chat, )


class TestRepliedWithTargetChat:
    class TestView:
        @staticmethod
        async def test_bad_reply(mock_message: MagicMock, ):
            await store_manager.RepliedWithTargetChat.View.bad_reply(message=mock_message, )
            mock_message.reply_text.acow(
                text='Кажется ответ на сообщение не содержит имени чата или его айди',
                reply_markup=ReplyKeyboardRemove(),
            )

    class TestCallback:
        """test_callback"""

        @staticmethod
        @pytest.fixture(scope='function', )
        def patched_accept_user():
            with patch_object(target=store_manager, attribute='accept_user', ) as mock_accept_user:
                yield mock_accept_user

        class TestEdgeCases:
            """test_accept_user"""

            @staticmethod
            async def test_accept_user_none_result(
                    mock_update: MagicMock,
                    mock_context: MagicMock,
                    patched_accept_user: MagicMock,
            ):
                patched_accept_user.return_value = None
                with (
                    pytest.raises(expected_exception=ApplicationHandlerStop, ),
                    patch_object(  # View patching failed to spec correctly
                        target=store_manager.RepliedWithTargetChat.View,
                        attribute='bad_reply',
                    ) as mock_bad_reply,
                ):
                    await store_manager.RepliedWithTargetChat.callback(update=mock_update, context=mock_context, )
                mock_bad_reply.acow(message=mock_update.effective_message, )

            @staticmethod
            async def test_accept_user_no_access(
                    mock_update: MagicMock,
                    mock_context: MagicMock,
                    patched_accept_user: MagicMock,
            ):
                mock_context.bot.get_chat.side_effect = store_manager.TelegramError(message='')
                with (
                    pytest.raises(expected_exception=ApplicationHandlerStop, ),
                    patch_object(  # View patching failed to spec correctly
                        target=store_manager.RepliedWithTargetChat.View,
                        attribute='no_access',
                    ) as mock_no_access,
                ):
                    await store_manager.RepliedWithTargetChat.callback(update=mock_update, context=mock_context, )
                mock_context.bot.get_chat.acow(chat_id=patched_accept_user.return_value, )
                mock_no_access.acow(message=mock_update.effective_message, )

            @staticmethod
            async def test_accept_user_no_permission(
                    mock_update: MagicMock,
                    mock_context: MagicMock,
                    patched_accept_user: MagicMock,
            ):
                mock_context.bot.get_chat.return_value.permissions.can_send_messages = False
                with (
                    pytest.raises(expected_exception=ApplicationHandlerStop, ),
                    patch_object(  # View patching failed to spec correctly
                        target=store_manager.RepliedWithTargetChat.View,
                        attribute='no_permission',
                    ) as mock_no_permission,
                ):
                    await store_manager.RepliedWithTargetChat.callback(update=mock_update, context=mock_context, )
                mock_context.bot.get_chat.acow(chat_id=patched_accept_user.return_value, )
                mock_no_permission.acow(message=mock_update.effective_message, )

        @staticmethod
        async def test_success(
                mock_update: MagicMock,
                mock_context: MagicMock,
                patched_accept_user: MagicMock,
                patched_model: MagicMock,
        ):
            with (
                pytest.raises(expected_exception=ApplicationHandlerStop, ),
                patch_object(  # View patching failed to spec correctly
                    target=store_manager.RepliedWithTargetChat.View,
                    attribute='success_setup',

                ) as mock_success_setup,
            ):
                await store_manager.RepliedWithTargetChat.callback(update=mock_update, context=mock_context, )
            patched_accept_user.acow(
                app=mock_context.application,
                message=mock_update.effective_message,
            )
            patched_model.save.acow(
                source=mock_update.effective_chat,
                target=mock_context.bot.get_chat.return_value,
                db_params=store_manager.DbParams(connection=mock_context.connection, ),
            )
            mock_success_setup.acow(message=mock_update.effective_message, )


class TestRegChat:
    class TestView:
        @staticmethod
        async def test_ask_source_and_target(mock_message: MagicMock, ):
            await store_manager.RegChat.View.ask_source_and_target(message=mock_message, )
            mock_message.reply_text.acow(
                text='Выберите откуда и куда постить.',
                reply_markup=store_manager.RegChat.View.SharedKeyboards.RequestChat.build(),
            )

    @staticmethod
    async def test_callback(mock_update: MagicMock, ):
        with (
            pytest.raises(expected_exception=ApplicationHandlerStop, ),
            patch_object(  # View patching failed to spec correctly
                target=store_manager.RegChat.View,
                attribute='ask_source_and_target',
            ) as mock_ask_source_and_target,
        ):
            await store_manager.RegChat.callback(update=mock_update, _=typing_Any, )
        mock_ask_source_and_target.acow(message=mock_update.effective_message, )


class TestChatShared:

    class TestView:
        test_cls = store_manager.ChatShared.View

        @pytest.mark.parametrize(
            argnames=('flag', 'chat_source', 'keyboard_build_param',),
            argvalues=((True, 'откуда', 'source_row',), (False, 'куда', 'target_row',),),
        )
        async def test_chat_success_added(
                self,
                mock_message: MagicMock,
                flag: bool,
                chat_source: str,
                keyboard_build_param: str,
        ):
            await self.test_cls.chat_success_added(message=mock_message, is_source=flag, )
            mock_message.reply_text.acow(
                text=f'Чат {chat_source} отправлять успешно добавлен',
                reply_markup=self.test_cls.Shared.Keyboards.RequestChat.build(**{keyboard_build_param: False, }, ),
            )

    class TestCheckPermissions:
        """ test_check_permissions """

        @staticmethod
        async def test_regular(mock_chat_full_info: MagicMock, ):
            """" Just run it """
            mock_chat_full_info.type = ChatType.GROUP  # Any not channel ok
            await store_manager.ChatShared.check_permissions(chat=mock_chat_full_info, bot_id=1, )

        @staticmethod
        async def test_channel(mock_chat_full_info: MagicMock, ):
            """" Just run it """
            mock_chat_full_info.type = ChatType.CHANNEL
            await store_manager.ChatShared.check_permissions(chat=mock_chat_full_info, bot_id=1, )
            mock_chat_full_info.get_member.acow(user_id=1, )

    class TestCallback:
        """test_callback"""

        @staticmethod
        @pytest.mark.parametrize(argnames='chat_name', argvalues=('source', 'target',), )
        def test_set_chat(mock_message: MagicMock, mock_context: MagicMock, chat_name: str, ):
            mock_context.user_data.tmp_data.chat_form = store_manager.ChatShared.ChatForm()
            mock_message.chat_shared.request_id = int(chat_name == 'source', )
            store_manager.ChatShared.set_chat(
                chat_shared=mock_message.chat_shared,
                form=mock_context.user_data.tmp_data.chat_form,
                chat=typing_Any,
            )
            assert getattr(mock_context.user_data.tmp_data.chat_form, chat_name, ) == typing_Any

        @staticmethod
        async def test_success(
                mock_update: MagicMock,
                mock_context: MagicMock,
                patched_model: MagicMock,
                chat_full_info_s: ChatFullInfo,
        ):
            # tmp_data.chat_form will be cleared
            orig_chat_form = mock_context.user_data.tmp_data.chat_form = store_manager.ChatShared.ChatForm(
                source=chat_full_info_s,
                target=chat_full_info_s,
            )
            mock_update.effective_message.chat_shared.request_id = 1  # Any number
            with (
                pytest.raises(expected_exception=ApplicationHandlerStop, ),
                patch_object(target=store_manager.ChatShared.View, attribute='success_setup', ) as mock_success_setup,
            ):
                await store_manager.ChatShared.callback(update=mock_update, context=mock_context, )
            mock_context.bot.get_chat.acow(
                chat_id=mock_update.effective_message.chat_shared.chat_id,
            )
            patched_model.save.acow(
                source=orig_chat_form.source,
                target=orig_chat_form.target,
                db_params=store_manager.DbParams(connection=mock_context.connection, ),
            )
            mock_success_setup.acow(message=mock_update.effective_message, )
            assert not hasattr(mock_context.user_data.tmp_data, 'chat_form')

        @staticmethod
        async def test_no_access(mock_update: MagicMock, mock_context: MagicMock, ):
            mock_context.bot.get_chat.side_effect = store_manager.TelegramError(message='', )
            with (
                pytest.raises(expected_exception=ApplicationHandlerStop, ),
                patch_object(target=store_manager.ChatShared.View, attribute='no_access', ) as mock_no_access,
            ):
                await store_manager.ChatShared.callback(update=mock_update, context=mock_context, )
            mock_no_access.acow(message=mock_update.effective_message, )

        @staticmethod
        async def test_no_permissions(mock_update: MagicMock, mock_context: MagicMock, ):
            mock_context.bot.get_chat.return_value.get_member.return_value = None  # Sets permissions to False
            mock_context.bot.get_chat.return_value.permissions.can_send_audios = False  # Sets permissions to False
            with (
                pytest.raises(expected_exception=ApplicationHandlerStop, ),
                patch_object(target=store_manager.ChatShared.View, attribute='no_permission', ) as mock_no_permission,
            ):
                await store_manager.ChatShared.callback(update=mock_update, context=mock_context, )
            mock_no_permission.acow(message=mock_update.effective_message, )

        @staticmethod
        async def test_form_source(mock_update: MagicMock, mock_context: MagicMock, ):
            mock_update.effective_message.chat_shared.request_id = 1  # Any positive number to set target later
            mock_context.user_data.tmp_data.chat_form = store_manager.ChatShared.ChatForm(target=None, )
            with (
                pytest.raises(expected_exception=ApplicationHandlerStop, ),
                patch_object(
                    target=store_manager.ChatShared.View,
                    attribute='chat_success_added',
                ) as mock_chat_success_added,
            ):
                await store_manager.ChatShared.callback(update=mock_update, context=mock_context, )
            mock_chat_success_added.acow(message=mock_update.effective_message, is_source=True, )
            assert hasattr(mock_context.user_data.tmp_data, 'chat_form')  # Assert not deleted incidentally

        @staticmethod
        async def test_form_target(mock_update: MagicMock, mock_context: MagicMock, ):
            mock_context.user_data.tmp_data.chat_form = store_manager.ChatShared.ChatForm(source=None, )
            mock_update.effective_message.chat_shared.request_id = -1  # Any negative number to set target later
            with (
                pytest.raises(expected_exception=ApplicationHandlerStop, ),
                patch_object(
                    target=store_manager.ChatShared.View,
                    attribute='chat_success_added',
                ) as mock_chat_success_added,
            ):
                await store_manager.ChatShared.callback(update=mock_update, context=mock_context, )
            mock_chat_success_added.acow(message=mock_update.effective_message, is_source=False, )
            assert hasattr(mock_context.user_data.tmp_data, 'chat_form')  # Assert not deleted incidentally


class TestHandleStoreTrigger:
    class TestView:
        class TestTargetChatNotRegistered:
            """ test_target_chat_not_registered """

            @staticmethod
            async def test_regular(mock_message: MagicMock, ):
                result = await store_manager.HandleStoreTrigger.View.target_chat_not_registered(message=mock_message, )
                mock_message.reply_text.acow(
                    text=store_manager.HandleStoreTrigger.View.ASK_TARGET_CHAT.format(
                        BOT_NAME=mock_message.get_bot().name
                    ),
                    parse_mode=ParseMode.HTML,
                    reply_markup=store_manager.ReplyKeyboardMarkup.from_button(
                        button=store_manager.RegChat.COMMAND,
                        resize_keyboard=True,
                        one_time_keyboard=True,
                        # force_reply=True,  # ?
                    ),
                )
                assert result == mock_message.reply_text.return_value

            @staticmethod
            async def test_channel(mock_message: MagicMock, ):
                mock_message.chat.type = ChatType.CHANNEL
                result = await store_manager.HandleStoreTrigger.View.target_chat_not_registered(message=mock_message, )
                mock_message.reply_text.acow(
                    text=store_manager.HandleStoreTrigger.View.ASK_TARGET_CHAT.format(
                        BOT_NAME=mock_message.get_bot().name
                    ),
                    parse_mode=ParseMode.HTML,
                    reply_markup=None,
                )
                assert result == mock_message.reply_text.return_value

    class TestCallback:
        """test_callback"""

        @staticmethod
        async def test_registered(mock_update: MagicMock, mock_context: MagicMock, patched_model: MagicMock, ):
            with pytest.raises(expected_exception=ApplicationHandlerStop):
                await store_manager.HandleStoreTrigger.callback(update=mock_update, context=mock_context, )
            patched_model.read_target.acow(
                source=mock_update.effective_chat.id,
                db_params=mock_context.db_params,
            )
            mock_update.effective_message.reply_text.acow(
                text=store_manager.Model.PostMetaData(),
                reply_to_message_id=mock_update.effective_message.message_id,
                reply_markup=store_manager.HandleStoreTrigger.View.Shared.Keyboards.Control.build(),
            )

        @staticmethod
        async def test_not_registered(mock_update: MagicMock, mock_context: MagicMock, patched_model: MagicMock, ):
            patched_model.read_target.return_value = None
            with (
                pytest.raises(expected_exception=ApplicationHandlerStop),
                patch_object(target=store_manager.HandleStoreTrigger, attribute='View', ) as mock_view_cls,
            ):
                await store_manager.HandleStoreTrigger.callback(update=mock_update, context=mock_context, )
            patched_model.read_target.acow(
                source=mock_update.effective_chat.id,
                db_params=mock_context.db_params,
            )
            mock_view_cls.target_chat_not_registered.acow(message=mock_update.effective_message, )


class TestSharedBtn:

    class TestCheckIsRegistered:
        """test_check_is_registered"""

        @staticmethod
        async def test_common(mock_update: MagicMock, mock_context: MagicMock, patched_model: MagicMock, ):
            await store_manager.SharedBtn.check_is_registered(update=mock_update, context=mock_context, )
            patched_model.read_target.acow(
                source=mock_update.effective_chat.id,
                db_params=mock_context.db_params,
            )

        @staticmethod
        async def test_registered(mock_update: MagicMock, mock_context: MagicMock, patched_model: MagicMock, ):
            result = await store_manager.SharedBtn.check_is_registered(update=mock_update, context=mock_context, )
            assert result == patched_model.read_target.return_value

        @staticmethod
        async def test_not_registered(mock_update: MagicMock, mock_context: MagicMock, patched_model: MagicMock, ):
            patched_model.read_target.return_value = None
            with pytest.raises(ApplicationHandlerStop, ):
                await store_manager.SharedBtn.check_is_registered(update=mock_update, context=mock_context, )
            mock_update.callback_query.answer.acow(
                text=(
                    f'Бот не знает куда постить :(\n'
                    f'Чтобы указать куда постить (канал или группу) - введите команду /{store_manager.RegChat.COMMAND}'
                ),
                show_alert=True,
            )


@pytest.fixture(scope='function', )
def patched_check_is_registered(request, ):
    """
    The dynamic version of a simple logger patching implementation to adhere to DRY principles.
    Each test witch uses this fixture should have test_cls attributes in the target (test) function.
    """
    with patch_object(target=request.node.cls.test_cls, attribute='check_is_registered', ) as result:
        yield result


@pytest.fixture(scope='function', )
def patched_view(request, ):
    """
    The dynamic version of a simple logger patching implementation to adhere to DRY principles.
    Each test witch uses this fixture should have test_cls attributes in the target (test) function.
    """
    with patch_object(target=request.node.cls.test_cls, attribute='View', ) as result:
        yield result


class TestHandlePublishBtn:

    test_cls = store_manager.HandlePublishBtn

    class TestView:
        @staticmethod
        async def test_update_status(mock_message: MagicMock, channel_public_post_s: IChannelPublicPost, ):
            with patch_object(
                    target=store_manager.HandlePublishBtn.View.Shared,
                    attribute='update_status',
            ) as mock_update_status:
                await store_manager.HandlePublishBtn.View.update_status(
                    message=mock_message,
                    post=channel_public_post_s,
                )
            mock_update_status.acow(message=mock_message, post=channel_public_post_s, )

        @staticmethod
        async def test_show_post(mock_bot: MagicMock, channel_public_post_f: IChannelPublicPost, ):
            await store_manager.HandlePublishBtn.View.show_post(
                bot=mock_bot,
                post=channel_public_post_f,
                source_chat_id=1,
                target_chat_id=2,
            )
            mock_bot.copy_message.acow(
                chat_id=2,
                from_chat_id=1,
                message_id=channel_public_post_f.message_id,
                reply_markup=store_manager.HandlePublishBtn.View.get_keyboard(post=channel_public_post_f, ),
            )
            assert channel_public_post_f.posts_channel_message_id == mock_bot.copy_message.return_value.message_id

    async def test_callback(
            self,
            mock_update: MagicMock,
            mock_context: MagicMock,
            patched_model: MagicMock,
            patched_post_cls: MagicMock,
            patched_check_is_registered: MagicMock,
            patched_view: MagicMock,
    ):
        mock_post = patched_post_cls.create.return_value
        patched_view.update_status.side_effect = store_manager.TelegramError(message='', )  # just for coverage
        with (pytest.raises(expected_exception=ApplicationHandlerStop), ):
            await self.test_cls.callback(update=mock_update, context=mock_context, )
        patched_check_is_registered.acow(update=mock_update, context=mock_context, )
        patched_post_cls.create.acow(
            author=store_manager.UserModel(id=mock_update.effective_chat.id, connection=mock_context.connection, ),
            message_id=mock_update.effective_message.message_id,
            channel_id=patched_check_is_registered.return_value,
        )
        patched_view.show_post.acow(
            bot=mock_context.bot,
            post=mock_post,
            source_chat_id=mock_update.effective_chat.id,
            target_chat_id=patched_check_is_registered.return_value,
        )
        mock_post.update_status.acow(status=mock_post.Status.RELEASED, )
        patched_view.update_status.acow(message=mock_update.effective_message, post=mock_post, )
        mock_update.callback_query.answer.acow('Успех!')


class TestHandleUnpublishBtn:

    test_cls = store_manager.HandleUnpublishBtn

    class TestView:
        @staticmethod
        async def test_unpublish(mock_message: MagicMock, channel_public_post_s: IChannelPublicPost, ):
            with patch_object(
                    target=store_manager.HandleUnpublishBtn.View.Shared,
                    attribute='update_status',
            ) as mock_update_status:
                await store_manager.HandleUnpublishBtn.View.unpublish(
                    message=mock_message,
                    post=channel_public_post_s,
                    target_chat_id=1,
                )
            mock_update_status.acow(message=mock_message, post=channel_public_post_s, )
            mock_message.get_bot.return_value.delete_message.acow(
                chat_id=1,
                message_id=channel_public_post_s.posts_channel_message_id,
            )

    async def test_callback(
            self,
            mock_update: MagicMock,
            mock_context: MagicMock,
            patched_model: MagicMock,
            patched_post_cls: MagicMock,
            patched_check_is_registered: MagicMock,
            patched_view: MagicMock,
    ):
        mock_update.callback_query.data = '1 1 1'  # Any 3 values split by space
        post = patched_post_cls.read.return_value
        db_params = store_manager.DbParams(connection=mock_context.connection, )
        patched_view.unpublish.side_effect = store_manager.TelegramError(message='', )  # just for coverage
        with pytest.raises(expected_exception=ApplicationHandlerStop):
            await self.test_cls.callback(update=mock_update, context=mock_context, )
        patched_check_is_registered.acow(update=mock_update, context=mock_context, )
        patched_post_cls.read.acow(
            post_id=patched_view.ControlKeyboard.extract_cbk_data(cbk_data=mock_update.callback_query.data, ),
            connection=mock_context.connection,
        )
        post.unpublish.acow(db_params=db_params, )
        patched_view.unpublish.acow(
            target_chat_id=patched_check_is_registered.return_value,
            message=mock_update.effective_message,
            post=post,
        )
        mock_update.callback_query.answer.acow('Успех!')


class TestHandleDeleteBtn:

    test_cls = store_manager.HandleDeleteBtn

    class TestView:
        @staticmethod
        async def test_remove_post(mock_message: MagicMock, channel_public_post_s: IChannelPublicPost, ):
            await store_manager.HandleDeleteBtn.View.remove_post(
                message=mock_message,
                post=channel_public_post_s,
                target_chat_id=1,
            )
            mock_message.delete.acow()
            mock_message.get_bot.return_value.delete_message.acow(
                message_id=channel_public_post_s.posts_channel_message_id,
                chat_id=1,
            )

    async def test_callback(
            self,
            mock_update: MagicMock,
            mock_context: MagicMock,
            patched_model: MagicMock,
            patched_post_cls: MagicMock,
            patched_check_is_registered: MagicMock,
            patched_view: MagicMock,
    ):
        mock_update.callback_query.data = '1 1 1'  # Any 3 values split by space
        post = patched_post_cls.read.return_value
        patched_view.remove_post.side_effect = store_manager.TelegramError(message='', )  # just for coverage
        with pytest.raises(expected_exception=ApplicationHandlerStop):
            await self.test_cls.callback(update=mock_update, context=mock_context, )
        patched_check_is_registered.acow(update=mock_update, context=mock_context, )
        post.unpublish.acow(db_params=mock_context.db_params, )
        post.delete.acow(id=post.id, connection=mock_context.connection, )
        patched_view.remove_post.acow(
            message=mock_update.effective_message,
            post=post,
            target_chat_id=patched_check_is_registered.return_value,
        )
        mock_update.callback_query.answer.acow('Успех!')
