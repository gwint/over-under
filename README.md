# over-under
I want to see how simple of a model can accurately predict whether to bet the over or under for total point totals in NBA games.  The main source for game data can be found at https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores?select=TeamStatistics.csv.  We begin by comparing a linear regression model and a locally weighted linear regression model created based on only team scores at halftime.

Model Generation and Evaluation Steps for Linear regression to answer the question "Can we predict a team's full game point total based on it's point total at halftime?":

0) Create and activate a python virtual environment in which we will install the neccesary dependencies:
`python3 -m venv dependencies`
`source dependencies/bin/activate` (on linux systems, for windows / macOS consult your preferred search engine for the correct activation command)
`pip install -r requirements.txt`

1) Generate smaller preprocessed, per-team csv's with just the data we care about (points at half time, points at game end) from the contents of game_data/TeamStatistics.csv.
generate_preprocessed_data.py : Creates a collection of csv files (one per team) with the data from TeamStatistics.csv:
`python generate_preprocessed_data.py game_data/TeamStatistics.csv preprocessed_data`
NOTE: The preprocessed_data directory will be created if it does not exist, and will be deleted and then recreated if it already exists.

2) Generate scatter plot visualizations of the per-team preprocessed data to better understand the data.
`python generate_data_visualizations preprocessed_data visualizations`
NOTE: The preprocessed_data directory is assumed to already exist and should contain the csv files created in step 2.  "visualizations" is the target directory in which the generated scatter plot png files will be placed.  If the directory does not exist then it will be created, and if it does exist it will be delated and recreated.

3) Train the linear regression models and generate a csv file containing weights for each team in the training set.
`python linear_regression.py  preprocessed_data linear_regression_weights`
NOTE: The generated weights file (in the example named 'linear_regression_weights') will contain slope and y-intercept values computed by both a manual gradient descent implementation and a library-provided function call for comparison.

4) Generate an error report tracking test error against a set of team scoring data not included in the test set.  generate_error_report.py : Creates a csv containing the sum of squared residuals on a per-team basis
for a given set of weights.
`python generate_error_report.py game_data/GameDataForTesting.csv linear_regression_weights error_report`