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

from telegram.error import TelegramError
from rubik_core.entities.user.exceptions import IncorrectProfileValue

from app.entities.shared.exceptions import NoVotes, NoSources, NoCovotes
from .model import MatchStats

from .texts import Search as Texts
from .forms import Target as TargetForm
from .view import Keyboards as ViewKeyboards

from app.tg.ptb.custom import accept_user as custom_accept_user, end_conversation as utils_end_conversation

if TYPE_CHECKING:
    from telegram import Update
    from custom_ptb.callback_context import CallbackContext as CallbackContext
    from .model import IMatch


async def entry_point(update, context):
    await context.view.match.say_search_hello()
    context.user_data.forms.target = TargetForm(user=context.user, )
    try:
        context.user_data.forms.target.handle_start_search(text=update.effective_message.text, )
    except NoVotes:
        await context.view.match.no_votes()
        return utils_end_conversation()
    if len(context.user.matcher.available_sources) > 1:  # Show channels option only if more than 1
        sent_message = await context.view.match.ask_votes_channel_sources(
                # Convert set to dict with default True values
                sources=dict.fromkeys(context.user.matcher.available_sources, True),
            )
        context.user_data.forms.target.channels_keyboard_message_id = sent_message.message_id
    return 0


async def entry_point_handler(_: Update, context: CallbackContext):
    """handle_votes_sources"""
    try:
        context.user_data.forms.target.handle_target_sources()  # Sources set over the cbk_handler
    except NoSources:
        await context.view.match.no_sources(
            reply_to_message_id=context.user_data.forms.target.channels_keyboard_message_id
        )
        return
    except NoCovotes:  # Use directly context.user.matcher.is_user_has_covotes?
        await context.view.match.no_covotes()
        # Feature: If not all sources selected - return None to reselect them?
        return utils_end_conversation()
    await context.view.match.ask_target_goal()
    return 1


async def goal_handler(update: Update, context: CallbackContext):
    try:
        context.user_data.forms.target.handle_goal(text=update.effective_message.text, )
    except IncorrectProfileValue:
        await context.view.match.warn.incorrect_target_goal()
        return
    await context.view.match.ask_target_gender()
    return 2


async def gender_handler(update: Update, context: CallbackContext):
    try:
        context.user_data.forms.target.handle_gender(text=update.effective_message.text, )
    except IncorrectProfileValue:
        await context.view.match.warn.incorrect_target_gender()
        return
    await context.view.match.ask_target_age()
    return 3


async def age_handler(update: Update, context: CallbackContext):
    try:
        context.user_data.forms.target.handle_age(text=update.effective_message.text, )
    except IncorrectProfileValue:
        await context.view.match.warn.incorrect_target_age()
        return
    await context.view.match.show_target_checkboxes(target=context.user_data.forms.target, )
    await context.view.match.ask_confirm()  # Send message to make delay. The answer is no matter.
    return 4


async def checkboxes_handler(_: Update, context: CallbackContext):
    context.user.matcher.make_search(
        channel_ids={source for source, is_chosen in context.user_data.forms.target.sources.items() if is_chosen}
    )
    if context.user.matcher.matches.all:  # If user has matches
        await context.view.match.ask_which_matches_show(
            matches=context.user.matcher.matches,
        )
    else:
        await context.view.match.no_matches_with_filters()
        return utils_end_conversation()
    return 5


async def match_type_handler(update: Update, context: CallbackContext):
    try:
        context.user_data.forms.target.handle_show_option(text=update.effective_message.text, )
        context.user.matcher.set_current_matches()  # outside the form cuz not related directly to it
    except IncorrectProfileValue:
        await context.view.match.warn.incorrect_show_option()
        return
    if match := context.user.matcher.get_match():  # Show first match to wait user input
        match.load()
        await context.view.match.show_match(match=match, )
        match.create()
    else:
        await context.view.match.no_more_matches()
        return utils_end_conversation()
    return 6


async def show_match_handler(update: Update, context: CallbackContext):
    message_text = update.effective_message.text.lower().strip()
    if message_text == Texts.Buttons.SHOW_MORE.lower():
        match: IMatch | None = context.user.matcher.get_match()
        if match:
            match.load()
            await context.view.match.show_match(match=match, )
            match.create()
        else:
            await context.view.match.no_more_matches()
            return utils_end_conversation()
    elif message_text == Texts.COMPLETE_KEYWORD.lower():
        await context.view.match.say_search_goodbye()
        return utils_end_conversation()
    else:
        await context.view.match.warn.incorrect_show_more_option()
        return


async def checkbox_cbk_handler(update: Update, context: CallbackContext) -> None:
    _, button_name = update.callback_query.data.split()
    context.user_data.forms.target.filters.checkboxes[button_name] ^= 1  # Swap between 1 and 0
    await context.view.match.update_target_checkboxes(
        message=update.effective_message,
        target=context.user_data.forms.target,
    )
    await update.callback_query.answer()
    return


async def channel_sources_cbk_handler(update: Update, context: CallbackContext):
    channel_id, is_chosen = ViewKeyboards.AskVotesChannelSources.extract_cbk_data(match=context.match, )
    context.user_data.forms.target.handle_source_cbk(channel_id=channel_id, is_chosen=is_chosen, )
    await context.view.match.update_chosen_channels_keyboard(
        message=update.effective_message,
        cbk_data=update.callback_query.data,
    )
    await update.callback_query.answer()
    return


class GetStatisticWith:

    @staticmethod
    async def entry_point(_: Update, context: CallbackContext, ):
        await context.view.match.say_statistic_hello()
        return 0

    @staticmethod
    async def entry_point_handler(update: Update, context: CallbackContext, ):
        with_id = await custom_accept_user(app=context.application, message=update.message, )
        if with_id is None:
            await context.view.warn.incorrect_user()
            return
        match_stats = MatchStats(
            user=context.user,
            with_user_id=with_id,
        )
        try:
            await context.view.match.show_statistic(match_stats=match_stats, )
        except TelegramError:
            await context.view.user_not_found()
            return
        return utils_end_conversation()


async def personal_example(_: Update, context: CallbackContext, ):
    # May be improved with "app_models_mix.MatchStats.get_random.statistic" classmethod
    statistic = MatchStats(
        user=context.user,
        with_user_id=123456,  # Any fake number
        set_statistic=False,
    )
    statistic.fill_random()
    await context.view.match.show_statistic(match_stats=statistic, )
