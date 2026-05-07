import matplotlib.pyplot as plt
import numpy as np

import csv
import pandas as pd
import os
import shutil
import sys

def main():
    preprocessed_data_dir = sys.argv[1]
    target_dir = sys.argv[2]

    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir, exist_ok=True)
    root, dirs, files = next(os.walk(preprocessed_data_dir))
    for file_name in files:
        halftime_team_pts = []
        total_game_team_pts = []
        with open(f"{preprocessed_data_dir}/{file_name}", 'r', newline='') as preprocessed_data_file:
            reader = csv.DictReader(preprocessed_data_file)
            for row in reader:
                first_half_pts = row["firstHalfTotal"]
                total_pts = row["totalTeamPoints"]

                halftime_team_pts.append(float(first_half_pts))
                total_game_team_pts.append(float(total_pts))

        assert len(halftime_team_pts) == len(total_game_team_pts)

        if not halftime_team_pts:
            continue

        ## TODO: Get the model parameters for the team given thier data.
        #slope, y_intercept = np.polyfit(halftime_team_pts, total_game_team_pts, deg = 1)
        #xseq = np.linspace(0, 80, num=100)
        # print(xseq)
        # plt.plot(xseq, y_intercept + slope * xseq, color="k", lw=2.5)

        plt.scatter(halftime_team_pts, total_game_team_pts, marker = 'x')
        graph_title = ''.join(file_name.replace('.csv', '').split('_')[-1]) + ' points at halftime vs. full game'
        plt.title(graph_title)
        plt.xlabel("halftime points")
        plt.ylabel("total game points")
        plt.xlim(40, 80)
        plt.ylim(90, 140)
        plt.savefig(f"{target_dir}/{graph_title}.png")

        plt.close()

main()
