"""This module may be completely separate from the app i.e. become another bot for UGC (user generated content)"""

from __future__ import annotations

from logging import getLogger
from dataclasses import dataclass
from typing import TYPE_CHECKING
from enum import Enum, auto
from re import compile as re_compile, IGNORECASE

from telegram.constants import ChatType, ChatMemberStatus, UpdateType, ParseMode
from telegram.error import TelegramError
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestChat,
    ReplyKeyboardRemove,
    KeyboardButton,
    ChatMemberAdministrator,
    ChatShared as TgChatShared,
)
from telegram.ext import (
    ChatMemberHandler,
    MessageHandler,
    ApplicationHandlerStop,
    CommandHandler,
    CallbackQueryHandler,
    filters,
)

from rubik_core.db.manager import Postgres, Params as DbParams

from app.config import LOGS_PATH
from app.postconfig import setup_logger

from .entities.post.constants import PostsChannels
from .entities.post.model import ChannelPublicPost
from .entities.user.model import User as UserModel
from .entities.post.view import Posts as PostsView
from .custom import accept_user

from .structures import IKeyboard

if TYPE_CHECKING:
    from telegram import Update, Chat, ChatFullInfo, Message, User as PtbUser
    from telegram.ext import ExtBot
    from custom_ptb.callback_context import CallbackContext as CallbackContext
    from app.tg.ptb.entities.post.model import IChannelPublicPost

logger = setup_logger(logger=getLogger(__name__), filename=f'{LOGS_PATH}/{__name__.split(".")[-1]}.log')


class Model:

    db = Postgres
    Status = ChannelPublicPost.Status

    @dataclass
    class ChatStruct:
        source: int
        target: int
        source_type: str
        target_type: str
        source_privacy: bool
        target_privacy: bool

    @dataclass
    class SQLS:
        CREATE = (
            'INSERT INTO M2M_MANAGERS_CHATS '
            '(source, target, source_type, target_type, source_privacy, target_privacy) '
            'VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING'
        )

        READ_TARGET_BY_SOURCE = 'SELECT (target) FROM M2M_MANAGERS_CHATS WHERE source = %s'

    @classmethod
    def save(
            cls,
            source: Chat | ChatFullInfo,
            target: Chat | ChatFullInfo,
            db_params: DbParams,
    ) -> None:
        # https://t.me/pythontelegrambotgroup/769806
        # telegram.Chat.username should be present if and only if the chat is public
        source_privacy = True if source.username else False
        target_privacy = True if target.username else False
        cls.db.create(
            statement=cls.SQLS.CREATE,
            values=(source.id, target.id, str(source.type), str(target.type), source_privacy, target_privacy,),
            db_params=db_params,
        )

    @classmethod
    def read_target(cls, source: int, db_params: DbParams, ) -> int:
        """Read only the target"""
        # telegram.Chat.username should be present if and only if the chat is public
        # https://t.me/pythontelegrambotgroup/769806
        result = cls.db.read(
            statement=cls.SQLS.READ_TARGET_BY_SOURCE,
            values=(source,),
            db_params=db_params,
        )
        return result

    class PostMetaData(str, ):
        """Class cuz functionality may grow"""

        Status = ChannelPublicPost.Status

        def __new__(cls, status: Status = Status.PENDING, ):
            """New cuz passed string can't be modified in init in case of (str) inheritance"""
            # Return just str_data also ok
            return super().__new__(cls, f"Post status: <b>{status.name.capitalize()}</b>\n\n")


class SharedViewKeyboards:
    class RequestChat:
        @classmethod
        def build(cls, source_row: bool = True, target_row: bool = True, ) -> ReplyKeyboardMarkup:
            keyboard = []
            if source_row:  # If not selected yet
                keyboard.append(
                    (  # Row 1
                        KeyboardButton(
                            text='Откуда постить (ваши чаты)',
                            request_chat=KeyboardButtonRequestChat(request_id=1, chat_is_channel=False, ),
                        ),
                        KeyboardButton(
                            text='Откуда постить (ваши каналы)',
                            request_chat=KeyboardButtonRequestChat(request_id=2, chat_is_channel=True, ),
                        ),
                    )
                )
            if target_row:  # If not selected yet
                keyboard.append(
                    (  # Row 2
                        KeyboardButton(
                            text='Куда постить (ваши чаты)',
                            request_chat=KeyboardButtonRequestChat(request_id=~11, chat_is_channel=False, ),
                        ),
                        KeyboardButton(
                            text='Куда постить (ваши каналы)',
                            request_chat=KeyboardButtonRequestChat(request_id=~12, chat_is_channel=True, ),
                        ),)
                )
            keyboard = ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True,
                one_time_keyboard=True,
                selective=True,
                # force_reply=True,  # ?
            )
            return keyboard

    class Control(IKeyboard, ):
        """Class to manage the keyboard"""

        class BtnStruct(Enum, ):
            PUBLISH = auto()
            UNPUBLISH = auto()
            DELETE = auto()

        CBK_S = 'store_channel_post'  # Prefix for trigger
        # first \d+ - post_id, [01] - 0 or 1 (is status was already added)
        PUBLISH_R = re_compile(fr'^{CBK_S} {BtnStruct.PUBLISH.value} \d+$', )
        UNPUBLISH_R = re_compile(fr'^{CBK_S} {BtnStruct.UNPUBLISH.value} \d+$', )
        DELETE_R = re_compile(fr'^{CBK_S} {BtnStruct.DELETE.value} \d+$', )

        @classmethod
        def build_callback(cls, action: BtnStruct, post_id: int, ) -> str:
            """Single prefix, different payload"""
            return f'{cls.CBK_S} {action.value} {post_id}'

        @classmethod
        def build_inline_button(cls, action: BtnStruct, post_id: int, ) -> InlineKeyboardButton:
            """Single prefix, different payload"""
            cbk_data = cls.build_callback(post_id=post_id, action=action, )
            btn = InlineKeyboardButton(text=action.name.capitalize(), callback_data=cbk_data, )
            return btn

        @classmethod
        def build(cls, post_id: int = 0, ) -> InlineKeyboardMarkup:  # post_id 0 if not published (saved) yet
            buttons = [
                [  # Row 1
                    cls.build_inline_button(action=cls.BtnStruct.UNPUBLISH, post_id=post_id, ),
                    cls.build_inline_button(action=cls.BtnStruct.PUBLISH, post_id=post_id, ),
                ],
                # Row 2
                [cls.build_inline_button(action=cls.BtnStruct.DELETE, post_id=post_id, )]
            ]
            return InlineKeyboardMarkup(inline_keyboard=buttons, )

        @classmethod
        def extract_cbk_data(cls, cbk_data: str, ) -> int:
            str_prefix, str_action, str_post_id, = cbk_data.split()
            return int(str_post_id)


class SharedView:

    Keyboards = SharedViewKeyboards

    @classmethod
    async def success_setup(cls, message: Message, ) -> None:
        await message.reply_text(text=f'Настройка успешно проведена!', )

    @classmethod
    async def no_access(cls, message: Message, ) -> None:
        await message.reply_text(text='У бота нет доступа к этому чату (сперва нужно добавить туда бота).', )

    @classmethod
    async def no_permission(cls, message: Message, ) -> None:
        await message.reply_text(text='У бота недостаточно прав для отправки сообщений.', )

    @classmethod
    async def update_status(cls, message: Message, post: IChannelPublicPost, ) -> None:
        try:
            if message.text:
                await message.edit_text(
                    text=Model.PostMetaData(status=post.status, ),
                    reply_markup=cls.Keyboards.Control.build(post_id=post.id, ),
                    parse_mode=ParseMode.HTML,
                )
            else:
                await message.edit_caption(
                    caption=Model.PostMetaData(status=post.status, ),
                    reply_markup=cls.Keyboards.Control.build(post_id=post.id, ),
                    parse_mode=ParseMode.HTML,
                )
        except TelegramError:  # If status the same
            pass  # Do nothing if status already have set and text not changed


class Shared:
    View = SharedView


class BotAddedToChatTrigger:
    """" For channels triggers only with max 2 members (admin and bot)"""

    class CustomChatMemberHandler(ChatMemberHandler, ):
        """ Trigger only channels """

        def check_update(self, update: Update, ) -> bool:
            check_result = super().check_update(update=update, )
            return (
                    check_result
                    and getattr(update.effective_chat, 'type', None, ) == ChatType.CHANNEL
                    and update.my_chat_member.new_chat_member.status == ChatMemberStatus.ADMINISTRATOR
            )

    class View:

        SharedKeyboards = SharedView.Keyboards

        @classmethod
        async def greeting(cls, chat: Chat, ) -> None:
            """Regular non channel greeting with keyboard"""
            await chat.send_message(
                text=(
                    f'Спасибо, что используете нашего бота!\n'
                    f'{HandleStoreTrigger.View.ADD_CHAT_INSTRUCTION.format(BOT_NAME=chat.get_bot().username)}'
                ),
                reply_markup=cls.SharedKeyboards.RequestChat.build(),
                parse_mode=ParseMode.HTML,
            )

        @classmethod
        async def personal_greeting(cls, channel_admin: PtbUser, ) -> None:
            """Greeting to personal messages on the bot chat (user admin subscribed)"""
            # noinspection PyTypeChecker
            await cls.greeting(chat=channel_admin, )  # Currently the same functionality, type mismatch warning is ok

    @classmethod
    async def callback(cls, update: Update, _: CallbackContext, ):
        """bot_added_to_channel_trigger"""
        try:
            if (
                    update.effective_chat.type == ChatType.CHANNEL
                    and await update.effective_chat.get_member_count() > 2  # TODO  # Creator and bot
            ):
                try:
                    # `effective_user` exists on chat subscribe action but not for all chats handlers
                    await cls.View.personal_greeting(channel_admin=update.effective_user, )
                except TelegramError:
                    logger.info(
                        f'Bot added to channel {update.effective_chat.link} '
                        f'but can not tell the reg chat instruction'
                    )
            else:
                await cls.View.greeting(chat=update.effective_chat, )
        except TelegramError:
            pass
        raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)

    @classmethod
    def create_handler(cls) -> CustomChatMemberHandler:
        result = cls.CustomChatMemberHandler(
            callback=BotAddedToChatTrigger.callback,
            chat_member_types=UpdateType.CHAT_MEMBER.value,  # Actual 0 will always False, others always True
        )
        return result


class RepliedWithTargetChat:

    class View:
        Shared = Shared.View
        success_setup = Shared.success_setup
        no_access = Shared.no_access
        no_permission = Shared.no_permission

        @classmethod
        async def bad_reply(cls, message: Message, ) -> None:
            await message.reply_text(
                text='Кажется ответ на сообщение не содержит имени чата или его айди',
                reply_markup=ReplyKeyboardRemove(),
            )

    @classmethod
    async def callback(cls, update: Update, context: CallbackContext, ):
        input_chat = await accept_user(app=context.application, message=update.effective_message, )
        if not input_chat:
            await cls.View.bad_reply(message=update.effective_message, )
            raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)
        try:
            target_chat = await context.bot.get_chat(chat_id=input_chat, )
        except TelegramError:
            await cls.View.no_access(message=update.effective_message, )
            raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)
        if target_chat.type != ChatType.CHANNEL and not target_chat.permissions.can_send_messages:
            await cls.View.no_permission(message=update.effective_message, )
            raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)
        Model.save(source=update.effective_chat, target=target_chat, db_params=context.db_params, )
        await cls.View.success_setup(message=update.effective_message, )
        raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)

    @classmethod
    def create_handler(cls) -> MessageHandler:
        result = MessageHandler(
            callback=cls.callback,
            filters=filters.REPLY & (
                    filters.CONTACT
                    | filters.TEXT
                    | filters.StatusUpdate.CHAT_SHARED
                    | filters.StatusUpdate.CHAT_SHARED
            ),
        )
        return result


class RegChat:
    """Note: not works for channels """

    COMMAND = 'reg_chat'
    START_COMMAND = 'start'  # Actually command will like `/start=reg_chat`
    CMD_R = re_compile(COMMAND, IGNORECASE, )

    class View:
        SharedKeyboards = Shared.View.Keyboards

        @classmethod
        async def ask_source_and_target(cls, message: Message, ) -> None:
            await message.reply_text(
                text='Выберите откуда и куда постить.',
                reply_markup=cls.SharedKeyboards.RequestChat.build(),
            )

    @classmethod
    async def callback(cls, update: Update, _: CallbackContext, ):
        """ Note: Chats can be requested in private chats only """
        await cls.View.ask_source_and_target(message=update.effective_message, )
        raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)

    @classmethod
    def create_handler(cls) -> CommandHandler:
        """
        If command used outside the bot (via url) - it's mandatory will start from `start` text
        and actual command is just args like `/start=reg_chat`.
        The filter required to pass the actual start command
        """
        result = CommandHandler(
            callback=cls.callback,
            command=(cls.COMMAND, cls.START_COMMAND,),
            filters=filters.Regex(pattern=cls.CMD_R, )
        )
        return result


class ChatShared:

    @dataclass
    class ChatForm:
        source: ChatFullInfo | None = None
        target: ChatFullInfo | None = None

    class View:
        Shared = Shared.View
        success_setup = Shared.success_setup
        no_access = Shared.no_access
        no_permission = Shared.no_permission

        @classmethod
        async def chat_success_added(cls, message: Message, is_source: bool, ) -> None:
            if is_source:
                chat_source = 'откуда'
                keyboard = cls.Shared.Keyboards.RequestChat.build(source_row=False, )  # If already added
            else:
                chat_source = 'куда'
                keyboard = cls.Shared.Keyboards.RequestChat.build(target_row=False, )  # If already added
            await message.reply_text(
                text=f'Чат {chat_source} отправлять успешно добавлен',
                reply_markup=keyboard,
            )

    @staticmethod
    async def check_permissions(chat: ChatFullInfo, bot_id: int, ) -> bool:
        if chat.type == ChatType.CHANNEL:
            member = await chat.get_member(user_id=bot_id, )
            return (
                    isinstance(member, ChatMemberAdministrator, ) and
                    member.can_manage_chat and
                    member.can_post_messages and
                    member.can_edit_messages and
                    member.can_delete_messages
            )
        else:  # For groups and other membership not contains permissions
            return (
                    chat.permissions.can_send_audios and
                    chat.permissions.can_send_documents and
                    chat.permissions.can_send_messages and
                    chat.permissions.can_send_other_messages and
                    chat.permissions.can_send_photos and
                    chat.permissions.can_send_polls and
                    chat.permissions.can_send_video_notes
            )

    @staticmethod
    def set_chat(chat_shared: TgChatShared, form: ChatForm, chat: ChatFullInfo, ) -> None:
        if chat_shared.request_id > 0:
            form.source = chat
        else:
            form.target = chat

    @classmethod
    async def callback(cls, update: Update, context: CallbackContext, ):
        form = context.user_data.tmp_data.chat_form = getattr(context.user_data.tmp_data, 'chat_form', cls.ChatForm())
        try:
            chat = await context.bot.get_chat(chat_id=update.effective_message.chat_shared.chat_id, )
        except TelegramError:
            await cls.View.no_access(message=update.effective_message, )
            raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)

        # For channels chat.permissions is None (cuz channel bot may be only admin), so we are checking bot membership
        if not await cls.check_permissions(chat=chat, bot_id=context.bot.id, ):
            await cls.View.no_permission(message=update.effective_message, )
            raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)

        cls.set_chat(chat_shared=update.effective_message.chat_shared, form=form, chat=chat, )

        if form.source and not form.target:
            await cls.View.chat_success_added(message=update.effective_message, is_source=True, )
        elif form.target and not form.source:
            await cls.View.chat_success_added(message=update.effective_message, is_source=False, )
        else:  # If both
            Model.save(source=form.source, target=form.target, db_params=context.db_params, )
            await cls.View.success_setup(message=update.effective_message, )
            del context.user_data.tmp_data.chat_form  # If filled both - clear for future usage
        raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)

    @classmethod
    def create_handler(cls) -> MessageHandler:
        result = MessageHandler(callback=cls.callback, filters=filters.StatusUpdate.CHAT_SHARED, )
        return result


class HandleStoreTrigger:
    """handle_store_trigger"""

    class View:
        Shared = Shared.View

        ADD_CHAT_INSTRUCTION = (
            f'Чтобы указать куда постить (канал или группу) - '
            f'<a href="https://t.me/{{BOT_NAME}}?start=reg_chat">нажмите сюда</a>\n'
            f'или вручную введите команду <b>/{RegChat.COMMAND}</b> в чате бота @{{BOT_NAME}}.'
        )

        ASK_TARGET_CHAT = f'Бот не знает куда постить :(\n{ADD_CHAT_INSTRUCTION}'

        @classmethod
        async def target_chat_not_registered(cls, message: Message, ) -> Message:
            if message.chat.type == ChatType.CHANNEL:
                keyboard = None
            else:
                keyboard = ReplyKeyboardMarkup.from_button(
                    button=RegChat.COMMAND,
                    resize_keyboard=True,
                    one_time_keyboard=True,
                    # force_reply=True,  # ?
                )
            return await message.reply_text(
                text=cls.ASK_TARGET_CHAT.format(BOT_NAME=message.get_bot().name),
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )

    @classmethod
    async def callback(cls, update: Update, context: CallbackContext, ):
        """Trigger. Subscribe on the store channel and resend to the control channel."""
        if not Model.read_target(source=update.effective_chat.id, db_params=context.db_params, ):
            await cls.View.target_chat_not_registered(message=update.effective_message, )
            raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)
        await update.effective_message.reply_text(
            text=Model.PostMetaData(),
            reply_to_message_id=update.effective_message.message_id,
            reply_markup=cls.View.Shared.Keyboards.Control.build(),
        )
        raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)

    @classmethod
    def create_handler(cls) -> MessageHandler:
        """Create subscribe_on_store_channel handler"""
        result = MessageHandler(
            callback=cls.callback,
            filters=(
                    filters.ChatType.CHANNEL & ~ (
                    filters.COMMAND |
                    filters.REPLY |
                    filters.Chat(chat_id=PostsChannels.STORE.value)
            )
            ),
        )
        return result


class SharedBtn:

    @classmethod
    async def check_is_registered(cls, update: Update, context: CallbackContext, ) -> int:
        target_chat_id = Model.read_target(source=update.effective_chat.id, db_params=context.db_params, )
        if not target_chat_id:
            await update.callback_query.answer(
                text=(
                    f'Бот не знает куда постить :(\n'
                    f'Чтобы указать куда постить (канал или группу) - введите команду /{RegChat.COMMAND}'
                ),
                show_alert=True,
            )
            raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)
        return target_chat_id


class HandlePublishBtn(SharedBtn, ):
    """handle_publish_btn"""

    class View:
        Shared = Shared.View
        get_keyboard = PostsView.ChannelPublicPost.get_keyboard

        @classmethod
        async def update_status(cls, message: Message, post: IChannelPublicPost, ) -> None:
            await cls.Shared.update_status(message=message, post=post, )

        @classmethod
        async def show_post(
                cls,
                bot: ExtBot,
                post: IChannelPublicPost,
                source_chat_id: int,
                target_chat_id: int,
        ) -> None:
            """show the same as send (send reviewed and deprecated) """
            sent_message = await bot.copy_message(
                chat_id=target_chat_id,
                from_chat_id=source_chat_id,
                message_id=post.message_id,
                reply_markup=cls.get_keyboard(post=post, ),
            )
            post.posts_channel_message_id = sent_message.message_id

    @classmethod
    async def callback(cls, update: Update, context: CallbackContext, ):
        """Publish the post in the post channel"""
        # raises ApplicationHandlerStop on False
        target_chat_id = await cls.check_is_registered(update=update, context=context, )
        post = ChannelPublicPost.create(
            # Channel source sender type secured by the filter
            # For channels bot can't access the user (sender), so user == channel
            author=UserModel(id=update.effective_chat.id, connection=context.connection, ),
            channel_id=target_chat_id,  # TODO check closely
            message_id=update.effective_message.message_id,
        )
        try:
            await cls.View.show_post(
                bot=context.bot,
                post=post,
                source_chat_id=update.effective_chat.id,
                target_chat_id=target_chat_id,
            )
            post.update_status(status=post.Status.RELEASED, )
            await cls.View.update_status(post=post, message=update.effective_message, )
        except TelegramError:
            pass  # TODO
        await update.callback_query.answer('Успех!')
        raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)

    @classmethod
    def create_handler(cls, ) -> CallbackQueryHandler:
        result = CallbackQueryHandler(
            callback=cls.callback,
            pattern=cls.View.Shared.Keyboards.Control.PUBLISH_R,
        )
        return result


class HandleUnpublishBtn(SharedBtn, ):
    """handle_unpublish_btn"""

    class View:
        ControlKeyboard = Shared.View.Keyboards.Control
        Shared = Shared.View

        @classmethod
        async def unpublish(cls, post: IChannelPublicPost, message: Message, target_chat_id: int, ) -> None:
            await cls.Shared.update_status(message=message, post=post, )
            await message.get_bot().delete_message(chat_id=target_chat_id, message_id=post.posts_channel_message_id, )

    @classmethod
    async def callback(cls, update: Update, context: CallbackContext, ):
        """Remove message from the post channel only"""
        target_chat_id = await cls.check_is_registered(update=update, context=context, )
        post = ChannelPublicPost.read(
            post_id=cls.View.ControlKeyboard.extract_cbk_data(cbk_data=update.callback_query.data, ),
            connection=context.connection,
        )
        post.unpublish(db_params=context.db_params, )
        try:
            await cls.View.unpublish(target_chat_id=target_chat_id, message=update.effective_message, post=post, )
        except TelegramError:
            pass  # TODO
        await update.callback_query.answer('Успех!')
        raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)

    @classmethod
    def create_handler(cls, ) -> CallbackQueryHandler:
        result = CallbackQueryHandler(
            callback=cls.callback,
            pattern=cls.View.Shared.Keyboards.Control.UNPUBLISH_R,
        )
        return result


class HandleDeleteBtn(SharedBtn, ):
    """handle_delete_btn"""

    class View:
        Shared = SharedView

        @classmethod
        async def remove_post(cls, message: Message, post: IChannelPublicPost, target_chat_id: int, ) -> None:
            await message.delete()  # Delete in source chat
            await message.get_bot().delete_message(chat_id=target_chat_id, message_id=post.posts_channel_message_id, )

    @classmethod
    async def callback(cls, update: Update, context: CallbackContext, ):
        """Delete post from the all 3 channels (2 if not published)"""
        target_chat_id = await cls.check_is_registered(update=update, context=context, )
        post = ChannelPublicPost.read(
            post_id=cls.View.Shared.Keyboards.Control.extract_cbk_data(cbk_data=update.callback_query.data, ),
            connection=context.connection,
        )
        post.delete(id=post.id, connection=context.connection, )  # Delete only from db
        try:
            # TODO check
            post.unpublish(db_params=context.db_params, )
            await cls.View.remove_post(message=update.effective_message, post=post, target_chat_id=target_chat_id, )
        except TelegramError:
            pass  # TODO
        await update.callback_query.answer('Успех!')
        raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)

    @classmethod
    def create_handler(cls, ) -> CallbackQueryHandler:
        result = CallbackQueryHandler(
            callback=cls.callback,
            pattern=cls.View.Shared.Keyboards.Control.DELETE_R,
        )
        return result


bot_added_to_channel_trigger_handler = BotAddedToChatTrigger.create_handler()
reg_chat_cmd_handler = RegChat.create_handler()
replied_with_target_chat_msg_handler = RepliedWithTargetChat.create_handler()
chat_shared_msg_handler = ChatShared.create_handler()
store_trigger_handler = HandleStoreTrigger.create_handler()
publish_btn_cbk_handler = HandlePublishBtn.create_handler()
unpublish_btn_cbk_handler = HandleUnpublishBtn.create_handler()
delete_btn_cbk_handler = HandleDeleteBtn.create_handler()

available_handlers = {
    -8: (
        bot_added_to_channel_trigger_handler,
        replied_with_target_chat_msg_handler,
        reg_chat_cmd_handler,
        chat_shared_msg_handler,
        store_trigger_handler,
        publish_btn_cbk_handler,
        unpublish_btn_cbk_handler,
        delete_btn_cbk_handler,
    ),

}
