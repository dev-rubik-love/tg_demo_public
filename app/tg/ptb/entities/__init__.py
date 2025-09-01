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

"""Control the import process"""
from .shared import constants, handlers, handlers_definition, texts, view

from .vote import constants
from .mix import constants
from .post import constants
from .collection import constants
from .match import constants
from .user import constants
from .cjm import constants

from .vote import model as vote_model
from .post import model as post_model
from .collection import model as collection_model
from .match import model as match_model
from .user import model as user_model

from .post import forms
from .match import forms
from .user import forms

from .post import services
from .collection import services

from .mix import handlers
from .vote import handlers
from .post import handlers
from .collection import handlers
from .match import handlers
from .user import handlers
from .cjm import handlers

from .vote import handlers_definition
from .mix import handlers_definition
from .post import handlers_definition
from .collection import handlers_definition
from .match import handlers_definition
from .user import handlers_definition
from .cjm import handlers_definition

from .mix import texts
from .post import texts
from .collection import texts
from .match import texts
from .user import texts
from .cjm import texts
from . import texts

from .mix import view
from .post import view
from .collection import view
from .match import view
from .user import view
from .cjm import view

available_handlers = (
    cjm.handlers_definition.available_handlers,
    user.handlers_definition.available_handlers,
    match.handlers_definition.available_handlers,
    mix.handlers_definition.available_handlers,
    collection.handlers_definition.available_handlers,
    post.handlers_definition.available_handlers,
    vote.handlers_definition.available_handlers,
    mix.handlers_definition.unknown_handlers,  # unknown handlers should be the last added
)

if TYPE_CHECKING:
    pass

# public vote mapper
vote_model.PublicVote.Post = post_model.PublicPost
vote_model.PublicVote.User = user_model.User

# personal vote mapper:
vote_model.PersonalVote.Post = post_model.PersonalPost
vote_model.PersonalVote.User = user_model.User

# public post mapper
post_model.PublicPost.Vote = vote_model.PublicVote
post_model.PublicPost.User = user_model.User

# personal post mapper
post_model.PersonalPost.Vote = vote_model.PersonalVote
post_model.PersonalPost.User = user_model.User

# collection mapper
collection_model.Collection.PublicPost = post_model.PublicPost
collection_model.Collection.PersonalPost = post_model.PersonalPost
collection_model.Collection.User = user_model.User

# matcher mapper
match_model.Matcher.Match = match_model.Match
match_model.Matcher.User = user_model.User

# user mapper
user_model.User.PublicVote = vote_model.PublicVote
user_model.User.PersonalVote = vote_model.PersonalVote
user_model.User.PublicPost = post_model.PublicPost
user_model.User.PersonalPost = post_model.PersonalPost
user_model.User.Collection = collection_model.Collection
user_model.User.Matcher = match_model.Matcher
