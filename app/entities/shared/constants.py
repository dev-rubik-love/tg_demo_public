from re import compile as re_compile, IGNORECASE

from app.entities.shared.texts import Words

HIDE_S = 'hide'
START_S = 'start'  # Shared cuz TG automatically adds "/start" cmd as prefix in some cases
EMPTY_CBK_S = 'empty_cbk'

EMPTY_CBK_R = re_compile(fr'^{EMPTY_CBK_S}$', )
NO_SPACE_R = re_compile(r'^[^ ]+$', )
READY_R = re_compile(rf'^{Words.READY}$', IGNORECASE, )
CANCEL_R = re_compile(f'^{Words.CANCEL}$', IGNORECASE)
BACK_R = re_compile(f'^{Words.BACK}$', IGNORECASE)
SKIP_R = re_compile(f'^{Words.SKIP}$', IGNORECASE)
SHOW_PROFILE_R = re_compile(fr'^{Words.SHOW_PROFILE} \d+$', IGNORECASE)  # \d+ is the user id
