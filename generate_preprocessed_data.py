import csv
import pandas as pd

GAMES_DATA_PATH = "/home/gregory/Downloads/archive/TeamStatistics.csv"
PREPROCESSED_DATA_COLUMN_NAMES = ["firstHalfTotal", "totalTeamPoints"]

def main():
    per_team_row_data = {}

    print("Iterating through all team statistics...")
    with open(GAMES_DATA_PATH, 'r',  newline='') as games_data_file: 
        reader = csv.DictReader(games_data_file)

        for row in reader:
            team_id: str = row["teamId"]
            team_name: str = row["teamName"] 
            
            if row["q1Points"] and row["q2Points"]:
                if team_id not in per_team_row_data:
                    per_team_row_data[team_id] = {"name": team_name, "rows": []}

                print(row["q1Points"], row["q2Points"], row["teamScore"])
                per_team_row_data[team_id]["rows"].append({
                    "q1_points": row["q1Points"],
                    "q2_points": row["q2Points"],
                    "total_team_points": row["teamScore"]
                }) 

    print("Done iterating through team stats and now creating per team files...")

    print(len(per_team_row_data))
    for k in per_team_row_data:
        print(per_team_row_data[k]["name"])
        print(per_team_row_data[k]["rows"])

    for team_id in per_team_row_data:
        print(f"Creating per team preprocessed data sheets for {per_team_row_data[team_id]['name'].lower()}...")
        preprocessed_team_data_file_name = f"preprocessed_data_{per_team_row_data[team_id]['name'].lower()}.csv"
        with open(preprocessed_team_data_file_name, 'w', newline='') as preprocessed_team_data_file:
            writer = csv.DictWriter(preprocessed_team_data_file, fieldnames=PREPROCESSED_DATA_COLUMN_NAMES)
            writer.writeheader()

            team_specific_rows = per_team_row_data[team_id]["rows"]
            for row_data in team_specific_rows:
                print(float(row_data["q1_points"]) + float(row_data["q2_points"]))
                print(float(row_data["total_team_points"]))
                
                writer.writerow({
                    "firstHalfTotal": float(row_data["q1_points"]) + float(row_data["q2_points"]),
                    "totalTeamPoints": float(row_data["total_team_points"])
                })
                



main()
