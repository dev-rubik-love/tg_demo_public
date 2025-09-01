from .mix.constants import Cmds as Mix
from .post.constants import Cmds as Post
from .collection.constants import Cmds as Collection
from .match.constants import Cmds as Match
from .user.constants import Cmds as User
from .cjm.constants import Cmds as Cjm

"""
got via: 
commands = await bot.get_my_commands()
(print(f'/{command.command} - {command.description}') for command in commands])

start - Нажми сюда если ты здесь первый раз
help - Помощь
public_mode - Найти людей с общими лайками (для новых пользователей)
personal_mode - Узнать общие интересы с другим человеком (для новых пользователей)
search - Найти людей с общими лайками (для опытных пользователей)
reg - Зарегистрироваться чтобы вас могли найти
create_public_post - Создать публичный пост
create_personal_post - Создать персональный пост
get_my_collections - Показать мои коллекции
share_collections - Поделиться моими коллекциями
get_stats_with - Получить статистику с пользователем
personal_mode_example - Показать пример персонального режима
all_commands - Все команды бота (расширенный список)
"""