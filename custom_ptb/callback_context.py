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

from telegram import Update
from telegram.ext import CallbackContext as PtbCallbackContext, Application
from rubik_core.db.manager import Postgres, Params as DbParams

from app.tg.ptb.entities.view import View
from app.tg.ptb.entities.user.model import User as UserModel

if TYPE_CHECKING:
    from app.tg.ptb.structures import CustomUserData, CustomBotData


class CallbackContext(PtbCallbackContext, ):
    """Custom class for context."""

    user_data: CustomUserData
    bot_data: CustomBotData
    chat_data: CustomBotData
    db_params: DbParams

    @property
    def connection(self):
        if self.user:
            return self.user.connection
        else:
            super().__getattribute__('connection', )

    @connection.setter
    def connection(self, value, ):
        if self.user:
            self.user.connection = value
        else:
            super().__setattr__('connection', value)

    @property
    def user(self):
        return self.user_data.model

    @user.setter
    def user(self, value, ):
        self.user_data.model = value

    @property
    def view(self):
        return self.user_data.view

    @view.setter
    def view(self, value, ):
        self.user_data.view = value

    @classmethod
    def from_update(cls, update: object, application: Application, ) -> CallbackContext:
        context = super().from_update(update=update, application=application, )
        if update is not None and isinstance(update, Update):  # Some attrs may be assigned even without update, do it?
            # context.user_data is empty if the update was not produced by the user, but by the bot or channel
            if context.user_data:  # user_data guarantees that update.effective_user exists
                context.user = (
                        context.user  # None on first request by the cls attribute
                        or
                        UserModel(
                            id=update.effective_user.id,
                            ptb=update.effective_user,
                            connection=Postgres.get_connection(
                                from_pool=True,
                                key=update.effective_user.id,
                                lazy=True,
                            ),
                        )
                )
                context.connection = context.user.connection
                context.view = context.view or View(user=context.user, )  # None on first request by the cls attribute
            else:
                context.connection = Postgres.get_connection(from_pool=True, key=update.effective_chat.id, lazy=True, )
            context.db_params = DbParams(connection=context.connection, )
        return context
