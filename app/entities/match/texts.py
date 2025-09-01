from app.config import MAIN_ADMIN_NAME
from app.postconfig import translators
from ..shared import texts as shared_texts

USE_GET_STATS_WITH_CMD = translators.search("USE_GET_STATS_WITH_CMD")  # format(GET_STATS_WITH_CMD, )


class Buttons:
    MALE = translators.search('MALE')
    FEMALE = translators.search('FEMALE')
    ANY_GENDER = translators.search("ANY_GENDER")
    I_WANNA_CHAT = translators.search("I_WANNA_CHAT")  # reg translator is ok
    I_WANNA_DATE = translators.search("I_WANNA_DATE")  # reg translator is ok
    I_WANNA_CHAT_AND_DATE = translators.search("I_WANNA_CHAT_AND_DATE")  # reg translator is ok
    ANY_AGE = translators.search("ANY_AGE")
    SHOW_ALL = translators.search("SHOW_ALL")
    SHOW_NEW = translators.search("SHOW_NEW")
    SHOW_MORE = translators.search("SHOW_MORE")
    FINISH = shared_texts.Words.FINISH
    SKIP = shared_texts.Words.SKIP
    BACK = shared_texts.Words.BACK
    ALL_CHANNELS = translators.search("ALL_CHANNELS")
    LIKES_FROM_BOT = translators.search("LIKES_FROM_BOT")


class Checkboxes:
    AGE_SPECIFIED = translators.search("AGE_SPECIFIED")
    COUNTRY_SPECIFIED = translators.search("COUNTRY_SPECIFIED")
    CITY_SPECIFIED = translators.search("CITY_SPECIFIED")
    PHOTO_SPECIFIED = translators.search("PHOTO_SPECIFIED")


class Result:
    NO_MATCHES_WITH_FILTERS = translators.search("NO_MATCHES_WITH_FILTERS")
    FOUND_MATCHES_COUNT = translators.search("FOUND_MATCHES_COUNT")  # format(FOUND_MATCHES_COUNT, )
    HERE_MATCH = translators.search("HERE_MATCH")  # format(SHARED_INTERESTS_PERCENTAGE, SHARED_INTERESTS_COUNT, )
    NO_MORE_MATCHES = translators.search("NO_MORE_MATCHES")


class Profile(shared_texts.Profile):  # Separate class instead of inheritance?
    TOTAL_LIKES_SET = translators.search("TOTAL_LIKES_SET")
    TOTAL_DISLIKES_SET = translators.search("TOTAL_DISLIKES_SET")
    TOTAL_UNMARKED_POSTS = translators.search("TOTAL_UNMARKED_POSTS")
    SHARED_LIKES_PERCENTAGE = translators.search("SHARED_LIKES_PERCENTAGE")
    SHARED_DISLIKES_PERCENTAGE = translators.search("SHARED_DISLIKES_PERCENTAGE")
    SHARED_UNMARKED_POSTS_PERCENTAGE = translators.search("SHARED_UNMARKED_POSTS_PERCENTAGE")
    IT_WANNA_CHAT = translators.search("IT_WANNA_CHAT")
    IT_WANNA_DATE = translators.search("IT_WANNA_DATE")
    IT_WANNA_CHAT_AND_DATE = CHAT_AND_DATE = translators.search("IT_WANNA_CHAT_AND_DATE")
    MALE = translators.search('MALE')
    FEMALE = translators.search('FEMALE')


class Search:
    Buttons = Buttons
    Checkboxes = Checkboxes
    Result = Result
    Profile = Profile

    NO_VOTES = translators.search("NO_VOTES")  # format(POSTS_CHANNEL_LINK, PUBLIC_MODE_CMD, GET_PUBLIC_POST_CMD, )
    NO_COVOTES = translators.search("NO_COVOTES")  # format(POSTS_CHANNEL_LINK, PUBLIC_MODE_CMD, GET_PUBLIC_POST_CMD, )
    NO_SOURCES = translators.search("NO_SOURCES")

    STEP_0 = translators.search("SEARCH_STEP_0")
    ASK_VOTES_SOURCES = translators.search("ASK_VOTES_SOURCES")  # Currently only type source is tg channel
    STEP_1 = translators.search("SEARCH_STEP_1")
    STEP_2 = translators.search("SEARCH_STEP_2")
    STEP_3 = translators.search("SEARCH_STEP_3")
    STEP_4 = shared_texts.FOR_READY

    NEW_FILTERS_SUGGESTIONS = translators.search("NEW_FILTERS_SUGGESTIONS").format(ADMIN=MAIN_ADMIN_NAME, )
    ERROR_FILTERS = translators.search("ERROR_FILTERS")
    TARGET_GOALS = [
        Buttons.I_WANNA_CHAT,
        Buttons.I_WANNA_DATE,
        Buttons.I_WANNA_CHAT_AND_DATE,
    ]
    TARGET_GENDERS = [translators.search('MALE'), translators.search('FEMALE'), translators.search('ANY_GENDER'), ]
    TARGET_SHOW_CHOICE = [translators.search('SHOW_ALL'), translators.search('SHOW_NEW'), ]

    INCORRECT_TARGET_GOAL = translators.search("INCORRECT_TARGET_GOAL").format(
        MISUNDERSTAND=shared_texts.Warn.MISUNDERSTAND,
        I_WANNA_CHAT=Buttons.I_WANNA_CHAT,
        I_WANNA_DATE=Buttons.I_WANNA_DATE,
        I_WANNA_CHAT_AND_DATE=Buttons.I_WANNA_CHAT_AND_DATE,
    )
    INCORRECT_TARGET_GENDER = translators.search("INCORRECT_TARGET_GENDER").format(
        MISUNDERSTAND=shared_texts.Warn.MISUNDERSTAND,
        MALE=Buttons.MALE,
        FEMALE=Buttons.FEMALE,
        ANY_GENDER=Buttons.ANY_GENDER,
    )
    INCORRECT_TARGET_AGE = translators.search("INCORRECT_TARGET_AGE").format(
        MISUNDERSTAND=shared_texts.Warn.MISUNDERSTAND,
        ANY_AGE=Buttons.ANY_AGE,
    )
    INCORRECT_SHOW_OPTION = translators.search("INCORRECT_SHOW_OPTION").format(
        MISUNDERSTAND=shared_texts.Warn.MISUNDERSTAND,
        SHOW_ALL=Buttons.SHOW_ALL,
        SHOW_NEW=Buttons.SHOW_NEW,
    )
    INCORRECT_SHOW_MORE_OPTION = translators.search("INCORRECT_SHOW_MORE_OPTION").format(
        MISUNDERSTAND=shared_texts.Warn.MISUNDERSTAND,
        SHOW_MORE=Buttons.SHOW_MORE,
        FINISH=Buttons.FINISH,
    )

    STATISTIC_HELLO = translators.search("STATISTIC_HELLO")
    HERE_STATISTICS_WITH = translators.search("HERE_STATISTICS_WITH")
    POSSIBLE_LONG_SEARCH = translators.search("POSSIBLE_LONG_SEARCH")
