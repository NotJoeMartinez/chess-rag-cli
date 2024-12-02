import sys
import re
import json
import sqlite3
import os
from pprint import pprint
import datetime
import requests

class AddUserHandler:
    def __init__(self, username):
        self.headers = {
            'User-Agent': 'chess-rag-cli (https://github.com/NotJoeMartinez/chess-rag-cli)'
        }
        self.username = username


    def run(self):
        self.validate_username()
        self.check_db()
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

        for url in month_urls["archives"]:
            res = requests.get(url=url, headers=self.headers).json()
            match = re.search(r"games\/(\d{4})\/(\d{2})$",url)
            year = match.group(1)
            month = match.group(2)
            games_dict[year] = []

        for url in month_urls["archives"]:
            match = re.search(r"games\/(\d{4})\/(\d{2})$",url)
            year = match.group(1)
            month = match.group(2)
            res = requests.get(url=url, headers=self.headers).json()
            games_dict[year].append({month:res})

        self.get_game_archive(games_dict)
        # now = datetime.datetime.now()
        # today = now.strftime("%Y-%m-%d")
        # fname = f"{self.username}_chess_com_{today}.json"
        
        # with open(fname, "w") as f:
        #     json.dump(games_dict,f)

        # print(f"Saved data from {self.username} to {fname}")


    def get_game_archive(self, data):
        
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
        db_path = self.get_db_path()
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

    def check_db(self):

        # check the database for the user
        # if the user exists update the archive with any new data
        # get or init db
        db_path = self.get_db_path()
        self.init_db(db_path)

        with sqlite3.connect(db_path) as conn:
            curr = conn.cursor()

            curr.execute(
                '''
                SELECT * FROM users WHERE username = ?
                ''',
                (self.username,)
            )

            user = curr.fetchone()

            if user is None:
                curr.execute(
                    '''
                    INSERT INTO users (username, last_updated) VALUES (?, ?)
                    ''',
                    (self.username, datetime.datetime.now())
                )

                conn.commit()   
                print(f"Added {self.username} to the database")
            else:
                curr.execute(
                    '''
                    UPDATE users SET last_updated = ? WHERE username = ?
                    ''',
                    (datetime.datetime.now(), self.username)
                )
                print(f"Updating {self.username}")
        
    def get_db_path(self):
        platform = sys.platform

        try:
            if platform == 'win32':
                config_path = os.path.join(os.getenv('APPDATA'), 'chess-rag')
            elif platform == 'darwin' or platform == 'linux':
                config_path = os.path.join(os.getenv('HOME'), '.config', 'chess-rag')
            else:
                print("Error: Unsupported platform")
                sys.exit(1)

            if not os.path.exists(config_path):
                os.makedirs(config_path) 

            return os.path.join(config_path, 'game-data.db')

        except Exception as e:
            print(f"Error: Failed to configure db: {e}")
            sys.exit(1)
    
    
    def init_db(self, db_path):
        with sqlite3.connect(db_path) as conn:
            curr = conn.cursor()

            curr.execute(
                '''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT UNIQUE, 
                    last_updated TEXT
                    )


                '''
            )

            curr.execute(
                '''
                CREATE TABLE IF NOT EXISTS games (
                    url TEXT UNIQUE,
                    pgn TEXT,
                    time_control TEXT,
                    end_time TEXT,
                    rated TEXT,
                    accuracies_white REAL,
                    accuracies_black REAL,
                    tcn TEXT,
                    uuid TEXT,
                    initial_setup TEXT,
                    fen TEXT,
                    time_class TEXT,
                    rules TEXT,
                    white_rating INTEGER,
                    white_result TEXT,
                    white_username TEXT,
                    white_uuid TEXT,
                    black_rating INTEGER,
                    black_result TEXT,
                    black_username TEXT,
                    black_uuid TEXT,
                    eco TEXT 
                )
                '''
            )

            conn.commit()