import csv
import pandas as pd
import sys

PREPROCESSED_DATA_COLUMN_NAMES = ["firstHalfTotal", "totalTeamPoints"]

def main():
    game_data_file_path = sys.argv[1]
    target_directory = sys.argv[2]

    per_team_row_data = {}

    with open(game_data_file_path, 'r',  newline='') as games_data_file: 
        reader = csv.DictReader(games_data_file)

        for row in reader:
            team_id: str = row["teamId"]
            team_name: str = row["teamName"] 
            
            if row["q1Points"] and row["q2Points"]:
                if team_id not in per_team_row_data:
                    per_team_row_data[team_id] = {"name": team_name, "rows": []}

                per_team_row_data[team_id]["rows"].append({
                    "q1_points": row["q1Points"],
                    "q2_points": row["q2Points"],
                    "total_team_points": row["teamScore"]
                }) 

    for team_id in per_team_row_data:
        preprocessed_team_data_file_name = f"{target_directory}/preprocessed_data_{per_team_row_data[team_id]['name'].lower()}.csv"
        with open(preprocessed_team_data_file_name, 'w', newline='') as preprocessed_team_data_file:
            writer = csv.DictWriter(preprocessed_team_data_file, fieldnames=PREPROCESSED_DATA_COLUMN_NAMES)
            writer.writeheader()

            team_specific_rows = per_team_row_data[team_id]["rows"]
            for row_data in team_specific_rows:
                writer.writerow({
                    "firstHalfTotal": float(row_data["q1_points"]) + float(row_data["q2_points"]),
                    "totalTeamPoints": float(row_data["total_team_points"])
                })

main()
