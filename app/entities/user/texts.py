from app.postconfig import translators
from ..shared import texts as shared_texts


class Buttons:
    REMOVE_PHOTOS = translators.user("REMOVE_PHOTOS")
    USE_ACCOUNT_NAME = translators.user("USE_ACCOUNT_NAME")
    USE_ACCOUNT_PHOTOS = translators.user("USE_ACCOUNT_PHOTOS")
    SEND_LOCATION = translators.user("SEND_LOCATION")
    I_MALE = translators.user("I_MALE")
    I_FEMALE = translators.user("I_FEMALE")
    I_WANNA_CHAT = translators.user("I_WANNA_CHAT")
    I_WANNA_DATE = translators.user("I_WANNA_DATE")
    I_WANNA_CHAT_AND_DATE = translators.user("I_WANNA_CHAT_AND_DATE")
    FINISH = shared_texts.Words.FINISH
    BACK = shared_texts.Words.BACK
    SKIP = shared_texts.Words.SKIP
    CANCEL = shared_texts.Words.CANCEL


class Profile:
    I_MALE = Buttons.I_MALE
    I_FEMALE = Buttons.I_FEMALE
    I_WANNA_CHAT = Buttons.I_WANNA_CHAT
    I_WANNA_DATE = Buttons.I_WANNA_DATE
    I_WANNA_CHAT_AND_DATE = Buttons.I_WANNA_CHAT_AND_DATE


class Reg:
    Buttons = Buttons
    Profile = Profile

    HERE_PROFILE_PREVIEW = shared_texts.HERE_PROFILE_PREVIEW

    Profile.I_MALE = Buttons.I_MALE
    Profile.I_FEMALE = Buttons.I_FEMALE
    Profile.I_WANNA_CHAT = Buttons.I_WANNA_CHAT
    Profile.I_WANNA_DATE = Buttons.I_WANNA_DATE
    Profile.I_WANNA_CHAT_AND_DATE = Buttons.I_WANNA_CHAT_AND_DATE

    REG_GOALS = TARGET_GOALS = [
        Buttons.I_WANNA_CHAT,
        Buttons.I_WANNA_DATE,
        Buttons.I_WANNA_CHAT_AND_DATE,
    ]
    REG_GENDERS = [Buttons.I_MALE, Buttons.I_FEMALE, ]

    COMMAND_FOR_REG = translators.user("COMMAND_FOR_REG")  # format(REG_CMD=REG_COMMAND, )

    STEP_0 = translators.user("REG_STEP_0")
    STEP_1 = translators.user("REG_STEP_1")
    STEP_2 = translators.user("REG_STEP_2")
    STEP_3 = translators.user("REG_STEP_3")
    STEP_4 = translators.user("REG_STEP_4")
    STEP_5 = translators.user("REG_STEP_5")
    STEP_6 = translators.user("REG_STEP_6")
    STEP_7 = translators.user("REG_STEP_7")

    SUCCESS_REG = translators.user("SUCCESS_REG")

    PHOTOS_ADDED_SUCCESS = translators.user("PHOTOS_ADDED_SUCCESS")
    PHOTOS_REMOVED_SUCCESS = translators.user("PHOTOS_REMOVED_SUCCESS")
    PHOTO_ADDED_SUCCESS = translators.user("PHOTO_ADDED_SUCCESS")
    NO_PHOTOS_TO_REMOVE = translators.user("NO_PHOTOS_TO_REMOVE")
    TOO_MANY_PHOTOS = translators.user("TOO_MANY_PHOTOS")  # format(USED_PHOTOS, MAX_PHOTOS_COUNT, )
    NO_PROFILE_PHOTOS = translators.user("NO_PROFILE_PHOTOS")

    INCORRECT_NAME = shared_texts.Warn.MISUNDERSTAND
    INCORRECT_GOAL = translators.user("INCORRECT_GOAL").format(
        MISUNDERSTAND=shared_texts.Warn.MISUNDERSTAND,
        I_WANNA_CHAT=Buttons.I_WANNA_CHAT,
        I_WANNA_DATE=Buttons.I_WANNA_DATE,
        I_WANNA_CHAT_AND_DATE=Buttons.I_WANNA_CHAT_AND_DATE,
    )
    INCORRECT_GENDER = translators.user("INCORRECT_GENDER").format(
        MISUNDERSTAND=shared_texts.Warn.MISUNDERSTAND,
        I_MALE=Buttons.I_MALE,
        I_FEMALE=Buttons.I_FEMALE,
    )  # No specific
    INCORRECT_AGE = translators.user("INCORRECT_AGE").format(MISUNDERSTAND=shared_texts.Warn.MISUNDERSTAND, )
    INCORRECT_LOCATION = translators.user("INCORRECT_LOCATION").format(MISUNDERSTAND=shared_texts.Warn.MISUNDERSTAND, )
    INCORRECT_FINISH = shared_texts.Warn.INCORRECT_FINISH

    ERROR_LOCATION_SERVICE = shared_texts.Warn.ERROR_LOCATION_SERVICE
    ERROR_SAVING_PHOTOS = translators.user("ERROR_SAVING_PHOTOS")
    ERROR_SAVING_PROFILE = translators.user("ERROR_SAVING_PROFILE")

    END_REG_HELP = translators.user("END_REG_HELP").format(
        MISUNDERSTAND=shared_texts.Warn.MISUNDERSTAND,
        FINISH=shared_texts.Words.FINISH,
        BACK=shared_texts.Words.BACK,
        CANCEL=shared_texts.Words.CANCEL,
    )
