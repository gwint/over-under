import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from math import exp

TEAM_STATISTICS_FILE = "/home/gregory/Projects/over-under/game_data/TeamStatistics.csv"
TEAM = "Heat"
BANDWIDTH_PARAMETER = 4

## Must calcualte weights matrix (n x n) for each point to be tested.
def _get_weights(training_df, test_pt, bandwidth_parameter):
    print(training_df)
    print(test_pt)
    print(training_df["halftimeScore"] - test_pt)
    weight_values = [exp(-(((x_i - test_pt)**2) / (2*(bandwidth_parameter**2)))) for x_i in training_df["halftimeScore"].to_list()]
    print(weight_values)
    weights_df = pd.DataFrame(np.diag(weight_values))
    return weights_df

def performLinearRegression(training_df, test_df):
    training_df_halftime_score_consolidated = training_df.assign(halftimeScore = training_df["q1Points"] + training_df["q2Points"])[["halftimeScore"]]
    training_df_halftime_score_consolidated["dummy"] = 1

    training_full_game_scores_only_df = training_df[["teamScore"]]

    ## Train linear regression model.
    model = LinearRegression().fit(training_df_halftime_score_consolidated, training_full_game_scores_only_df)
    print(model)
    print(f"Slope: {model.coef_[0][0]}")
    print(f"Intercept: {model.intercept_[0]}")

    slope = model.coef_[0][0]
    y_intercept = model.intercept_[0]

    test_df["estimatedScores"] = slope * test_df["halftimeScore"] + y_intercept
    print(test_df)
    for test_idx in range(len(test_df)):
        print("estimated full game score:", test_df.iloc[test_idx, 5])
        print("actual full game score:", test_df.iloc[test_idx, 2])

    ## Calculate mean squared error.
    print("MSE:", mean_squared_error(test_df[["estimatedScores"]], test_df[["teamScore"]]))
    return test_df["estimatedScores"].to_list(), test_df["teamScore"].to_list()


## Performs locally weighted linear regression based on data in input file.
def performLocallyWeightedLinearRegression(training_df, test_df):
    ## For each test vector, calculate parameters using closed form equation.
    ## Get proper matrices for closed form equation to calculate the parameters.
    training_df_halftime_score_consolidated = training_df.assign(halftimeScore = training_df["q1Points"] + training_df["q2Points"])[["halftimeScore"]]
    print(training_df_halftime_score_consolidated)

    training_final_scores_df = training_df[["teamScore"]]
    print(training_final_scores_df)

    ## Note: Scale down by a factor of 10 so that weights scale to 0 more smoothly.
    training_df["halftimeScore"] = training_df["q1Points"] + training_df["q2Points"]
    training_df["dummy"] = 1
    test_df["halftimeScore"] = test_df["q1Points"] + test_df["q2Points"]

    ## TODO: For each value in the test set, get the weights.
    test_df["weights_df"] = test_df["halftimeScore"].apply(lambda halftimeScore : _get_weights(training_df, halftimeScore, BANDWIDTH_PARAMETER))

    print(test_df["weights_df"].to_list())

    training_halftime_scores_only_df = training_df[["halftimeScore", "dummy"]]
    testing_halftime_scores_only_df = test_df[["halftimeScore"]]
    print(training_halftime_scores_only_df)
    print(testing_halftime_scores_only_df)

    training_full_game_scores_only_df = training_df[["teamScore"]]
    print(training_full_game_scores_only_df)

    print(test_df)

    real_full_game_scores = []
    estimated_full_game_scores = []

    for test_idx in range(len(test_df)):
        curr_test_pt_weights = test_df.iloc[test_idx, 4]
        #print("test pt weights shape:", curr_test_pt_weights.shape)
        #print("training data shape:", training_halftime_scores_only_df.T.shape)
        ##print(curr_test_pt_weights.transpose().dot(training_halftime_scores_only_df.values))
        rate_df = pd.DataFrame(np.linalg.inv(training_halftime_scores_only_df.transpose().dot(curr_test_pt_weights.values).dot(training_halftime_scores_only_df.values))).dot(training_halftime_scores_only_df.transpose().values).dot(curr_test_pt_weights.values).dot(training_full_game_scores_only_df.values)
        print(rate_df)
        y_intercept = rate_df.iloc[1, 0]
        slope = rate_df.iloc[0, 0]
        estimated_score = slope * test_df.iloc[test_idx, 3] + y_intercept
        actual_score = test_df.iloc[test_idx, 2]
        print("estimated full game score:", estimated_score)
        print("actual full game score:", actual_score)
        real_full_game_scores.append(actual_score)
        estimated_full_game_scores.append(estimated_score)

    print("MSE:", mean_squared_error(real_full_game_scores, estimated_full_game_scores))
    return real_full_game_scores, estimated_full_game_scores

if __name__ == "__main__":
    ## Read statistics file and pull out relevant rows, then break into training and test sets.
    data_df = pd.read_csv(TEAM_STATISTICS_FILE)
    data_df = data_df.dropna(subset=["q1Points", "q2Points"])
    ## Make sure game datetime field is a datetime.
    data_df["gameDateTimeEst"] = pd.to_datetime(data_df["gameDateTimeEst"])
    print(data_df[["gameDateTimeEst"]])
    recent_games_df = data_df[data_df["gameDateTimeEst"] > "2022-01-01"]
    print(recent_games_df.shape)
    ## Need to pull out data for a single team.
    team_specific_df = recent_games_df[recent_games_df["teamName"] == TEAM.title()]
    print(team_specific_df.shape)
    ## Split data into test and training sets.
    train_df, test_df = train_test_split(team_specific_df, test_size=0.4, random_state=42)
    train_df = train_df[["q1Points", "q2Points", "teamScore"]]
    test_df = test_df[["q1Points", "q2Points", "teamScore"]]
    print(train_df.shape)

    print(train_df)
    print(test_df)

    performLocallyWeightedLinearRegression(train_df, test_df)
    performLinearRegression(train_df, test_df)
