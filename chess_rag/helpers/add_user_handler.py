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
        sys.exit(0)
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
        self.get_or_init_db()
        # check the database for the user
        # if the user exists update the archive with any new data

        # get or init db
        pass

    def get_or_init_db(self): 
        config_path = self.get_config_path()
        print(f"config_path: {config_path}")
    

    def get_config_path(self):
        platform = sys.platform

        if platform == 'win32':
            config_path = os.path.join(os.getenv('APPDATA'), 'chess-rag')
            if not os.path.exists(config_path):
                return self.make_config_dir() 
            else:
                return config_path 

        elif platform == 'darwin' or platform == 'linux':
            config_path = os.path.join(os.getenv('HOME'), '.config', 'chess-rag')
            if not os.path.exists(config_path):
                return self.make_config_dir()
            else:
                return config_path

        else:
            print("Error: Failed to configure db:")
            sys.exit(1)


    def make_config_dir(self):
        platform = sys.platform
        try:
            if platform == 'win32':
                config_path = os.path.join(os.getenv('APPDATA'), 'chess-rag')
                # check if config dir exists
                if not os.path.exists(config_path):
                    os.mkdir(config_path)
                    return config_path
            
            if platform == 'darwin' or platform == 'linux':
                config_path = os.path.join(os.getenv('HOME'), '.config', 'chess-rag')
                # check if config dir exists
                if not os.path.exists(config_path):
                    os.mkdir(config_path)
                    return config_path
        except Exception as e:
            print(e)
            sys.exit(1)
