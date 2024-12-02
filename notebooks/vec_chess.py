import sqlite3
import sys
import sqlite_vec
import struct

from openai import OpenAI
from typing import List
from utils import add_or_update_user, fetch_user_archives

USERNAME = 'notjoemartinez'
DB_PATH = 'chess.db'

def main():

    if len(sys.argv) < 2:
        print("Usage: python vec_chess.py init|search")
        sys.exit(1)
    
    command = sys.argv[1]
    if command == 'init':
        init()
    elif command == 'search':
        if len(sys.argv) < 3:
            print("Usage: python vec_chess.py search <query>")
            sys.exit(1)
        query = sys.argv[2]
        search(query)
    else:
        print("Usage: python vec_chess.py init|search")
        sys.exit(1)

def init():
    init_db()
    add_or_update_user(username=USERNAME, db_path=DB_PATH)
    print("Fetching user archives")
    fetch_user_archives(username=USERNAME, db_path=DB_PATH)
    print("Adding embeddings")
    add_embeddings()


def search(query):
    search_db(query)

def init_db():
    # init db
    with sqlite3.connect(DB_PATH) as conn:
        curr = conn.cursor()
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        
        # basic schema
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

        curr.execute(
        """
            CREATE VIRTUAL TABLE pgn_embeddings USING vec0(
                url TEXT PRIMARY KEY UNIQUE,
                pgn_embedding FLOAT[1536]
            );
        """
        )

        conn.commit()


def add_embeddings():
    username = USERNAME
    with sqlite3.connect(DB_PATH) as conn:
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        
        curr = conn.cursor()

        curr.execute(
            """
            SELECT url, pgn FROM games
            WHERE white_username = ? OR black_username = ?
            """, (username, username)
        )
        
        games = curr.fetchall()

        for url, pgn in games:
            print(url)
            pgn_embedding = get_embedding(pgn)
            curr.execute(
                    "INSERT OR IGNORE INTO pgn_embeddings(url, pgn_embedding) VALUES(?, ?)",
                    [url, serialize(pgn_embedding)],
                )


def search_db(query):

    query_embedding = get_embedding(query)

    with sqlite3.connect(DB_PATH) as db:
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        db.enable_load_extension(False)

        results = db.execute(
            """
            SELECT
                pgn_embeddings.url,
                distance,
                pgn 
            FROM pgn_embeddings 
            LEFT JOIN games ON games.url = pgn_embeddings.url
            WHERE pgn_embedding MATCH ?
                AND k = 3
            ORDER BY distance
            """,
            [serialize(query_embedding)],
        ).fetchall()

        for row in results:
            print(row)


def serialize(vector: List[float]) -> bytes:
    """serializes a list of floats into a compact "raw bytes" format"""
    return struct.pack("%sf" % len(vector), *vector)


def get_embedding(text, model="text-embedding-3-small"):

    client = OpenAI()
    text_embedding = client.embeddings.create(input=[text], model=model).data[0].embedding

    return text_embedding



if __name__ == '__main__':
    main()