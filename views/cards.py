def movie_full(title, genres: list, overview, release_date, length, vote_average):
    return f'''<b>Название:</b> {title}
<i>{','.join(genres)}</i>
<b>Описание:</b>
<i>{overview}</i>
<b>Год выхода:</b> {release_date}
<b>Длительность:</b> {length} мин.
<b>Оценка:</b> {vote_average}'''


def movie_short(title, release_date, vote_average):
    return f'''<b>Название:</b> {title}
<b>Год выхода:</b> {release_date} 
<b>Оценка:</b> {vote_average}'''


def person_short(name, date_of_birth, films):
    return f'''<b>Имя:</b> {name}
<b>Год рождения:</b> {date_of_birth}
<i>{films}</i>'''
