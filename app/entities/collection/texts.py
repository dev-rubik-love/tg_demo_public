from app.postconfig import translators
from app.entities.shared.texts import Words as SharedWords


class Collections:
    ASK_FOR_NAMES = translators.collections("ASK_FOR_NAMES")
    MAX_NAME_LEN = translators.collections("MAX_NAME_LEN")  # format(MAX_NAME_LEN)
    ASK_TO_SHARE = translators.collections("ASK_TO_SHARE")
    COLLECTIONS_TO_SHARE_NOT_CHOSE = translators.collections("COLLECTIONS_TO_SHARE_NOT_CHOSE")
    NO_POSTS = translators.collections("NO_POSTS")
    NO_COLLECTIONS = translators.collections("NO_COLLECTIONS")  # format(CREATE_PERSONAL_POST_CMD)
    COLLECTION_NOT_FOUND = translators.collections("COLLECTION_NOT_FOUND")
    COLLECTION_POSTS_NOT_FOUND = translators.collections("COLLECTION_POSTS_NOT_FOUND")
    FEW_POSTS_NOT_FOUND = translators.collections("FEW_COLLECTION_POSTS_NOT_FOUND")  # format(num POSTS_COUNT)

    # Warn: грамматика, "штука" <5> "штук".
    NOTIFY_SHARE_PROPOSAL = translators.collections("NOTIFY_SHARE_PROPOSAL")  # format(USER_ID, COUNT)
    WHO_TO_SHARE = translators.collections("WHO_TO_SHARE")
    HERE_YOUR_COLLECTIONS = translators.collections("HERE_YOUR")
    HERE_SHARED = translators.collections("HERE_SHARED")

    SAY_CHOSE_FOR_POST = translators.collections("SAY_CHOSE_FOR_POST")
    HERE_POSTS = translators.collections("HERE_POSTS")

    SHARED_COLLECTIONS_NOT_FOUND = translators.collections("SHARED_COLLECTIONS_NOT_FOUND")
    USER_DECLINED_SHARE_PROPOSAL = translators.shared("USER_DECLINED_SHARE_PROPOSAL")  # format(USER_ID, )
    # format(ACCEPTER_USERNAME)
    USER_ACCEPTED_SHARE_PROPOSAL = translators.collections("USER_ACCEPTED_SHARE_PROPOSAL")

    DEFAULT_COLLECTION_NAME = translators.collections("DEFAULT_COLLECTION_NAME")  # format(USER_ID)
    POST_SUCCESS_ADDED_TO_COLLECTION = translators.collections(
        "POST_SUCCESS_ADDED_TO_COLLECTION"  # format(COLLECTION_NAME)
    )
    POST_SUCCESS_REMOVED_FROM_COLLECTION = translators.collections(
        "POST_SUCCESS_REMOVED_FROM_COLLECTION"  # format(COLLECTION_NAME)
    )
    COLLECTION_SUCCESS_ADDED = translators.collections("COLLECTION_SUCCESS_ADDED")
    COLLECTION_SUCCESS_REMOVED = translators.collections("COLLECTION_SUCCESS_REMOVED")

    FINISH_KEYWORD = SharedWords.FINISH
