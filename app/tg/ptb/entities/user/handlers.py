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

from rubik_core.entities.user.exceptions import IncorrectProfileValue

from app.entities.shared.exceptions import BadLocation, LocationServiceError


from .forms import NewUser as NewUserForm
from .texts import Reg as Texts

from app.tg.ptb.custom import end_conversation as custom_end_conversation

if TYPE_CHECKING:
    from telegram import Update
    from custom_ptb.callback_context import CallbackContext as CallbackContext


async def entry_point(_: Update, context: CallbackContext, ):
    await context.view.reg.say_reg_hello()
    return 0


async def entry_point_handler(_: Update, context: CallbackContext, ):
    context.user_data.forms.new_user = NewUserForm(user=context.user, )
    await context.view.reg.ask_user_name()
    return 1


async def name_handler(update: Update, context: CallbackContext, ):
    try:
        # await to get remote nickname
        await context.user_data.forms.new_user.handle_name(text=update.effective_message.text, )
    except IncorrectProfileValue:
        await context.view.reg.warn.incorrect_name()
        return
    await context.view.reg.ask_user_goal()
    return 2


async def goal_handler(update: Update, context: CallbackContext, ):
    try:
        context.user_data.forms.new_user.handle_goal(text=update.effective_message.text, )
    except IncorrectProfileValue:
        await context.view.reg.warn.incorrect_goal()
        return
    await context.view.reg.ask_user_gender()
    return 3


async def gender_handler(update: Update, context: CallbackContext, ):
    try:
        context.user_data.forms.new_user.handle_gender(text=update.effective_message.text, )
    except IncorrectProfileValue:
        await context.view.reg.warn.incorrect_gender()
        return
    await context.view.reg.ask_user_age()
    return 4


async def age_handler(update: Update, context: CallbackContext, ):
    try:
        context.user_data.forms.new_user.handle_age(text=update.effective_message.text, )
    except IncorrectProfileValue:
        await context.view.reg.warn.incorrect_age()
        return
    await context.view.reg.ask_user_location()
    return 5


async def location_handler_geo(update: Update, context: CallbackContext, ):  # user_city don't have validation
    """
    Maybe no necessary to get the country from the location, as the country may be determined incorrectly ?
    Perhaps no need to get city from the location, as the user may want to specify only a country ?
    """
    try:
        context.user_data.forms.new_user.handle_location_geo(location=update.effective_message.location, )
    except BadLocation:
        await context.view.reg.warn.incorrect_location()
        return
    except LocationServiceError:
        await context.view.location_service_error()
        return
    await context.view.reg.ask_user_photos()
    return 6


async def location_handler_text(update: Update, context: CallbackContext, ):  # user_city don't have validation
    """
    Maybe no necessary to get the country from the location, as the country may be determined incorrectly ?
    Perhaps no need to get city from the location, as the user may want to specify only a country ?
    """
    try:
        context.user_data.forms.new_user.handle_location_text(text=update.effective_message.text, )
    except IncorrectProfileValue:
        await context.view.reg.warn.incorrect_location()
        return
    await context.view.reg.ask_user_photos()
    return 6


async def photos_handler_tg_photo(update: Update, context: CallbackContext, ):
    """Always returns None"""
    result_text = context.user_data.forms.new_user.handle_photo_tg_object(
        photo=update.effective_message.photo,
        media_group_id=update.effective_message.media_group_id,
    )
    if result_text == Texts.PHOTO_ADDED_SUCCESS:
        await context.view.reg.say_photo_added_success(
            keyboard=context.user_data.forms.new_user.current_keyboard,
        )
    elif result_text == Texts.TOO_MANY_PHOTOS:
        await context.view.reg.warn.too_many_photos(
            # TODO passing keyboard explicitly is poor design. Use forms.new_user.keyboard inside views
            keyboard=context.user_data.forms.new_user.current_keyboard,
            used_photos=len(context.user_data.forms.new_user.photos, ),
        )


async def photos_handler_text(update: Update, context: CallbackContext, ):
    result_text = await context.user_data.forms.new_user.handle_photo_text(text=update.effective_message.text, )
    if result_text == Texts.PHOTOS_ADDED_SUCCESS:
        await context.view.reg.say_photo_added_success(
            keyboard=context.user_data.forms.new_user.current_keyboard,
        )
    elif result_text == Texts.TOO_MANY_PHOTOS:
        await context.view.reg.warn.too_many_photos(
            keyboard=context.user_data.forms.new_user.current_keyboard,
            used_photos=len(context.user_data.forms.new_user.photos, ),
        )
    elif result_text == Texts.PHOTOS_REMOVED_SUCCESS:
        await context.view.reg.say_photos_removed_success(
            keyboard=context.user_data.forms.new_user.current_keyboard,
        )
    elif result_text == Texts.NO_PHOTOS_TO_REMOVE:
        await context.view.reg.warn.no_profile_photos()
    elif result_text == Texts.INCORRECT_FINISH:
        await context.view.warn.incorrect_finish()
    elif result_text == Texts.FINISH_KEYWORD:
        await context.view.reg.ask_user_comment()
        return 7


async def comment_handler(update: Update, context: CallbackContext, ):
    try:
        context.user_data.forms.new_user.handle_comment(text=update.effective_message.text, )
    except IncorrectProfileValue:
        await context.view.reg.warn.comment_too_long(comment_len=len(update.effective_message.text), )
        return
    await context.view.reg.show_new_user(new_user=context.user_data.forms.new_user, )
    return 8


async def confirm_handler(update: Update, context: CallbackContext, ):
    # Create handler
    if update.effective_message.text.lower().strip() != Texts.FINISH_KEYWORD.lower():
        await context.view.reg.warn.incorrect_end_reg()
        return
    context.user_data.forms.new_user.create()
    await context.view.reg.say_success_reg()
    return custom_end_conversation()
