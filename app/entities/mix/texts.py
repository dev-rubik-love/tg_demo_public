from __future__ import annotations

from app.config import MAIN_ADMIN_NAME, DONATE_URL
from app.postconfig import translators

from ..shared.texts import Warn

FAQ = translators.mix("FAQ").format(MAIN_ADMIN_NAME=MAIN_ADMIN_NAME, )
DONATE = translators.mix("DONATE").format(URL=DONATE_URL, )
MISUNDERSTAND = Warn.MISUNDERSTAND.replace('.', ':(')

# No CJM for app
START_MODE = translators.mix("START_MODE")  # format(REG_CMD, PUBLIC_MODE_CMD, PERSONAL_MODE_CMD, SEARCH_CMD, )
PUBLIC_MODE = translators.mix("PUBLIC_MODE").format(READY=translators.shared("READY"))
PERSONAL_MODE = translators.mix("PERSONAL_MODE").format(READY=translators.shared("READY"))
