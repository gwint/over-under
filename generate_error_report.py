import csv
import math
import pprint
import sys

from sklearn.metrics import root_mean_squared_error
from utils import get_training_test_splits, SKIPPABLE_TEAMS, NBA_TEAM_ACRONYMS
from locally_weighted_linear_regression import performLocallyWeightedLinearRegression, performLinearRegression

def main():
    algorithm_type = sys.argv[1]
    game_results_file_path = sys.argv[2]
    testing_data_file_path = sys.argv[3]

    if algorithm_type == "lr":
        weights_file_path = sys.argv[4]
        error_report_file = sys.argv[5]

        per_team_weights = {}
        with open(weights_file_path, 'r', newline='') as weights_file:
            weights_reader = csv.DictReader(weights_file)
            for team_weights in weights_reader:
                team_name = team_weights["name"]
                slope = float(team_weights["slope"])
                y_intercept = float(team_weights["y-intercept"])

                per_team_weights[team_name.lower().strip()] = {
                    "slope": slope,
                    "y_intercept": y_intercept
                }

        per_team_library_rmse_values = {}

        per_team_game_count = {}
        with open(game_results_file_path, 'r', newline='') as game_results_file:
            game_results_reader = csv.DictReader(game_results_file)

            for game_result in game_results_reader:
                team_1 = game_result["teamName"].lower().strip()
                if team_1 in SKIPPABLE_TEAMS:
                    continue

                q1_points = game_result.get("q1Points", 0)
                q2_points = game_result.get("q2Points", 0)
                if not (q1_points and q2_points):
                    continue

                team_1_first_half_points = float(game_result.get("q1Points", 0)) + float(game_result.get("q2Points", 0))
                slope, y_intercept = per_team_weights[team_1]["slope"], per_team_weights[team_1]["y_intercept"]

                team_1_score_calculated = slope * team_1_first_half_points + y_intercept
                team_1_score_actual = float(game_result["teamScore"])

                if team_1 not in per_team_library_rmse_values:
                    per_team_library_rmse_values[team_1] = {"pred": [], "actual": []}
                per_team_library_rmse_values[team_1]["pred"].append(team_1_score_calculated)
                per_team_library_rmse_values[team_1]["actual"].append(team_1_score_actual)

        for team in per_team_library_rmse_values:
            print(team, root_mean_squared_error(per_team_library_rmse_values[team]["actual"], per_team_library_rmse_values[team]["pred"]))

        assert(len(per_team_library_rmse_values) == 30)

        with open(error_report_file, 'w', newline='') as library_rmse_values_file:
            fieldnames = ["teamName", "rmse"]
            writer = csv.DictWriter(library_rmse_values_file, fieldnames=fieldnames)
            writer.writeheader()

            for team in per_team_library_rmse_values:
                rmse_value = root_mean_squared_error(per_team_library_rmse_values[team]["actual"], per_team_library_rmse_values[team]["pred"])
                writer.writerow({
                    "teamName": team,
                    "rmse": rmse_value
                })

    elif algorithm_type == "lwlr":
        error_report_file = sys.argv[4]
        with open(error_report_file, 'w', newline='') as error_report_csv:
            fieldnames = ["teamName", "rmse"]
            writer = csv.DictWriter(error_report_csv, fieldnames=fieldnames)
            writer.writeheader()

            for team in NBA_TEAM_ACRONYMS.keys():
                print(f"Performing locally weighted linear regression for {team}...")
                train_df, test_df = get_training_test_splits(game_results_file_path, team)
                real_full_game_scores, estimated_full_game_scores = performLocallyWeightedLinearRegression(train_df, test_df)
                rmse_value = root_mean_squared_error(real_full_game_scores, estimated_full_game_scores)
                writer.writerow({
                    "teamName": team,
                    "rmse": rmse_value
                })

    elif algorithm_type == "both":
        weights_file_path = sys.argv[4]
        error_report_file = sys.argv[5]

        with open(error_report_file, 'w', newline='') as error_report_csv:
            fieldnames = ["teamName", "rmse_lwlr", "rmse_lr"]
            writer = csv.DictWriter(error_report_csv, fieldnames=fieldnames)
            writer.writeheader()

            for team in NBA_TEAM_ACRONYMS.keys():
                print(f"Performing locally weighted linear regression for {team}...")
                train_df, test_df = get_training_test_splits(game_results_file_path, team)

                real_full_game_scores_lwlr, estimated_full_game_scores_lwlr = performLocallyWeightedLinearRegression(train_df, test_df)
                rmse_value_lwlr = root_mean_squared_error(real_full_game_scores_lwlr, estimated_full_game_scores_lwlr)

                real_full_game_scores_lr, estimated_full_game_scores_lr = performLinearRegression(train_df, test_df)
                rmse_value_lr = root_mean_squared_error(real_full_game_scores_lr, estimated_full_game_scores_lr)

                writer.writerow({
                    "teamName": team,
                    "rmse_lwlr": rmse_value_lwlr,
                    "rmse_lr": rmse_value_lr
                })

    else:
        raise Exception(f"Unsupported algorithm type: {algorithm_type}")

main()
