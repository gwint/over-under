import csv
import os
import pprint
import numpy as np
import pandas as pd
from sys import argv
from sklearn.model_selection import train_test_split
from pathlib import Path

SKIPPABLE_TEAMS = ["loong-lions", "phoenix", "jerusalem b.c.", "united"]

NBA_TEAMS_TO_CITIES = {
    "hawks": "atlanta",
    "celtics": "boston",
    "nets": "brooklyn",
    "hornets": "charlotte",
    "bulls": "chicago",
    "cavaliers": "cleveland",
    "mavericks": "dallas",
    "nuggets": "denver",
    "pistons": "detroit",
    "warriors": "golden state",
    "rockets": "houston",
    "pacers": "indiana",
    "clippers": "los angeles",
    "lakers": "los angeles",
    "grizzlies": "memphis",
    "heat": "miami",
    "bucks": "milwaukee",
    "timberwolves": "minnesota",
    "pelicans": "new orleans",
    "knicks": "new york",
    "thunder": "oklahoma city",
    "magic": "orlando",
    "76ers": "philadelphia",
    "suns": "phoenix",
    "trail blazers": "portland",
    "kings": "sacramento",
    "spurs": "san antonio",
    "raptors": "toronto",
    "jazz": "utah",
    "wizards": "washington"
}

NBA_TEAM_ACRONYMS = {
    'hawks': 'ATL',
    'celtics': 'BOS',
    'nets': 'BKN',
    'hornets': 'CHA',
    'bulls': 'CHI',
    'cavaliers': 'CLE',
    'mavericks': 'DAL',
    'nuggets': 'DEN',
    'pistons': 'DET',
    'warriors': 'GSW',
    'rockets': 'HOU',
    'pacers': 'IND',
    'clippers': 'LAC',
    'lakers': 'LAL',
    'grizzlies': 'MEM',
    'heat': 'MIA',
    'bucks': 'MIL',
    'timberwolves': 'MIN',
    'pelicans': 'NOP',
    'knicks': 'NYK',
    'thunder': 'OKC',
    'magic': 'ORL',
    '76ers': 'PHI',
    'suns': 'PHX',
    'trail blazers': 'POR',
    'kings': 'SAC',
    'spurs': 'SAS',
    'raptors': 'TOR',
    'jazz': 'UTA',
    'wizards': 'WAS'
}

def get_training_test_splits(all_data_file_name: str, team: str):
    data_df = pd.read_csv(all_data_file_name)
    data_df = data_df.dropna(subset=["q1Points", "q2Points"])
    ## Make sure game datetime field is a datetime.
    data_df["gameDateTimeEst"] = pd.to_datetime(data_df["gameDateTimeEst"])
    print(data_df[["gameDateTimeEst"]])
    recent_games_df = data_df[data_df["gameDateTimeEst"] > "2022-01-01"]
    print(recent_games_df.shape)
    ## Need to pull out data for a single team.
    team_specific_df = recent_games_df[recent_games_df["teamName"] == (team if team[0].isdigit() else team.title())]
    print(team_specific_df.shape)
    assert team_specific_df.shape[0] > 0, team.title() + " rows not found."
    ## Split data into test and training sets.
    train_df, test_df = train_test_split(team_specific_df, test_size=0.4, random_state=42)
    train_df = train_df[["q1Points", "q2Points", "teamScore"]]
    test_df = test_df[["q1Points", "q2Points", "teamScore"]]
    print(train_df.shape)

    print(train_df)
    print(test_df)

    return train_df, test_df

def get_clean_timestamp(timestamp: str): 
    return timestamp.split('.')[0] + "Z"

def get_halftime_timestamp(game_date, team_1_name, team_2_name, play_by_play_dir):
    play_by_play_directory_path = Path(play_by_play_dir)
    relevant_play_by_play_file = ""
    for item in play_by_play_directory_path.iterdir():
        if NBA_TEAM_ACRONYMS[team_1_name] in item.name and NBA_TEAM_ACRONYMS[team_2_name] in item.name and game_date in item.name:
            relevant_play_by_play_file = item.name
            break

    assert relevant_play_by_play_file
    with open(f"{play_by_play_dir}/{relevant_play_by_play_file}", 'r') as play_by_play:
        play_by_play_reader = csv.DictReader(play_by_play)
        end_of_period_count = 0
        for row in play_by_play_reader:
            event_type = row["event_type"]
            event_time = row["time_actual"]
            if event_type == "end of period":
                end_of_period_count += 1

                if end_of_period_count == 2:
                    return event_time
                    return get_clean_timestamp(event_time)

        raise Exception(f"Unable to find halftime in {play_by_play_dir}/{relevant_play_by_play_file}")

if __name__ == "__main__":
    play_by_play_dir = argv[1]
    game_date = "2025-10-21"
    team_1_name = "rockets"
    team_2_name = "thunder"
    print(get_halftime_timestamp(game_date, team_1_name, team_2_name, play_by_play_dir))