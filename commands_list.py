# Список доступных команд для бота
import commands

cmds = {
    'помощь': commands.hlp,
    'кино': commands.movie_search,  # поиск фильмов
    'мульт': commands.mult_search,  # поиск мультфильмов
    'подробности': commands.details,  # подробности о фильме, мульте и т.д.
    'похожие': commands.similar,  # похожие на фильм
    'рекомендации': commands.recommendations,
    'популярные': commands.popular,
}
