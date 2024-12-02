import os
import datetime
import sys
import sqlite3
import sqlite_vec

class DBHandler:
    def __init__(self) -> None:
        self.init_db()

    def init_db(self):
        db_path = self.get_db_path()
        with sqlite3.connect(db_path) as conn:
            curr = conn.cursor()

            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            # vec_version, = conn.execute("select vec_version()").fetchone()
            # print(f"vec_version={vec_version}")


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



    def add_or_update_user(self, username):

        db_path = self.get_db_path()

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
    

    def get_users(self):

        db_path = self.get_db_path()
        with sqlite3.connect(db_path) as conn:
            curr = conn.cursor()
            curr.execute(
                '''
                SELECT * FROM users
                '''
            )

            return curr.fetchall()
