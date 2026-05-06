import matplotlib.pyplot as plt
import numpy as np

import csv
import pandas as pd
import os

PREPROCESSED_DATA_DIR = "preprocessed_data"

def main():
    root, dirs, files = next(os.walk(PREPROCESSED_DATA_DIR))
    for file_name in files:
        halftime_team_pts = []
        total_game_team_pts = []
        with open(f"{PREPROCESSED_DATA_DIR}/{file_name}", 'r', newline='') as preprocessed_data_file:
            reader = csv.DictReader(preprocessed_data_file)
            for row in reader:
                first_half_pts = row["firstHalfTotal"]
                total_pts = row["totalTeamPoints"]

                halftime_team_pts.append(float(first_half_pts))
                total_game_team_pts.append(float(total_pts))

        print(halftime_team_pts)
        print(len(total_game_team_pts))

        assert len(halftime_team_pts) == len(total_game_team_pts)

        if not halftime_team_pts:
            continue

        ## TODO: Get the model parameters for the team given thier data.
        slope, y_intercept = np.polyfit(halftime_team_pts, total_game_team_pts, deg = 1)

        xseq = np.linspace(0, 80, num=100)
        print(xseq)
        plt.plot(xseq, y_intercept + slope * xseq, color="k", lw=2.5)

        plt.scatter(halftime_team_pts, total_game_team_pts, marker = 'x')
        graph_title = ''.join(file_name.replace('.csv', '').split('_')[-1]) + ' points at halftime vs. full game'
        plt.title(graph_title)
        plt.xlabel("halftime points")
        plt.ylabel("total game points")
        plt.xlim(40, 80)
        plt.ylim(90, 140)
        plt.savefig(f"visualization/pts_visualized/{graph_title}.png")

        plt.close()

main()
