from abc import ABC
from app.entities.match.form import ITarget as IAppTarget, Target as AppTarget


class ITarget(IAppTarget, ABC):
    channels_keyboard_message_id: int | None  # For the reply (link to original message)


class Target(AppTarget, ITarget, ):

    def __init__(self, *args, **kwargs, ):
        super().__init__(*args, **kwargs, )
        self.channels_keyboard_message_id: int | None = None  # For the reply (link to original message)

