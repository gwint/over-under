import pandas as pd
import csv
import os

DATA_PATH = "preprocessed_data/preprocessed_data_wizards.csv"
LEARNING_RATE = 0.0000001
NUM_TRAINING_EPOCHS = 15000
WEIGHTS_FILE_PATH = "calculated_weights.csv"
PREPROCESSED_DATA_DIRECTORY = "preprocessed_data"

def get_model_output(slope, y_intercept, single_input_data):
    return (float(slope) * float(single_input_data)) + float(y_intercept)

def get_updated_weights(current_slope: float, current_y_intercept: float, data):
    updated_slope = current_slope - (LEARNING_RATE * sum([data.loc[i, "firstHalfTotal"] * (get_model_output(current_slope, current_y_intercept, data.loc[i, "firstHalfTotal"]) - data.loc[i, "totalTeamPoints"]) for i in range(data.shape[0])]))

    updated_y_intercept = current_y_intercept - (LEARNING_RATE * sum([get_model_output(current_slope, current_y_intercept, data.loc[i, "firstHalfTotal"]) - data.loc[i, "totalTeamPoints"] for i in range(data.shape[0])]) * data.shape[0])

    return (updated_slope, updated_y_intercept)

def main():
    ##pointsAtHalftime = int(input("Points at halftime: "))
    epsilon = 0.0001

    with open(WEIGHTS_FILE_PATH, 'w', newline='') as weights_file:
        ## TODO: Read through directory 
        for preprocessed_data_file_path in os.scandir(PREPROCESSED_DATA_DIRECTORY):
            print(preprocessed_data_file_path.path)
            slope = 0
            y_intercept = 0
            data = pd.read_csv(preprocessed_data_file_path.path)

            team_name = preprocessed_data_file_path.name.replace('.csv', '').split('_')[-1]

            print(f"Training model for {team_name}...")
            for _ in range(NUM_TRAINING_EPOCHS):
                updated_slope, updated_y_intercept = get_updated_weights(slope, y_intercept, data)
                if abs(updated_slope - slope) < epsilon and abs(updated_y_intercept - y_intercept) < epsilon:
                    slope, y_intercept = updated_slope, updated_y_intercept
                    break

                slope, y_intercept = updated_slope, updated_y_intercept
                print(slope, y_intercept)

            print(f"Model for {team_name} trained:", slope, y_intercept)
            break

    '''
    data = pd.read_csv(DATA_PATH)
    slope = 1
    y_intercept = 0 

    for _ in range(NUM_TRAINING_EPOCHS):
        slope, y_intercept = get_updated_weights(slope, y_intercept, data)
        print(slope, y_intercept)

    ## TODO: Evaluate equations at point
    expected_full_game_points = get_model_output(slope, y_intercept, pointsAtHalftime)
    print(expected_full_game_points)
    '''

main()
