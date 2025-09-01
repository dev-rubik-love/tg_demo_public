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
from unittest.mock import create_autospec, AsyncMock  # Mock for isinstance
from typing import TYPE_CHECKING, Sequence, Callable

from pytest import fixture

from telegram.ext import ConversationHandler

from app.tg.ptb.entities.mix.handlers_definition import (
    debug_logger,
    typing_response,
    analytics_handler,
    release_resources,
    gen_bots_handler_cmd,
    gen_me_handler_cmd,
)
from app.entities.shared.texts import Words
from app.tg.ptb.entities.shared.handlers_definition import cancel_handler
from app.tg.ptb.app import create_ptb_app

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from telegram import Update
    from telegram.ext import Application, BaseHandler


async def cancel_body(  # pragma: no cover
        update_fabric: Callable[..., Update],
        ptb_app: Application,
        ch: ConversationHandler,
        callback: MagicMock,
        monkeypatch,
):
    """Test the shared cancel handler"""
    update = update_fabric(message_kwargs=dict(text=Words.CANCEL))
    ch._conversations[(update.effective_chat.id, update.effective_user.id)] = 0
    monkeypatch.setattr(callback, 'return_value', -1)
    await ptb_app.process_update(update=update, )
    callback.assert_called_once()
    callback.reset_mock()


def get_ch_handlers(ch: ConversationHandler, ) -> set[BaseHandler]:
    result = set()
    for handler in (
            ch.entry_points +
            # ch.prefallbacks +
            [handler for state_handler in [*ch.states.values()] for handler in state_handler] +
            ch.fallbacks
    ):
        result.add(handler)
    return result


def collect_handlers(handlers: Sequence[BaseHandler], ) -> set[tuple[str | None, BaseHandler]]:  # First is CH
    collected_handlers = set()
    for group_handlers in handlers:  # Collect stage
        for i, group_handler in enumerate(group_handlers):
            if isinstance(group_handler, ConversationHandler):
                # Just add the parent CH (maybe None) for easiest debug
                collected_handlers |= {(group_handler.name, handler) for handler in get_ch_handlers(ch=group_handler, )}
            else:
                collected_handlers.add((None, group_handler))
    return collected_handlers


@fixture(scope='package', )
def ptb_app(mock_bot_p: MagicMock, ) -> Application:
    ptb_app = create_ptb_app(bot=mock_bot_p, )
    ptb_app._initialized = True
    ptb_app.context_types.context.from_update = create_autospec(
        spec=ptb_app.context_types.context.from_update,
        spec_set=True,
    )
    ptb_app.context_types.context.from_update.return_value.refresh_data = AsyncMock()  # Need for PTB in process_update
    yield ptb_app


@fixture(scope='package', )
def app_s_with_mock_handlers(ptb_app: Application, ) -> Application:
    """Mock dispatcher handler (Only check that they were called)"""
    for callback, block in ptb_app.error_handlers.copy().items():  # Error handlers is just list of func
        ptb_app.remove_error_handler(callback=callback, )
        ptb_app.add_error_handler(callback=create_autospec(spec=callback, spec_set=True, ), block=block, )
    for _, handler in collect_handlers(handlers=ptb_app.handlers.values(), ):  # Mocking stage
        if not isinstance(handler.callback, AsyncMock):
            # TODO Failed to use create_autospec for age_handler, probably because of crate_autospec internal bug
            # Replace real callback during tests
            handler.callback = AsyncMock(
                spec_set=handler.callback,
                return_value=handler.callback,  # Just keep the ref of the orig func
            )
    yield ptb_app


def check_is_all_mock_handlers_called(handlers: Sequence[BaseHandler], ):
    """Internal test to check that all handlers was called"""
    collected_handlers = collect_handlers(handlers=handlers, )
    try:
        to_exclude = (
            debug_logger,
            typing_response,
            analytics_handler,
            release_resources,
            gen_bots_handler_cmd,
            gen_me_handler_cmd,
        )
        for ch_name, handler in collected_handlers:
            if handler not in to_exclude:  # Called on each update
                handler.callback.assert_not_called()
        yield
        for ch_name, handler in collected_handlers:
            if handler not in (cancel_handler, *to_exclude,):
                # separately
                handler.callback.assert_called_once()
    except AssertionError as e:  # pragma: no cover # Try - except to just add some additional exception context
        e.args = (f'func name - {handler.callback.return_value.__name__}, ch name - {ch_name}', *e.args,)
        raise
