import csv

WEIGHTS_FILE = "calculated_weights.csv"
TESTING_GAME_DATA_FILE = "/home/gregory/Downloads/archive/GameDataForTesting.csv"

def main():
    ## TODO: For each game, use the weights to calculate the estimated scores for each team, and
    ## write that along with the real scores to a spreadsheet (get column names from the other sheet)

    per_team_weights = {}
    with open(WEIGHTS_FILE, 'r', newline='') as weights_file:
        weights_reader = csv.DictReader(weights_file)
        for team_weights in weights_reader:
            team_name = team_weights["team"]
            slope = float(team_weights[" slope"])
            y_intercept = float(team_weights[" yintercept"])

            per_team_weights[team_name.strip()] = {
                "slope": slope,
                "y_intercept": y_intercept
            }

        with open(TESTING_GAME_DATA_FILE, 'r', newline='') as testing_data_file:
            testing_data_reader = csv.DictReader(testing_data_file)
            for testing_data in testing_data_reader:
                q1Points = float(testing_data["q1Points"])
                q2Points = float(testing_data["q2Points"])
                team_name = testing_data["teamName"].lower().strip()
                
                slope = float(per_team_weights[team_name]["slope"])
                y_intercept = float(per_team_weights[team_name]["y_intercept"])

                estimated_total = slope * (q1Points + q2Points) + y_intercept

                print(testing_data["teamName"], testing_data["teamScore"], estimated_total, testing_data["q1Points"], testing_data["q2Points"])

main()
