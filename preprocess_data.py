import csv
import pandas as pd

GAMES_DATA_PATH = "/home/gregory/Downloads/archive/TeamStatistics.csv"
PREPROCESSED_DATA_PATH = "preprocessed_data.csv"
TARGET_TEAM_ID = "1610612752" ## Knicks

PREPROCESSED_DATA_COLUMN_NAMES = ["firstHalfTotal", "totalTeamPoints"]

def main():
    with open(GAMES_DATA_PATH, 'r',  newline='') as games_data_file:
        with open(PREPROCESSED_DATA_PATH, 'w', newline='') as preprocessed_data_file:
            writer = csv.DictWriter(preprocessed_data_file, fieldnames=PREPROCESSED_DATA_COLUMN_NAMES)
            writer.writeheader()

            reader = csv.DictReader(games_data_file)

            for row in reader:
                if row["teamId"] == TARGET_TEAM_ID and row["q1Points"] and row["q2Points"]:
                    print(row["q1Points"], row["q2Points"], row["teamScore"])
                    writer.writerow({
                        "firstHalfTotal": float(row["q1Points"]) + float(row["q2Points"]),
                        "totalTeamPoints": float(row["teamScore"])
                    })

main()
