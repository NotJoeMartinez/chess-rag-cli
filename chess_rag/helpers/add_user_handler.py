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
        # self.check_db()
        # sys.exit(0)
        print(f"fetching user data")
        self.fetch_user_archives()
        

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

        now = datetime.datetime.now()
        today = now.strftime("%Y-%m-%d")
        fname = f"{self.username}_chess_com_{today}.json"
        
        with open(fname, "w") as f:
            json.dump(games_dict,f)

        print(f"Saved data from {self.username} to {fname}")


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
                    );

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
                );
                '''
            )

            conn.commit()