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
from unittest.mock import Mock

from pytest import fixture as pytest_fixture
from telegram import ChatFullInfo, InlineKeyboardMarkup, InlineKeyboardButton

from app.tg.ptb.entities.match import view
from app.tg.ptb.entities.match.texts import Search as Texts

from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from app.tg.ptb.entities.match.model import IMatch
    from app.tg.ptb.entities.user.model import IUser
    from app.tg.ptb.entities.match.forms import ITarget as ITargetForm
    from app.tg.ptb.entities.match.view import IProfile


class TestWarn:

    @staticmethod
    async def test_incorrect_target_goal(mock_view_f: MagicMock, ):
        result = await view.Match.Warn.incorrect_target_goal(self=mock_view_f.match.warn, )
        mock_view_f.match.warn.bot.send_message.acow(
            chat_id=mock_view_f.match.warn.id,
            text=Texts.INCORRECT_TARGET_GOAL,
        )
        assert result == mock_view_f.match.warn.bot.send_message.return_value

    @staticmethod
    async def test_incorrect_target_gender(mock_view_f: MagicMock, ):
        result = await view.Match.Warn.incorrect_target_gender(self=mock_view_f.match.warn, )
        mock_view_f.match.warn.bot.send_message.acow(
            chat_id=mock_view_f.match.warn.id,
            text=Texts.INCORRECT_TARGET_GENDER,
        )
        assert result == mock_view_f.match.warn.bot.send_message.return_value

    @staticmethod
    async def test_incorrect_target_age(mock_view_f: MagicMock, ):
        result = await view.Match.Warn.incorrect_target_age(self=mock_view_f.match.warn, )
        mock_view_f.match.warn.bot.send_message.acow(
            chat_id=mock_view_f.match.warn.id,
            text=Texts.INCORRECT_TARGET_AGE,
        )
        assert result == mock_view_f.match.warn.bot.send_message.return_value

    @staticmethod
    async def test_incorrect_show_option(mock_view_f: MagicMock, ):
        result = await view.Match.Warn.incorrect_show_option(self=mock_view_f.match.warn, )
        mock_view_f.match.warn.bot.send_message.acow(
            chat_id=mock_view_f.match.warn.id,
            text=Texts.INCORRECT_SHOW_OPTION,
        )
        assert result == mock_view_f.match.warn.bot.send_message.return_value

    @staticmethod
    async def test_incorrect_show_more_option(mock_view_f: MagicMock, ):
        result = await view.Match.Warn.incorrect_show_more_option(self=mock_view_f.match.warn, )
        mock_view_f.match.warn.bot.send_message.acow(
            chat_id=mock_view_f.match.warn.id,
            text=Texts.INCORRECT_SHOW_MORE_OPTION,
            reply_markup=view.Keyboards.show_one_more_match,
        )
        assert result == mock_view_f.match.warn.bot.send_message.return_value


async def test_no_votes(mock_view_f: MagicMock, ):
    result = await view.Match.no_votes(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.NO_VOTES,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_no_sources(mock_view_f: MagicMock, ):
    result = await view.Match.no_sources(self=mock_view_f.match, reply_to_message_id=1, )
    mock_view_f.match.bot.send_message.acow(
        chat_id=mock_view_f.match.id,
        text=Texts.NO_SOURCES,
        reply_to_message_id=1,
    )
    assert result == mock_view_f.match.bot.send_message.return_value


async def test_no_covotes(mock_view_f: MagicMock, ):
    result = await view.Match.no_covotes(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(chat_id=mock_view_f.id, text=Texts.NO_COVOTES, )
    assert result == mock_view_f.bot.send_message.return_value


async def test_no_matches_with_filters(mock_view_f: MagicMock, ):
    result = await view.Match.no_matches_with_filters(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(chat_id=mock_view_f.id, text=Texts.Result.NO_MATCHES_WITH_FILTERS, )
    assert result == mock_view_f.bot.send_message.return_value


async def test_say_search_hello(mock_view_f: MagicMock, ):
    result = await view.Match.say_search_hello(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.STEP_0,
        reply_markup=view.Keyboards.go
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_ask_votes_channel_sources(mock_view_f: MagicMock, ):
    with patch_object(
            target=view.Keyboards,
            attribute='AskVotesChannelSources',
            autospec=False,  # returned ikm attr exists only on instance
            spec_set=False,  # returned ikm attr exists only on instance
    ) as MockAskVotesChannelSources:
        result = await view.Match.ask_votes_channel_sources(self=mock_view_f, sources={123: True, })
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.ASK_VOTES_SOURCES,
        reply_markup=MockAskVotesChannelSources.return_value.ikm
    )
    MockAskVotesChannelSources.acow(
        channels={mock_view_f.bot.get_chat.return_value: True},
        ikm=True,
    )
    mock_view_f.bot.get_chat.acow(chat_id=123, )
    assert result == mock_view_f.bot.send_message.return_value


async def test_ask_target_goal(mock_view_f: MagicMock, ):
    result = await view.Match.ask_target_goal(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.STEP_1,
        reply_markup=view.Keyboards.ask_target_goal,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_ask_target_gender(mock_view_f: MagicMock, ):
    result = await view.Match.ask_target_gender(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.STEP_2,
        reply_markup=view.Keyboards.ask_target_gender,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_ask_target_age(mock_view_f: MagicMock, ):
    result = await view.Match.ask_target_age(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.STEP_3,
        reply_markup=view.Keyboards.ask_target_age,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_show_checkboxes(mock_view_f: MagicMock, target_s: ITargetForm, ):
    result = await view.Match.show_target_checkboxes(self=mock_view_f, target=target_s, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.NEW_FILTERS_SUGGESTIONS,
        reply_markup=view.Keyboards.Checkboxes.build(target=target_s, ),
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_ask_which_matches_show(mock_view_f: MagicMock, mock_matcher: MagicMock, ):
    result = await view.Match.ask_which_matches_show(self=mock_view_f, matches=mock_matcher.matches, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.Result.FOUND_MATCHES_COUNT.format(FOUND_MATCHES_COUNT=mock_matcher.matches.count_all),
        reply_markup=view.Keyboards.ask_which_matches_show(
            num_all_matches=mock_matcher.matches.count_all,
            num_new_matches=mock_matcher.matches.count_new,
        ),
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_here_match(mock_view_f: MagicMock, match_s: IMatch, ):
    await view.Match.show_match(self=mock_view_f.match, match=match_s, )
    mock_view_f.match.bot.send_message.acow(
        chat_id=mock_view_f.match.id,
        text=Texts.Result.HERE_MATCH.format(
            SHARED_INTERESTS_PERCENTAGE=match_s.stats.common_posts_perc,
            SHARED_INTERESTS_COUNT=match_s.stats.common_posts_count,
        ),
        reply_markup=view.Keyboards.show_one_more_match,
    )


async def test_no_more_matches(mock_view_f: MagicMock, ):
    result = await view.Match.no_more_matches(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.Result.NO_MORE_MATCHES,
        reply_markup=view.Keyboards.remove(),
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_say_search_goodbye(mock_view_f: MagicMock, ):
    result = await view.Match.say_search_goodbye(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=f'{Texts.COMPLETED_KEYWORD} {Texts.GOODBYE_KEYWORD}',
        reply_markup=view.Keyboards.remove(),
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_update_checkboxes(target_s: ITargetForm, mock_message: MagicMock, ):
    result = await view.Match.update_target_checkboxes(message=mock_message, target=target_s, )
    mock_message.edit_reply_markup.acow(
        reply_markup=view.Keyboards.Checkboxes.build(target=target_s, ),
    )
    assert result == mock_message.edit_reply_markup.return_value


async def test_ask_confirm(mock_view_f: MagicMock, ):
    result = await view.Match.ask_confirm(self=mock_view_f)
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=f'{Texts.FOR_READY.format(READY=Texts.READY_KEYWORD)}\n',
        reply_markup=view.Keyboards.ask_user_confirm,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_update_chosen_channels_keyboard(mock_view_f: MagicMock, mock_message: MagicMock, ):
    with (
        patch_object(
            target=view.Keyboards.AskVotesChannelSources,
            attribute='update_keyboard',
        ) as mock_update_keyboard,
        patch_object(target=view, attribute='tg_IKM', ) as mock_tg_IKM,
    ):
        await view.Match.update_chosen_channels_keyboard(
            self=mock_view_f.match,
            message=mock_message,
            cbk_data='foo',
        )
    mock_view_f.match.bot.edit_message_reply_markup.acow(
        chat_id=mock_view_f.match.id,
        message_id=mock_message.message_id,
        reply_markup=mock_tg_IKM.return_value,
    )
    mock_tg_IKM.acow(inline_keyboard=mock_update_keyboard.return_value, )
    mock_update_keyboard.acow(keyboard=mock_message.reply_markup, btn_cbk_data='foo', )


class TestAskVotesChannelSources:

    cls_to_test = view.Keyboards.AskVotesChannelSources

    def test_init(self, ):
        mock_chat_full_info = Mock(isntance=False, spec=ChatFullInfo, )
        with (
            patch_object(target=self.cls_to_test.Keyboard, attribute='build', ) as mock_build,
            patch_object(target=self.cls_to_test, attribute='IKM', ) as mock_ikm,
        ):
            instance = self.cls_to_test(channels={mock_chat_full_info: True}, ikm=True, )
        mock_build.acow(
            items=[dict(
                text=mock_chat_full_info.title,
                cbk_key=mock_chat_full_info.id,
                is_chosen=True,
            )],
        )
        assert instance.inline_keyboard == mock_build.return_value
        assert instance.ikm == mock_ikm.return_value

    def test_extract_cbk_data(self, ):
        """Test for just delegating and simple converting"""
        with patch_object(
                target=self.cls_to_test.Keyboard,
                attribute='extract_cbk_data',

                return_value=('1', True,),
        ) as mock_extract_cbk_data:
            result = self.cls_to_test.extract_cbk_data(match=typing_Any, )
        mock_extract_cbk_data.acow(cbk_data=typing_Any, )
        assert result == (1, True)

    def test_update_keyboard(self, ):
        """Test for just delegating"""

        with patch_object(
                target=self.cls_to_test.Keyboard,
                attribute='update_keyboard',
                return_value=('1', True,),
        ) as mock_update_keyboard:
            result = self.cls_to_test.update_keyboard(keyboard=typing_Any, btn_cbk_data='foo', )
        mock_update_keyboard.acow(keyboard=typing_Any, btn_cbk_data='foo', )
        assert result == mock_update_keyboard.return_value


class TestCheckboxes:

    cls_to_test = view.Keyboards.Checkboxes

    def test_convert_checkboxes_emojis(self, target_s: ITargetForm, ):
        actual = self.cls_to_test.checkboxes_emojis_map(checkboxes=target_s.filters.checkboxes, )
        expected = {
            'age': view.Keyboards.Checkboxes.CHECKED_EMOJI_CHECKBOX,
            'photo': view.Keyboards.Checkboxes.UNCHECKED_EMOJI_CHECKBOX,
            'country': view.Keyboards.Checkboxes.UNCHECKED_EMOJI_CHECKBOX,
            'city': view.Keyboards.Checkboxes.UNCHECKED_EMOJI_CHECKBOX,
        }

        assert actual == expected

    def test_get_checkboxes_keyboard(self, target_s: ITargetForm, ):
        actual_keyboard = self.cls_to_test.build(target=target_s, )
        expected_keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{self.cls_to_test.CHECKED_EMOJI_CHECKBOX} {Texts.Checkboxes.AGE_SPECIFIED}",
                        callback_data=f"{view.Cbks.CHECKBOX} age",
                    ),
                    InlineKeyboardButton(
                        text=f"{self.cls_to_test.UNCHECKED_EMOJI_CHECKBOX} {Texts.Checkboxes.COUNTRY_SPECIFIED}",
                        callback_data=f"{view.Cbks.CHECKBOX} country",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=f"{self.cls_to_test.UNCHECKED_EMOJI_CHECKBOX} {Texts.Checkboxes.CITY_SPECIFIED}",
                        callback_data=f"{view.Cbks.CHECKBOX} city",
                    ),
                    InlineKeyboardButton(
                        text=f"{self.cls_to_test.UNCHECKED_EMOJI_CHECKBOX} {Texts.Checkboxes.PHOTO_SPECIFIED}",
                        callback_data=f"{view.Cbks.CHECKBOX} photo",
                    ),
                ],
            ]
        )
        assert actual_keyboard.to_dict() == expected_keyboard.to_dict()


class TestGetStatisticWith:
    @staticmethod
    async def test_say_statistic_hello(mock_view_f: MagicMock):
        result = await view.Match.say_statistic_hello(self=mock_view_f, )
        mock_view_f.bot.send_message.acow(text=Texts.STATISTIC_HELLO, chat_id=mock_view_f.id, )
        assert result == mock_view_f.bot.send_message.return_value

    @staticmethod
    async def test_show_statistic(mock_view_f: MagicMock, mock_match_stats: MagicMock, ):
        statistic_text = (
            f'{Texts.Profile.TOTAL_LIKES_SET} {mock_match_stats.opposite_pos_votes_count}: '
            f'{Texts.FROM} {mock_match_stats.pos_votes_count}.\n'
            f'{Texts.Profile.TOTAL_DISLIKES_SET} {mock_match_stats.opposite_neg_votes_count}: '
            f'{Texts.FROM} {mock_match_stats.neg_votes_count}.\n'
            f'{Texts.Profile.TOTAL_UNMARKED_POSTS} {mock_match_stats.opposite_zero_votes_count}: '
            f'{Texts.FROM} {mock_match_stats.zero_votes_count}.\n'
            f'{Texts.Profile.SHARED_LIKES_PERCENTAGE}: {mock_match_stats.common_pos_votes_perc}%\n'
            f'{Texts.Profile.SHARED_DISLIKES_PERCENTAGE}: {mock_match_stats.common_neg_votes_perc}%\n'
            f'{Texts.Profile.SHARED_UNMARKED_POSTS_PERCENTAGE}: '
            f'{mock_match_stats.common_zero_votes_perc}%\n'
        )
        result = await view.Match.show_statistic(self=mock_view_f, match_stats=mock_match_stats, )
        mock_view_f.bot.send_message.acow(
            chat_id=mock_view_f.id,
            text=(
                f'{Texts.HERE_STATISTICS_WITH} '
                f'{mock_match_stats.user.ptb.name} '
                f'(id {mock_match_stats.with_user_id}):'
            ),
        )
        mock_view_f.bot.send_photo.acow(
            chat_id=mock_view_f.id,
            photo=mock_match_stats.get_pie_chart_result(),
            caption=statistic_text,
            reply_markup=view.tg_IKM.from_button(
                button=view.SharedKeyboards.get_show_profile_btn(user_id=mock_match_stats.user.id, ),
            )
        )
        assert result == (mock_view_f.bot.send_message.return_value, mock_view_f.bot.send_photo.return_value,)


class TestProfile:
    """test_profile"""

    @staticmethod
    @pytest_fixture(scope='function', )
    def profile(mock_bot: MagicMock, user_s: IUser, ):
        result = view.Profile(bot=mock_bot, data_source=user_s, id=user_s.id, )
        result.data.photos = ['foo', 'bar']
        result.TranslationsMap = {
            # Simplified to use value as translation
            result.Goal: {item: str(item.value) for item in view.Profile.Goal},
            result.Gender: {item: str(item.value) for item in view.Profile.Gender},
        }
        yield result

    @staticmethod
    def test_translate_text(profile: IProfile, ):
        result = view.Profile.translate_text(self=profile, )
        nickname_link = f"<a href='tg://user?id={profile.id}'>{profile.data.fullname}</a>"
        assert result == {
            Texts.Profile.NAME: nickname_link,
            Texts.Profile.GOAL: profile.translate_goal(),
            Texts.Profile.GENDER: profile.translate_gender(),
            Texts.Profile.AGE: profile.data.age,
            Texts.Profile.LOCATION: profile.translate_location(),
            Texts.Profile.ABOUT: profile.data.comment,
        }
        assert None not in result.values()
