import sys
import re
import json
import sqlite3
import os
import datetime
import requests


from pprint import pprint

from chess_rag.helpers.db_handler import DBHandler

class AddUserHandler:
    def __init__(self, username):
        self.headers = {
            'User-Agent': 'chess-rag-cli (https://github.com/NotJoeMartinez/chess-rag-cli)'
        }
        self.username = username


    def run(self):

        self.validate_username()
        db = DBHandler()
        db.init_db()
        print("Checking database for user...")
        db.add_or_update_user(self.username)
        print(f"fetching user data")
        self.fetch_user_archives()
        print(f"Added {self.username} to the database")
        

    def validate_username(self):
        username = self.username
        user_url = f'https://api.chess.com/pub/player/{username}'

        res = requests.get(url=user_url, headers=self.headers)

        if res.status_code != 200:
            print(f"Error getting user: {res.status_code}")
            sys.exit(1)
    

    def fetch_user_archives(self):
        archive_url = f"https://api.chess.com/pub/player/{self.username}/games/archives"
        r = requests.get(url=archive_url, headers=self.headers)
        month_urls = r.json()

        games_dict = {}

        len_archives = len(month_urls["archives"])
        count = 0

        for url in month_urls["archives"]:
            res = requests.get(url=url, headers=self.headers).json()
            match = re.search(r"games\/(\d{4})\/(\d{2})$",url)
            year = match.group(1)
            month = match.group(2)
            games_dict[year] = []
            print(f"Fetching games for {year}-{month} ({count}/{len_archives})")

        for url in month_urls["archives"]:
            match = re.search(r"games\/(\d{4})\/(\d{2})$",url)
            year = match.group(1)
            month = match.group(2)
            res = requests.get(url=url, headers=self.headers).json()
            games_dict[year].append({month:res})

        self.insert_archives(games_dict)


    def insert_archives(self, data):
        
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

        db_path = DBHandler().get_db_path() 

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
                        'end_time': self.unix_epoch_to_datetime(game['end_time']),
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
    def unix_epoch_to_datetime(self, unix_epoch):
        return datetime.datetime.fromtimestamp(unix_epoch)
