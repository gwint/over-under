import csv
import math
import pprint

GAME_RESULTS_FILE = "/home/gregory/Downloads/game_under_game_results.csv"
WEIGHTS_FILE = "calculated_weights.csv"

def main():
    per_team_weights = {}
    with open(WEIGHTS_FILE, 'r', newline='') as weights_file:
        weights_reader = csv.DictReader(weights_file)
        for team_weights in weights_reader:
            team_name = team_weights["team"]
            slope = float(team_weights[" slope"])
            y_intercept = float(team_weights[" yintercept"])

            per_team_weights[team_name] = {
                "slope": slope,
                "y_intercept": y_intercept
            }

        per_team_sum_squared_residuals = {}

        game_count = 0
        with open(GAME_RESULTS_FILE, 'r', newline='') as game_results_file:
            game_results_reader = csv.DictReader(game_results_file)
            for game_result in game_results_reader:
                team_1 = game_result["Team 1"]
                team_2 = game_result["Team 2"]
                team_1_score_calculated = float(game_result["Team 1 Score Calculated"])
                team_2_score_calculated = float(game_result["Team 2 Score Calculated"])
                team_1_score_actual = float(game_result["Team 1 Real Score"])
                team_2_score_actual = float(game_result["Team 2 Real Score"])

                if team_1 not in per_team_sum_squared_residuals:
                    per_team_sum_squared_residuals[team_1] = 0.0
                if team_2 not in per_team_sum_squared_residuals:
                    per_team_sum_squared_residuals[team_2] = 0.0

                per_team_sum_squared_residuals[team_1] += (team_1_score_calculated - team_1_score_actual) ** 2
                per_team_sum_squared_residuals[team_2] += (team_2_score_calculated - team_2_score_actual) ** 2
                game_count += 1

        for team in per_team_sum_squared_residuals:
            per_team_sum_squared_residuals[team] = math.sqrt(per_team_sum_squared_residuals[team] / game_count)

        pprint.pprint(per_team_sum_squared_residuals)

main()
