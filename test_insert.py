import json
import datetime
import sqlite3

from pprint import pprint

def main():
    get_game_archive()


def get_game_archive():
    data_path = '.scratch/nowhere2b_chess_com_2024-12-01.json'

    with open(data_path, 'r') as f:
        data = json.load(f)
    
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
    with sqlite3.connect('test.db') as conn:
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
def unix_epoch_to_datetime(unix_epoch):
    return datetime.datetime.fromtimestamp(unix_epoch)

if __name__ == '__main__':
    main()