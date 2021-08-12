from bs4 import BeautifulSoup
import requests
import re
import json
import json
import networkx as nx
import matplotlib.pyplot as plt
from tenacity import retry, stop_after_attempt
import math
from collections import OrderedDict
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import re
import csv
import io
import pandas as pd
import numpy as np

"""global variables for cashing data"""
seen_mov = dict()
seen_act = dict()
seen_name_mov = dict()
seen_name_act = dict()


def films_filter(films):
    filtered_films = []
    is_omitted = 0
    omitted = ["TV Series", "Short", "Video Game", "Video short", "Video", "TV Movie", "TV Mini Series",
               "TV Series short", "TV Special"]

    for el in films:
        for val in omitted:
            if re.findall(val, el.text):
                is_omitted = 1
                break
        if el.find_all('a', attrs={'class': 'in_production'}) or is_omitted:
            is_omitted = 0
            continue
        filtered_films.append(el)

    return filtered_films


def cashing():
    try:
        with open('cash.json', 'r') as f:
            return json.load(f)
    except:
        return {}


cash = cashing()


def get_actor_name(url):
    soup = get_bs_na(url)
    name = soup.find('span', attrs={'class': 'itemprop'})
    return name.text, url


def get_bs_na(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def make_json(file_name, dump_file):
    with open(file_name, 'w', encoding='utf-8') as fp:
        json.dump(dump_file, fp)


def make_url(url):
    try:
        res = re.search(r'^https?:\/\/www\.(.*)$', url).group(1).rsplit('/', 1)[0]
    except AttributeError:
        res = url

    if res[len(res) - 1] != '/':
        res += '/'
    res = 'https://www.' + res
    return res


def convert_data_to_graph(data):
    res = {}
    for val in data:
        # if val in data[val]:
            # data[val].pop(val, None)
        res[get_actor_name(val)[0]] = data[val]
    make_json('graph.json', res)


def make_csv():
    with open('full_dct.json', 'r') as f:
        dct = json.load(f)
    df = pd.DataFrame(dct)
    print(df)
    df.to_csv('res.csv')


def give_names():
    full_dct = {}
    with open('graph.json', 'r') as f:
        dct = json.load(f)

    for val in dct:
        if val in dct[val]:
            dct[val].pop(val, None)
        full_dct[val] = {get_actor_name(el)[0]: dct[val][el] for el in dct[val]}
    make_json('full_dct.json', full_dct)
    print(full_dct)


def creating_graph():
    """For loading data I have used this code"""
    dct_names = {}
    dct_val = {}

    with open('graph.json', 'r') as f:
        dct = json.load(f)
    for val in dct:
        if val in dct[val]:
            dct[val].pop(val, None)
        dct_names[val] = [get_actor_name(el)[0] for el in list(dct[val].keys())]
        dct_val[val] = [el for el in list(dct[val].values())]
    make_json('dct_values3.json', dct_val)
    make_json('dct_name3.json', dct_names)


    with open('dct_name3.json', 'r', encoding='utf-8') as f:
        dct = json.load(f)
    with open('dct_values3.json', 'r', encoding='utf-8') as f:
        dct_val = json.load(f)

    G = nx.Graph()
    G.add_nodes_from(list(dct.keys()))
    labels = {}
    for val in dct:
        for indx, name in enumerate(dct[val]):
            if dct_val[val][indx] == 1:
                G.add_edge(val, name, color='green', label='1')
            elif dct_val[val][indx] == 2:
                G.add_edge(val, name, color='blue', label='2')
            elif dct_val[val][indx] == 3:
                G.add_edge(val, name, color='red', label='3')
            labels[name] = name
    edges = G.edges()
    pos = nx.circular_layout(G)
    print(edges)
    colors = [G[u][v]['color'] for u, v in edges]
    plt.figure(figsize=(8, 8))
    plt.axis('off')
    nx.draw_networkx(G, pos, edges=edges, edge_color=colors, with_labels=True, labels=labels, node_size=1000,
                     font_size=8)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'label'))
    plt.show()
creating_graph()