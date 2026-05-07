import pandas as pd
import numpy as np
import csv
import os
import sys

LEARNING_RATE = 0.000003
NUM_TRAINING_EPOCHS = 9000

def get_model_output(slope, y_intercept, single_input_data):
    return (float(slope) * float(single_input_data)) + float(y_intercept)

def get_weights_from_library(data):
    return np.polyfit(data["firstHalfTotal"], data["totalTeamPoints"], 1)

def get_updated_weights(current_slope: float, current_y_intercept: float, data):
    ## Update weights using gradient descent.
    updated_slope = current_slope - (LEARNING_RATE * sum([data.loc[i, "firstHalfTotal"] * (get_model_output(current_slope, current_y_intercept, data.loc[i, "firstHalfTotal"]) - data.loc[i, "totalTeamPoints"]) for i in range(data.shape[0])]))

    updated_y_intercept = current_y_intercept - (LEARNING_RATE * sum([get_model_output(current_slope, current_y_intercept, data.loc[i, "firstHalfTotal"]) - data.loc[i, "totalTeamPoints"] for i in range(data.shape[0])]) * data.shape[0])

    ## Update weights using newton's method.
    ##sum_of_squared_residuals_prime_slope = sum([data.loc[i, "firstHalfTotal"] * (get_model_output(current_slope, current_y_intercept, data.loc[i, "firstHalfTotal"]) - data.loc[i, "totalTeamPoints"]) for i in range(data.shape[0]))
    ##sum_of_squared_residuals_prime_y_intercept = sum([get_model_output(current_slope, current_y_intercept, data.loc[i, "firstHalfTotal"]) - data.loc[i, "totalTeamPoints"] for i in range(data.shape[0])]) * data.shape[0]

    #sum_of_squared_residuals = sum([get_model_output(current_slope, current_y_intercept, data.loc[i, "firstHalfTotal"]) - data.loc[i, "totalTeamPoints"] ** 2 for i in range(data.shape[0])])

    #updated_y_intercept = current_y_intercept - (sum_of_squared_residuals / sum_of_squared_residuals_prime_y_intercept)
    #updated_slope = current_slope - (sum_of_squared_residuals / sum_of_squared_residuals_prime_slope)

    return (updated_slope, updated_y_intercept)

def main():
    preprocessed_dir_path = sys.argv[1]
    weights_file_path = sys.argv[2]

    epsilon = 0.0001

    with open(weights_file_path, 'w', newline='') as weights_file:
        weights_writer = csv.DictWriter(weights_file, fieldnames=["slope", "y-intercept", "estimated-slope", "estimated-y-intercept", "name"])
        weights_writer.writeheader()

        for preprocessed_data_file_path in os.scandir(preprocessed_dir_path):
            slope = 0
            y_intercept = 0
            data = pd.read_csv(preprocessed_data_file_path.path)

            team_name = preprocessed_data_file_path.name.replace('.csv', '').split('_')[-1]
            print(f"Getting weights for {team_name}...")

            for epoch in range(NUM_TRAINING_EPOCHS):
                updated_slope, updated_y_intercept = get_updated_weights(slope, y_intercept, data)
                if abs(updated_slope - slope) < epsilon and abs(updated_y_intercept - y_intercept) < epsilon:
                    slope, y_intercept = updated_slope, updated_y_intercept
                    break

                slope, y_intercept = updated_slope, updated_y_intercept
                if epoch % 50 == 0:
                    print("calcuated weights:", slope, y_intercept)

            weights_from_library = get_weights_from_library(data)
            slope, y_intercept = weights_from_library
            print("from library:", slope, y_intercept)
            weights_writer.writerow({
                "slope": weights_from_library[0],
                "y-intercept": weights_from_library[1],
                "estimated-slope": slope,
                "estimated-y-intercept": y_intercept,
                "name": team_name
            })

main()
