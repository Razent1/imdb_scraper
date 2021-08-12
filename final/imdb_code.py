from imdb_helper_functions import *


@retry(stop=stop_after_attempt(7))
def collect_nearest_actors(root_actor, num_of_movies_limit, num_of_actors_limit):
    if root_actor in cash:
        return cash[root_actor]
    if root_actor in seen_act.keys():
        return seen_act[root_actor]

    dis1 = []

    try:
        if root_actor in seen_name_mov.keys():
            film = seen_name_mov[root_actor]
        else:
            film = get_bs_na(root_actor)
            seen_name_mov[root_actor] = get_bs_na(root_actor)
        if root_actor in seen_name_act.keys():
            films = seen_name_act[root_actor]
        else:
            films = get_movies_by_actor_soup(film)
            seen_name_mov[root_actor] = get_movies_by_actor_soup(film)
    except AttributeError:
        return []

    if num_of_movies_limit is not None:
        films = films[:num_of_movies_limit]

    for film in films:
        if film[1] not in seen_mov.keys():
            film_link = get_bs_na(film[1] + 'fullcredits/')
            actor = get_actors_by_movie_soup(film_link)
            if num_of_actors_limit is not None:
                actor = actor[:num_of_actors_limit]
            seen_mov[film[1]] = actor

        for el in [el[1] for el in seen_mov[film[1]]]:
            dis1.append(el)

    seen_act[root_actor] = list(OrderedDict.fromkeys(dis1))
    return seen_act[root_actor]


@retry(stop=stop_after_attempt(7))
def save_data():
    actors_check = ['https://www.imdb.com/name/nm0262635/', 'https://www.imdb.com/name/nm1165110/',
                    'https://www.imdb.com/name/nm0425005/', 'https://www.imdb.com/name/nm0474774/',
                    'https://www.imdb.com/name/nm0000375/',
                    'https://www.imdb.com/name/nm0000329/', 'https://www.imdb.com/name/nm0177896/',
                    'https://www.imdb.com/name/nm0001191/', 'https://www.imdb.com/name/nm0424060/',
                    'https://www.imdb.com/name/nm0005527/',
                    ]

    res = {}
    for i in range(len(actors_check)):
        for actor in actors_check:
            if actors_check[i] not in res:
                res[actors_check[i]] = {}
            if actor != actors_check[i]:
                res[actors_check[i]].update({actor: get_movie_distance(actors_check[i], actor, 5, 5)})
    return res


def save_desc_to_file():
    actors_check = ['https://www.imdb.com/name/nm0262635/', 'https://www.imdb.com/name/nm1165110/',
                    'https://www.imdb.com/name/nm0425005/', 'https://www.imdb.com/name/nm0474774/',
                    'https://www.imdb.com/name/nm0000375/',
                    'https://www.imdb.com/name/nm0000329/', 'https://www.imdb.com/name/nm0177896/',
                    'https://www.imdb.com/name/nm0001191/', 'https://www.imdb.com/name/nm0424060/',
                    'https://www.imdb.com/name/nm0005527/',
                    ]
    for actor in actors_check:
        file = get_movie_descriptions_by_actor_soup(get_bs_na(actor))
        make_json(get_actor_name(actor)[0] + '.json', file)


def get_actors_by_movie_soup(cast_page_soup, num_of_actors_limit=None):
    actors_href = []

    cast_list = cast_page_soup.find('table', attrs={'class': 'cast_list'})
    cast_list = cast_list.find_all('tr')

    for td in cast_list:
        try:
            a = td.find_all('td')[1].find('a')
            actors_href.append((a.text.strip(), 'https://www.imdb.com' + a['href']))
        except IndexError:
            pass

    if num_of_actors_limit is not None:
        return actors_href[:num_of_actors_limit]
    return actors_href


def get_movies_by_actor_soup(actor_page_soup, num_of_movies_limit=None):
    res = []

    actor_head = actor_page_soup.find('div', attrs={'id': re.compile(r'filmo-head-actor|filmo-head-actress')})
    films = actor_head.find_next_sibling()
    films = films.find_all('div', attrs={'class': re.compile(r'filmo-row odd|filmo-row even')})

    for div in films_filter(films):
        a = div.find('a')
        res.append((a.text, 'https://www.imdb.com' + a['href']))

    if num_of_movies_limit is not None:
        return res[:num_of_movies_limit]
    return res


@retry(stop=stop_after_attempt(7))
def get_movie_distance(actor_start_url, actor_end_url, num_of_actors_limit=None, num_of_movies_limit=None):
    indentation_level = 1
    int_level = 1
    actor_start_url = make_url(actor_start_url)
    actor_end_url = make_url(actor_end_url)

    linked_actors = collect_nearest_actors(actor_start_url, num_of_movies_limit, num_of_actors_limit)
    while actor_end_url not in linked_actors[1:]:
        indentation_level += 1
        if indentation_level > int_level:
            make_json('cash.json', seen_mov)
            make_json('cash.json', seen_act)
            return math.inf

        new_linked_actors = []
        for actor in linked_actors:
            actor_link = collect_nearest_actors(actor, num_of_movies_limit, num_of_actors_limit)
            if actor_end_url in actor_link:
                make_json('cash.json', seen_mov)
                make_json('cash.json', seen_act)
                return indentation_level
            new_linked_actors += list(OrderedDict.fromkeys(actor_link))

        linked_actors = list(OrderedDict.fromkeys(new_linked_actors[1:]))
        print(linked_actors)
    make_json('cash.json', seen_mov)
    make_json('cash.json', seen_act)
    return indentation_level


def get_movie_descriptions_by_actor_soup(actor_page_soup):
    res = []

    films = get_movies_by_actor_soup(actor_page_soup)
    for film in films:
        description = get_bs_na(film[1])
        description = description.find('div', attrs={'class': re.compile(r'Hero__MetaContainer\w+')})
        description = description.find('span',
                                       attrs={'data-testid': 'plot-xl', 'class': re.compile(r'GenresAndPlot\w+')}).text
        res.append(description)
    return res
