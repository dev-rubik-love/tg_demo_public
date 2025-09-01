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


class KnownException(Exception):
    pass


class NoPhotos(KnownException, SystemError, ):
    pass


class NoVotes(KnownException, SystemError, ):
    pass


class NoSources(KnownException, SystemError, ):
    pass


class NoCovotes(KnownException, SystemError, ):
    pass


class PostNotFound(KnownException, FileNotFoundError, ):
    def __init__(self, post, ):
        post = getattr(post, 'post', post)  # Just in case if accidentally passed voted_post
        message = (
            f'{type(self).__name__} - '
            f'id: {post.id}; '
            f'channel_id: {post.channel_id}; ' if getattr(post, 'channel_id', False) else ''
            # f'{channel_message_id_str}'
            f'posts_channel_message_id: {post.posts_channel_message_id}; '
            if getattr(post, 'posts_channel_message_id', False) else ''
            f'message_id: {post.message_id}; ' if getattr(post, 'message_id', False) else ''
        )
        super(PostNotFound, self).__init__(message)


class IncorrectFinish(KnownException, ValueError, ):
    pass


class IncorrectSearchParameter(KnownException, ValueError, ):
    pass


class IncorrectVote(KnownException, ValueError, ):
    pass


class BadLocation(KnownException, ValueError, ):
    pass


class LocationServiceError(KnownException, SystemError, ):
    pass


class UserDeclinedRequest(KnownException, ValueError, ):
    pass


class DuplicateKeyError(KnownException, KeyError, ):
    pass


class ReqRequired(KnownException, ):
    pass


class UnexpectedException(Exception, ):
    pass


class UnknownPostType(UnexpectedException, ValueError, ):
    def __init__(self, post: object | None = None, ):
        message = f"Unknown post_type {type(post)}\n" if post else ""
        super(UnknownPostType, self).__init__(message)


class DevException(Exception):
    pass


class ConnectionNotPassed(DevException):
    pass
