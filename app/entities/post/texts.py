from app.postconfig import translators
from ..shared import texts as shared_texts


class Public:
    class Buttons:
        PENDING = shared_texts.Words.PENDING
        READY_TO_RELEASE = translators.posts("READY_TO_RELEASE")
        SEND = shared_texts.Words.SEND

    NO_PENDING = translators.posts("NO_PENDING")
    HELLO = translators.posts("PUBLIC_POST_HELLO")
    NO_NEW_POSTS = translators.posts("NO_NEW_POSTS")
    NO_MASS_POSTS = translators.posts("NO_MASS_POSTS")

    NOT_FOUND = translators.posts("POST_NOT_FOUND")
    ERROR_CREATE = translators.posts("ERROR_CREATE")


class Personal:
    class Buttons:
        ALLOW = shared_texts.Words.ALLOW
        DISALLOW = shared_texts.Words.DISALLOW
        ACCEPT = shared_texts.Words.ACCEPT
        DECLINE = shared_texts.Words.DECLINE
        READY = shared_texts.Words.READY

    WHO_TO_SHARE = translators.posts("WHO_TO_SHARE")
    WHO_TO_REQUEST = translators.posts("WHO_TO_REQUEST")
    NOTIFY_SHARE_PROPOSAL = translators.posts("NOTIFY_SHARE_PROPOSAL")  # format(USER_ID)
    NOTIFY_REQUEST_PROPOSAL = translators.posts("NOTIFY_REQUEST_PROPOSAL")  # format(USER_ID)
    USER_DECLINED_SHARE_PROPOSAL = translators.posts("USER_DECLINED_SHARE_PROPOSAL")  # format(USER_ID, )
    # format(ACCEPTER_USERNAME)
    USER_ACCEPTED_SHARE_PROPOSAL = translators.posts("USER_ACCEPTED_SHARE_PROPOSAL")
    # USER_DECLINES_SHARE_PROPOSAL = USER_DECLINED_INVITE  # format(USER_ID)
    USER_ACCEPTED_REQUEST_PROPOSAL = translators.posts("USER_ACCEPTED_REQUEST_PROPOSAL")  # format(USER_ID)
    USER_DECLINED_REQUEST_PROPOSAL = shared_texts.USER_DECLINED_REQUEST_PROPOSAL  # format(USER_ID)
    SENDER_HAS_NO_POSTS = translators.posts("SENDER_HAS_NO_PERSONAL_POSTS")

    HELLO = translators.posts("PERSONAL_POST_HELLO")
    NO_POSTS = translators.posts("NO_PERSONAL_POSTS")  # format(CREATE_PERSONAL_POST_CMD)
    HERE_YOUR_POSTS = translators.posts("HERE_YOUR_PERSONAL_POSTS")
    CANT_SEND_TO_THIS_USER = translators.posts("CANT_SEND_POSTS_TO_THIS_USER")


class Post:
    Public = Public
    Personal = Personal
    HERE_POST_PREVIEW = translators.posts("HERE_POST_PREVIEW")
    CREATED_SUCCESSFULLY = translators.posts("POST_CREATED_SUCCESSFULLY")  # Public or common?
    POST_TO_VOTE_NOT_FOUND = translators.posts("POST_TO_VOTE_NOT_FOUND")  # Public or common?
