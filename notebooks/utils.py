import sys
import re
import json
import sqlite3
import datetime
import requests


DEV_HEADERS = {
    'User-Agent': 'chess-rag-cli (https://github.com/NotJoeMartinez/chess-rag-cli)'
}


def add_or_update_user(username, db_path):

    with sqlite3.connect(db_path) as conn:
        curr = conn.cursor()

        curr.execute(
            '''
            SELECT * FROM users WHERE username = ?
            ''',
            (username,)
        )

        user = curr.fetchone()

        if user is None:
            curr.execute(
                '''
                INSERT INTO users (username, last_updated) VALUES (?, ?)
                ''',
                (username, datetime.datetime.now())
            )

            conn.commit()   
            print(f"Added {username} to the database")
        else:
            curr.execute(
                '''
                UPDATE users SET last_updated = ? WHERE username = ?
                ''',
                (datetime.datetime.now(), username)
            )
            print(f"Updating {username}")


def fetch_user_archives(username, db_path):
    archive_url = f"https://api.chess.com/pub/player/{username}/games/archives"
    r = requests.get(url=archive_url, headers=DEV_HEADERS)
    month_urls = r.json()

    games_dict = {}

    for url in month_urls["archives"]:
        res = requests.get(url=url, headers=DEV_HEADERS).json()
        match = re.search(r"games\/(\d{4})\/(\d{2})$",url)
        year = match.group(1)
        month = match.group(2)
        games_dict[year] = []

    for url in month_urls["archives"]:
        match = re.search(r"games\/(\d{4})\/(\d{2})$",url)
        year = match.group(1)
        month = match.group(2)
        res = requests.get(url=url, headers=DEV_HEADERS).json()
        games_dict[year].append({month:res})

    insert_archives(games_dict, db_path)


def insert_archives(data, db_path):
    
    extracted_games = []

    for year in data.keys():
        months_lst = data[year]
        for month_dict in months_lst:
            for month in month_dict:
                games_dict = month_dict[month]
                for games in games_dict:
                    for game in games_dict[games]:
                        extracted_games.append(game)


    print('Inserting games into database...')


    with sqlite3.connect(db_path) as conn:
        for game in extracted_games:

            # handle missing keys 'accuracies'
            if 'accuracies' not in game:
                accuracies_white = None
                accuracies_black = None
            else:
                accuracies_white = game['accuracies']['white']
                accuracies_black = game['accuracies']['black']

            curr = conn.cursor()
            curr.execute(
                '''
                INSERT OR IGNORE INTO games (
                    url,
                    pgn,
                    time_control,
                    end_time,
                    rated,
                    accuracies_white,
                    accuracies_black,
                    tcn,
                    uuid,
                    initial_setup,
                    fen,
                    time_class,
                    rules,
                    white_rating,
                    white_result,
                    white_username,
                    white_uuid,
                    black_rating,
                    black_result,
                    black_username,
                    black_uuid,
                    eco
                ) VALUES (
                    :url,
                    :pgn,
                    :time_control,
                    :end_time,
                    :rated,
                    :accuracies_white,
                    :accuracies_black,
                    :tcn,
                    :uuid,
                    :initial_setup,
                    :fen,
                    :time_class,
                    :rules,
                    :white_rating,
                    :white_result,
                    :white_username,
                    :white_uuid,
                    :black_rating,
                    :black_result,
                    :black_username,
                    :black_uuid,
                    :eco
                )
                ''',
                {
                    'url': game['url'],
                    'pgn': game['pgn'],
                    'time_control': game['time_control'],
                    'end_time': unix_epoch_to_datetime(game['end_time']),
                    'rated': game['rated'],
                    'accuracies_white': accuracies_white, 
                    'accuracies_black': accuracies_black, 
                    'tcn': game['tcn'],
                    'uuid': game['uuid'],
                    'initial_setup': game['initial_setup'],
                    'fen': game['fen'],
                    'time_class': game['time_class'],
                    'rules': game['rules'],
                    'white_rating': game['white']['rating'],
                    'white_result': game['white']['result'],
                    'white_username': game['white']['username'],
                    'white_uuid': game['white']['uuid'],
                    'black_rating': game['black']['rating'],
                    'black_result': game['black']['result'],
                    'black_username': game['black']['username'],
                    'black_uuid': game['black']['uuid'],
                    'eco': game['eco']
                }
            )
            conn.commit()


# YYYY-MM-DD HH:MM:SS
def unix_epoch_to_datetime( unix_epoch):
    return datetime.datetime.fromtimestamp(unix_epoch)
