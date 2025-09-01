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
from unittest.mock import AsyncMock

from pytest import fixture as pytest_fixture, mark as pytest_mark

from app.tg.ptb.entities.match.model import Matcher
from app.tg.ptb.entities.match.constants import Cbks
from app.tg.ptb.entities.match import handlers

from tests.conftest import patch_object
from tests.tg.ptb.conftest import get_text_cases

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from app.tg.ptb.entities.match.model import IMatcher


@pytest_fixture(scope='function', )
async def patched_target_form_cls(mock_target: MagicMock, ):
    with patch_object(target=handlers, attribute='TargetForm', return_value=mock_target, ) as result:
        yield result


@pytest_fixture(scope='function', )
def patched_match_stats_cls() -> MagicMock:
    with patch_object(target=handlers, attribute='MatchStats', ) as MockMatchStats:
        yield MockMatchStats


async def test_entry_point_no_votes(
        mock_context: MagicMock,
        mock_update: MagicMock,
        patched_target_form_cls: MagicMock,
):
    # Set side_effect on the cls cuz instance not exists yet
    patched_target_form_cls.return_value.handle_start_search.side_effect = handlers.NoVotes
    result = await handlers.entry_point(update=mock_update, context=mock_context, )
    # Checks
    mock_context.view.match.say_search_hello.acow()
    patched_target_form_cls.acow(user=mock_context.user, )
    mock_context.user_data.forms.target.handle_start_search.acow(text=mock_update.effective_message.text, )
    mock_context.view.match.no_votes.acow()
    assert result == -1


async def test_entry_point_success(
        mock_context: MagicMock, mock_update: MagicMock, patched_target_form_cls: MagicMock, ):
    mock_context.user.matcher.available_sources = {1, 2, }
    result = await handlers.entry_point(update=mock_update, context=mock_context, )
    mock_context.view.match.say_search_hello.acow()
    patched_target_form_cls.acow(user=mock_context.user, )
    mock_context.user_data.forms.target.handle_start_search.acow(text=mock_update.effective_message.text, )
    mock_context.view.match.ask_votes_channel_sources.acow(sources={1: True, 2: True, }, )
    assert (
            mock_context.user_data.forms.target.channels_keyboard_message_id ==
            mock_context.view.match.ask_votes_channel_sources.return_value.message_id
    )
    assert result == 0


async def test_channel_sources_cbk_handler(mock_context: MagicMock, mock_update: MagicMock, ):
    with patch_object(
            target=handlers.ViewKeyboards.AskVotesChannelSources,
            attribute='extract_cbk_data',
            return_value=(1, True),
    ) as mock_extract_cbk_data:
        result = await handlers.channel_sources_cbk_handler(update=mock_update, context=mock_context, )
    mock_extract_cbk_data.acow(match=mock_context.match, )
    mock_context.user_data.forms.target.handle_source_cbk.acow(channel_id=1, is_chosen=True, )
    mock_context.view.match.update_chosen_channels_keyboard.acow(
        message=mock_update.effective_message,
        cbk_data=mock_update.callback_query.data,
    )
    mock_update.callback_query.answer.acow()
    assert result is None


async def test_entry_point_handler_no_sources(mock_context: MagicMock, mock_update: MagicMock, ):
    mock_context.user_data.forms.target.handle_target_sources.side_effect = handlers.NoSources
    # Execution
    result = await handlers.entry_point_handler(_=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.target.handle_target_sources.acow()
    mock_context.view.match.no_sources.acow(
        reply_to_message_id=mock_context.user_data.forms.target.channels_keyboard_message_id
    )
    assert result is None


async def test_entry_point_handler_no_covotes(mock_context: MagicMock, ):
    mock_context.user_data.forms.target.handle_target_sources.side_effect = handlers.NoCovotes
    # Execution
    result = await handlers.entry_point_handler(_=typing_Any, context=mock_context, )
    # Checks
    mock_context.user_data.forms.target.handle_target_sources.acow()
    mock_context.view.match.no_covotes.acow()
    assert result == -1


async def test_entry_point_handler_success(mock_context: MagicMock, ):
    # Execution
    result = await handlers.entry_point_handler(_=typing_Any, context=mock_context, )
    # Checks
    mock_context.user_data.forms.target.handle_target_sources.acow()
    mock_context.view.match.ask_target_goal.acow()
    assert result == 1


async def test_goal_handler_incorrect(mock_context: MagicMock, mock_update: MagicMock, ):
    mock_update.effective_message.text = 'foo'
    mock_handle_goal = mock_context.user_data.forms.target.handle_goal
    mock_handle_goal.side_effect = handlers.IncorrectProfileValue
    # Execution
    result = await handlers.goal_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.target.handle_goal.acow(text=mock_update.effective_message.text, )
    mock_context.view.match.warn.incorrect_target_goal.acow()

    assert result is None


@pytest_mark.parametrize(argnames='text', argvalues=get_text_cases(texts=handlers.Texts.TARGET_GOALS))
async def test_goal_handler(mock_context: MagicMock, mock_update: MagicMock, text: str, mock_target, ):
    mock_update.effective_message.text = text
    # Execution
    result = await handlers.goal_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.target.handle_goal.acow(text=text)
    mock_context.view.match.ask_target_gender.acow()

    assert result == 2


async def test_gender_handler_incorrect(mock_context: MagicMock, mock_update: MagicMock, ):
    mock_update.effective_message.text = 'foo'
    mock_handle_gender = mock_context.user_data.forms.target.handle_gender
    mock_handle_gender.side_effect = handlers.IncorrectProfileValue
    # Execution
    result = await handlers.gender_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.target.handle_gender.acow(
        text=mock_update.effective_message.text,
    )
    mock_context.view.match.warn.incorrect_target_gender.acow()

    assert result is None


@pytest_mark.parametrize(
    argnames='text',
    argvalues=get_text_cases(texts=handlers.Texts.TARGET_GENDERS),
)
async def test_gender_handler(mock_context: MagicMock, mock_update: MagicMock, text: str, ):
    mock_update.effective_message.text = text
    # Execution
    result = await handlers.gender_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.target.handle_gender.acow(
        text=mock_update.effective_message.text,
    )
    mock_context.view.match.ask_target_age.acow()

    assert result == 3


async def test_age_handler_incorrect(mock_context: MagicMock, mock_update: MagicMock, ):
    mock_update.effective_message.text = 'foo'
    mock_handle_age = mock_context.user_data.forms.target.handle_age
    mock_handle_age.side_effect = handlers.IncorrectProfileValue
    # Execution
    result = await handlers.age_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.target.handle_age.acow(
        text=mock_update.effective_message.text,
    )
    mock_context.view.match.warn.incorrect_target_age.acow()

    assert result is None


@pytest_mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['e1e0', 'sad4fs2', '99lk&^*']))
async def test_age_handler(mock_context: MagicMock, mock_update: MagicMock, text: str, ):
    mock_update.effective_message.text = text
    # Execution
    result = await handlers.age_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.target.handle_age.acow(
        text=mock_update.effective_message.text,
    )
    mock_context.view.match.show_target_checkboxes.acow(
        target=mock_context.user_data.forms.target,
    )
    mock_context.view.match.ask_confirm.acow()
    assert result == 4


async def test_checkboxes_handler_no_matches_with_filters(mock_context: MagicMock, mock_update: MagicMock, ):
    mock_update.effective_message.text = 'foo'
    mock_context.user.matcher.matches.all = []
    result = await handlers.checkboxes_handler(_=mock_update, context=mock_context, )
    mock_context.user.matcher.make_search.acow(
        channel_ids={source for source, is_chosen in mock_context.user_data.forms.target.sources.items() if is_chosen}
    )
    mock_context.view.match.no_matches_with_filters.acow()

    assert result == -1


async def test_checkboxes_handler(mock_context: MagicMock, mock_update: MagicMock, ):
    mock_update.effective_message.text = 'foo'
    # Execution
    mock_context.user.matcher.matches.all = ['foo']
    result = await handlers.checkboxes_handler(_=mock_update, context=mock_context, )
    # Checks
    mock_context.user.matcher.make_search.acow(
        channel_ids={source for source, is_chosen in mock_context.user_data.forms.target.sources.items() if is_chosen}
    )
    matches = mock_context.user.matcher.matches
    mock_context.view.match.ask_which_matches_show.acow(matches=matches, )

    assert result == 5


async def test_match_type_handler_incorrect(mock_context: MagicMock, mock_update: MagicMock, ):
    mock_update.effective_message.text = 'foo'
    mock_handle_show_option = mock_context.user_data.forms.target.handle_show_option
    mock_handle_show_option.side_effect = handlers.IncorrectProfileValue
    # Execution
    result = await handlers.match_type_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.target.handle_show_option.acow(
        text=mock_update.effective_message.text,
    )
    mock_context.view.match.warn.incorrect_show_option.acow()

    assert result is None


async def test_match_type_handler_no_more_matches(mock_context: MagicMock, mock_update: MagicMock, ):
    mock_update.effective_message.text = handlers.Texts.Buttons.SHOW_ALL
    mock_context.user.matcher.get_match.return_value = None
    # Execution
    result = await handlers.match_type_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user.matcher.get_match.acow()
    mock_context.view.match.no_more_matches.acow()

    assert result == -1


@pytest_mark.parametrize(
    argnames='text',
    argvalues=get_text_cases(texts=handlers.Texts.TARGET_SHOW_CHOICE),
)
async def test_match_type_handler(
        mock_context: MagicMock,
        mock_update: MagicMock,
        match_s: IMatcher,
        text: str,
):
    mock_update.effective_message.text = text
    mock_context.user.matcher.get_match.return_value = AsyncMock(spec_set=match_s, )
    # Execution
    result = await handlers.match_type_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user.matcher.get_match.acow()
    mock_context.view.match.show_match.acow(match=mock_context.user.matcher.get_match.return_value, )
    mock_context.user.matcher.get_match.return_value.create.acow()

    assert result


async def test_show_match_handler_incorrect(mock_context: MagicMock, mock_update: MagicMock, ):
    mock_update.effective_message.text = 'foo'
    # Execution
    result = await handlers.show_match_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.view.match.warn.incorrect_show_more_option.acow()

    assert result is None


async def test_show_match_handler_no_more_matches(mock_context: MagicMock, mock_update: MagicMock, ):
    mock_update.effective_message.text = handlers.Texts.Buttons.SHOW_MORE
    mock_context.user.matcher.get_match.return_value = None
    # Execution
    result = await handlers.show_match_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.view.match.no_more_matches.acow()

    assert result == -1


@pytest_mark.parametrize(
    argnames='text',
    argvalues=get_text_cases(texts=[handlers.Texts.COMPLETE_KEYWORD]),
)
async def test_show_match_handler_complete(mock_context: MagicMock, mock_update: MagicMock, text: str, ):
    mock_update.effective_message.text = text
    # Execution
    result = await handlers.show_match_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.view.match.say_search_goodbye.acow()

    assert result == -1


async def test_show_match_handler(mock_context: MagicMock, mock_update: MagicMock, ):
    mock_update.effective_message.text = handlers.Texts.Buttons.SHOW_MORE
    # Execution
    result = await handlers.show_match_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user.matcher.get_match.acow()
    mock_context.view.match.show_match.acow(match=mock_context.user.matcher.get_match.return_value, )
    mock_context.user.matcher.get_match.return_value.create.acow()

    assert result is None


@pytest_mark.parametrize(argnames='checkbox', argvalues=Matcher.Filters.Checkboxes(), )
async def test_checkbox_cbk_handler(
        mock_context: MagicMock,
        mock_update: MagicMock,
        checkbox: str,
):
    mock_update.callback_query.data = f'{Cbks.CHECKBOX} {checkbox}'
    await handlers.checkbox_cbk_handler(update=mock_update, context=mock_context, )
    mock_context.view.match.update_target_checkboxes(
        message=mock_update.effective_message,
        target=mock_context.user_data.forms.target,
    )
    mock_update.callback_query.answer.acow()


async def test_personal_example(mock_context: MagicMock, patched_match_stats_cls: MagicMock, ):
    result = await handlers.personal_example(_=typing_Any, context=mock_context, )
    patched_match_stats_cls.acow(user=mock_context.user, with_user_id=123456, set_statistic=False, )
    patched_match_stats_cls.return_value.fill_random.acow()
    mock_context.view.match.show_statistic.acow(match_stats=patched_match_stats_cls.return_value, )
    assert result is None


class TestGetStatisticWith:

    @staticmethod
    async def test_entry_point(mock_context: MagicMock, ):
        result = await handlers.GetStatisticWith.entry_point(_=typing_Any, context=mock_context, )
        mock_context.view.match.say_statistic_hello.acow()

        assert result == 0

    class TestEntryPointHandler:
        """entry_point_handler"""

        @staticmethod
        async def test_incorrect_user(
                mock_update: MagicMock,
                mock_context: MagicMock,
        ):
            with patch_object(
                    target=handlers,
                    attribute='custom_accept_user',
                    return_value=None,
            ) as mock_accept_user:
                result = await handlers.GetStatisticWith.entry_point_handler(
                    update=mock_update,
                    context=mock_context,
                )
            mock_accept_user.acow(app=mock_context.application, message=mock_update.message, )
            mock_context.view.warn.incorrect_user.acow()
            assert len(mock_context.view.mock_calls, ) == 1
            assert result is None

        @staticmethod
        async def test_user_not_found(
                mock_update: MagicMock,
                mock_context: MagicMock,
                patched_match_stats_cls: MagicMock,
        ):
            mock_context.view.match.show_statistic.side_effect = handlers.TelegramError('')
            with patch_object(target=handlers, attribute='custom_accept_user', autospec=True, ) as mock_accept_user:
                # Execution
                result = await handlers.GetStatisticWith.entry_point_handler(
                    update=mock_update,
                    context=mock_context,
                )
            mock_accept_user.acow(app=mock_context.application, message=mock_update.message, )
            patched_match_stats_cls.acow(user=mock_context.user, with_user_id=mock_accept_user.return_value, )
            mock_context.view.match.show_statistic.acow(match_stats=patched_match_stats_cls.return_value, )
            mock_context.view.user_not_found.acow()
            assert result is None
            patched_match_stats_cls.reset_mock()

        @staticmethod
        async def test_success(
                mock_update: MagicMock,
                mock_context: MagicMock,
                patched_match_stats_cls: MagicMock,
        ):
            with (
                patch_object(target=handlers, attribute='custom_accept_user', ) as mock_accept_user,
                patch_object(target=handlers, attribute='utils_end_conversation', ) as mock_end_conversation,
            ):
                # Execution
                result = await handlers.GetStatisticWith.entry_point_handler(
                    update=mock_update,
                    context=mock_context,
                )
            mock_accept_user.acow(app=mock_context.application, message=mock_update.message, )
            patched_match_stats_cls.acow(user=mock_context.user, with_user_id=mock_accept_user.return_value, )
            mock_context.view.match.show_statistic.acow(match_stats=patched_match_stats_cls.return_value, )
            assert result == mock_end_conversation.return_value
            patched_match_stats_cls.reset_mock()
