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
from typing import TYPE_CHECKING
from abc import ABC
from re import Match as re_Match

from telegram import ReplyKeyboardMarkup as tg_RKM, InlineKeyboardMarkup as tg_IKM, InlineKeyboardButton as tg_IKB

from rubik_core.shared.structures import Goal, Gender

from app.tg.ptb.custom import ChoseKeyboardFabric

from . import model
from .constants import Cbks
from .texts import Search as SearchTexts
from ..shared.view import SharedInit, Keyboards as SharedKeyboards, ProfileBase, IProfileBase

if TYPE_CHECKING:
    from telegram import Message, ChatFullInfo

    from .model import IMatchStats, IMatch, IMatcher
    from .forms import ITarget as ITargetForm
    from ..user.model import IUser
    from ..shared.view import ProfileText


class IProfile(IProfileBase, ABC, ):
    TranslationsMap: dict


class Profile(ProfileBase, IProfile, ):
    TranslationsMap = {
        Goal: {
            Goal.CHAT: SearchTexts.Profile.IT_WANNA_CHAT,
            Goal.DATE: SearchTexts.Profile.IT_WANNA_DATE,
            Goal.BOTH: SearchTexts.Profile.IT_WANNA_CHAT_AND_DATE,
        },
        Gender: {
            Gender.MALE: SearchTexts.Profile.MALE,
            Gender.FEMALE: SearchTexts.Profile.FEMALE,
        },
    }

    def translate_text(self, ) -> ProfileText:
        """Convert user attributes to human-readable views"""
        text = {
            SearchTexts.Profile.NAME: f"<a href='tg://user?id={self.id}'>{self.data.fullname}</a>",
            SearchTexts.Profile.GOAL: self.translate_goal(),
            SearchTexts.Profile.GENDER: self.translate_gender(),
            SearchTexts.Profile.AGE: self.data.age,
            SearchTexts.Profile.LOCATION: self.translate_location(),
            SearchTexts.Profile.ABOUT: self.data.comment,
        }
        return {k: v for k, v in text.items() if v is not None}


class Match(SharedInit, ):
    Profile = Profile

    class Warn(SharedInit, ):

        async def incorrect_target_goal(self, ) -> Message:
            return await self.bot.send_message(chat_id=self.id, text=SearchTexts.INCORRECT_TARGET_GOAL, )

        async def incorrect_target_gender(self, ) -> Message:
            return await self.bot.send_message(chat_id=self.id, text=SearchTexts.INCORRECT_TARGET_GENDER, )

        async def incorrect_target_age(self, ) -> Message:
            return await self.bot.send_message(chat_id=self.id, text=SearchTexts.INCORRECT_TARGET_AGE, )

        async def incorrect_show_option(self, ) -> Message:
            return await self.bot.send_message(chat_id=self.id, text=SearchTexts.INCORRECT_SHOW_OPTION, )

        async def incorrect_show_more_option(self, ) -> Message:
            return await self.bot.send_message(
                chat_id=self.id,
                text=SearchTexts.INCORRECT_SHOW_MORE_OPTION,
                reply_markup=Keyboards.show_one_more_match,
            )

    def __init__(self, user: IUser, ):
        super().__init__(user=user, )
        self.warn = self.Warn(user=user, )

    async def say_search_hello(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=SearchTexts.STEP_0,
            reply_markup=Keyboards.go,
        )

    async def ask_votes_channel_sources(self, sources: dict[int, bool], ) -> Message:
        """Ask which channels where user has set vote user votes take into account for searching"""
        return await self.bot.send_message(
            chat_id=self.id,
            text=SearchTexts.ASK_VOTES_SOURCES,  # TODO add chat usernames links
            reply_markup=Keyboards.AskVotesChannelSources(
                channels={
                    (await self.bot.get_chat(chat_id=channel_id)): is_chosen
                    for channel_id, is_chosen in sources.items()
                },
                ikm=True,
            ).ikm
        )

    async def update_chosen_channels_keyboard(
            self,
            cbk_data: str,
            message: Message,
    ) -> None:
        await self.bot.edit_message_reply_markup(
            chat_id=self.id,
            message_id=message.message_id,
            reply_markup=tg_IKM(
                inline_keyboard=Keyboards.AskVotesChannelSources.update_keyboard(
                    keyboard=message.reply_markup,
                    btn_cbk_data=cbk_data,
                )
            ),
        )

    async def no_votes(self, ) -> Message:
        return await self.bot.send_message(chat_id=self.id, text=SearchTexts.NO_VOTES, )

    async def no_sources(self, reply_to_message_id: int, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=SearchTexts.NO_SOURCES,
            reply_to_message_id=reply_to_message_id,
        )

    async def no_covotes(self, ) -> Message:
        return await self.bot.send_message(chat_id=self.id, text=SearchTexts.NO_COVOTES, )

    async def ask_target_goal(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=SearchTexts.STEP_1,
            reply_markup=Keyboards.ask_target_goal,
        )

    async def ask_target_gender(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=SearchTexts.STEP_2,
            reply_markup=Keyboards.ask_target_gender
        )

    async def ask_target_age(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=SearchTexts.STEP_3,
            reply_markup=Keyboards.ask_target_age
        )

    async def show_target_checkboxes(self, target: ITargetForm, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=SearchTexts.NEW_FILTERS_SUGGESTIONS,
            reply_markup=Keyboards.Checkboxes.build(target=target, ),
        )

    async def ask_confirm(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=f'{SearchTexts.FOR_READY.format(READY=SearchTexts.READY_KEYWORD)}\n',
            reply_markup=Keyboards.ask_user_confirm,
        )

    async def no_matches_with_filters(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=SearchTexts.Result.NO_MATCHES_WITH_FILTERS,
        )

    async def ask_which_matches_show(self, matches: model.Matcher.Matches, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=SearchTexts.Result.FOUND_MATCHES_COUNT.format(FOUND_MATCHES_COUNT=matches.count_all, ),
            reply_markup=Keyboards.ask_which_matches_show(
                num_all_matches=matches.count_all,
                num_new_matches=matches.count_new,
            ), )

    async def show_match(self, match: IMatch, ) -> None:
        """Different keyboard with match profile"""
        # TODO no use class methods
        profile = self.Profile(bot=self.bot, data_source=match.user, id=match.user.id, )
        await self.bot.send_message(
            chat_id=self.id,
            text=SearchTexts.Result.HERE_MATCH.format(
                SHARED_INTERESTS_PERCENTAGE=match.stats.common_posts_perc,
                SHARED_INTERESTS_COUNT=match.stats.common_posts_count,
            ),
            reply_markup=Keyboards.show_one_more_match,
        )
        await profile.send(show_to_id=self.id, )

    @staticmethod
    async def update_target_checkboxes(message: Message, target: ITargetForm, ) -> Message | bool:
        """Update message with target checkboxes"""
        return await message.edit_reply_markup(reply_markup=Keyboards.Checkboxes.build(target=target, ), )

    async def no_more_matches(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=SearchTexts.Result.NO_MORE_MATCHES,
            reply_markup=Keyboards.remove(),
        )

    async def say_search_goodbye(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=f'{SearchTexts.COMPLETED_KEYWORD} {SearchTexts.GOODBYE_KEYWORD}',
            reply_markup=Keyboards.remove(),
        )

    '''Show statistic'''

    async def say_statistic_hello(self, ) -> Message:
        return await self.bot.send_message(chat_id=self.id, text=SearchTexts.STATISTIC_HELLO, )

    async def show_statistic(
            self,
            match_stats: IMatchStats,
            id: int | None = None,
    ) -> tuple[Message, Message]:
        id = id or self.id
        with_tg_name = match_stats.user.ptb.name
        message_1 = await self.bot.send_message(
            chat_id=id,
            text=f'{SearchTexts.HERE_STATISTICS_WITH} {with_tg_name} (id {match_stats.with_user_id}):',
        )
        statistic_text = (
            f'{SearchTexts.Profile.TOTAL_LIKES_SET} {match_stats.opposite_pos_votes_count}: '
            f'{SearchTexts.FROM} {match_stats.pos_votes_count}.\n'
            f'{SearchTexts.Profile.TOTAL_DISLIKES_SET} {match_stats.opposite_neg_votes_count}: '
            f'{SearchTexts.FROM} {match_stats.neg_votes_count}.\n'
            f'{SearchTexts.Profile.TOTAL_UNMARKED_POSTS} {match_stats.opposite_zero_votes_count}: '
            f'{SearchTexts.FROM} {match_stats.zero_votes_count}.\n'
            f'{SearchTexts.Profile.SHARED_LIKES_PERCENTAGE}: {match_stats.common_pos_votes_perc}%\n'
            f'{SearchTexts.Profile.SHARED_DISLIKES_PERCENTAGE}: {match_stats.common_neg_votes_perc}%\n'
            f'{SearchTexts.Profile.SHARED_UNMARKED_POSTS_PERCENTAGE}: {match_stats.common_zero_votes_perc}%\n'
        )
        message_2 = await self.bot.send_photo(
            chat_id=id,
            photo=match_stats.get_pie_chart_result(),
            caption=statistic_text,
            reply_markup=tg_IKM.from_button(
                button=SharedKeyboards.get_show_profile_btn(user_id=match_stats.user.id, ), )
        )
        return message_1, message_2


class Keyboards:
    remove = SharedKeyboards.remove
    go = SharedKeyboards.go

    ask_target_goal = tg_RKM(
        keyboard=[
            [SearchTexts.Buttons.I_WANNA_CHAT, SearchTexts.Buttons.I_WANNA_DATE],
            [SearchTexts.Buttons.I_WANNA_CHAT_AND_DATE],
            [SearchTexts.CANCEL_KEYWORD],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    ask_target_gender = tg_RKM(
        keyboard=[
            [SearchTexts.Buttons.MALE, SearchTexts.Buttons.FEMALE],
            [SearchTexts.Buttons.ANY_GENDER],
            [SearchTexts.CANCEL_KEYWORD],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    ask_target_age = tg_RKM(
        keyboard=[
            [SearchTexts.Buttons.ANY_AGE], [SearchTexts.CANCEL_KEYWORD]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    show_one_more_match = tg_RKM(
        keyboard=[[SearchTexts.Buttons.SHOW_MORE], [SearchTexts.COMPLETE_KEYWORD]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    @staticmethod
    def ask_which_matches_show(num_all_matches: int = 0, num_new_matches: int = 0, ):
        return tg_RKM(
            keyboard=[
                [f'{SearchTexts.Buttons.SHOW_ALL} ({num_all_matches})'],
                [f'{SearchTexts.Buttons.SHOW_NEW} ({num_new_matches})'],
                [SearchTexts.CANCEL_KEYWORD, ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    apply_filters = ask_user_confirm = tg_RKM(
        keyboard=[
            [SearchTexts.FINISH_KEYWORD],
            [SearchTexts.CANCEL_KEYWORD],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    class AskVotesChannelSources:
        """Not a fabric, produces concrete instance"""

        CBK_PREFIX = Cbks.CHOOSE_CHANNELS
        PATTERN = Cbks.CHOOSE_CHANNELS_R
        IKM = tg_IKM

        Keyboard = ChoseKeyboardFabric(
            all_btn_text=SearchTexts.Buttons.ALL_CHANNELS,
            unchecked_symbol='',
            cbk_prefix=CBK_PREFIX,
            pattern=PATTERN,
            btns_in_row=1,
        )

        def __init__(self, channels: dict[ChatFullInfo, bool], ikm: bool = False, ):
            """
            Channels, groups, supergroups and bots has title, private chats - username (optional)
            Warn: If is another bot - will be problem (multiple btns with the same text)
            """
            buttons = []
            for channel, is_chosen in channels.items():
                buttons.append(
                    dict(
                        text=channel.title or SearchTexts.Buttons.LIKES_FROM_BOT,
                        cbk_key=channel.id,
                        is_chosen=is_chosen,
                    )
                )
            self.inline_keyboard = self.Keyboard.build(items=buttons, )
            self.ikm = None
            if ikm:
                self.ikm = self.IKM(inline_keyboard=self.inline_keyboard, )

        @classmethod
        def extract_cbk_data(cls, match: re_Match, ):
            str_channel_id, is_chosen = cls.Keyboard.extract_cbk_data(cbk_data=match, )
            return int(str_channel_id), is_chosen

        @classmethod
        def update_keyboard(cls, keyboard: tg_IKM, btn_cbk_data: str, ):
            return cls.Keyboard.update_keyboard(keyboard=keyboard, btn_cbk_data=btn_cbk_data, )

    class Checkboxes:
        CHECKED_EMOJI_CHECKBOX = '☑'
        UNCHECKED_EMOJI_CHECKBOX = '🔲'

        @classmethod
        def checkboxes_emojis_map(cls, checkboxes: IMatcher.Filters.Checkboxes, ) -> dict[str, str]:
            return {
                key: cls.CHECKED_EMOJI_CHECKBOX if value else cls.UNCHECKED_EMOJI_CHECKBOX
                for key, value in checkboxes.items()
            }

        @classmethod
        def build(cls, target: ITargetForm, ) -> tg_IKM:
            """
            "callback_data" without flag cuz current incoming value just will be swapped
            """
            checkboxes_emojis = cls.checkboxes_emojis_map(  # Separate method for easiest tests
                checkboxes=target.filters.checkboxes,
            )

            btn_2 = tg_IKB(
                text=f"{checkboxes_emojis['age']} {SearchTexts.Checkboxes.AGE_SPECIFIED}",
                callback_data=f"{Cbks.CHECKBOX} age",
            )
            btn_3 = tg_IKB(
                text=f"{checkboxes_emojis['country']} {SearchTexts.Checkboxes.COUNTRY_SPECIFIED}",
                callback_data=f"{Cbks.CHECKBOX} country",
            )
            btn_4 = tg_IKB(
                text=f"{checkboxes_emojis['city']} {SearchTexts.Checkboxes.CITY_SPECIFIED}",
                callback_data=f"{Cbks.CHECKBOX} city",
            )
            btn_5 = tg_IKB(
                text=f"{checkboxes_emojis['photo']} {SearchTexts.Checkboxes.PHOTO_SPECIFIED}",
                callback_data=f"{Cbks.CHECKBOX} photo",
            )
            return tg_IKM([[btn_2, btn_3], [btn_4, btn_5]])
