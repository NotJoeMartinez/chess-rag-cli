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