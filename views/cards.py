def full(title, genres: list, overview, release_date, length, vote_average):
    return f'''<b>Название:</b> {title}
<i>{','.join(genres)}</i>
<b>Описание:</b>
<i>{overview}</i>
<b>Год выхода:</b> {release_date}
<b>Длительность:</b> {length} мин.
<b>Оценка:</b> {vote_average}'''


def short(title, overview, release_date, vote_average):
    return f'''<b>Название:</b> {title}
<b>Описание:</b>
<i>{overview}</i>
<b>Год выхода:</b> {release_date} 
<b>Оценка:</b> {vote_average}'''
