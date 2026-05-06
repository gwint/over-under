# over-under
I want to see how simple of a model can accurately predict whether to bet the over or under for total point totals in NBA games.  The main source for game data can be found at https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores?select=TeamStatistics.csv.  We begin by comparing a linear regression model and a locally weighted linear regression model created based on
only team scores at halftime.

generate_weights_file.py : Creates a csv containing slope and y-intercept values.  Both calculated through use of gradient descent to minimize the sum of squared residuals in a sheet of first half points - total points data.  Also has weights determined using numpy polyfit with a degree of 1.
ex: TBD

generate_error_report.py : Creates a csv containing the sum of squared residuals on a per-team basis
for a given set of weights.
ex: `python pipeline/generate_error_report.py game_data/TeamStatistics.csv old_weights.csv`

generate_preprocessed_data.py : Creates a collection of csv files (one per team) with the data from TeamStatistics.csv.
ex: `python pipeline/generate_preprocessed_data.py game_data/TeamStatistics.csv`

run.sh : Run a backtest using data not included in the training set (~about 2 weeks of data), figuring
out money is won/lost following a betting strategy (currently using first half points to bet nba game totals, placing the bet at halftime).  A csv containing betting results (pot amount over time) will be generated.  We use docker under the hood to launch a container, install dependencies, and run the backtest.

$ docker build -t backtest .
$ docker run -it --rm --name running-backtest backtest

