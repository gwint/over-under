# over-under
I want to see how simple of a model can accurately predict whether to bet the over or under for total point totals in NBA games

generate_weights_file.py : Creates a csv containing slope and y-intercept values.  Both calculated through use of gradient descent to minimize the sum of squared residuals in a sheet of first half points - total points data.  Also has weights determined using numpy polyfit with a degree of 1.

generate_error_report.py : Creates a csv containing the sum of squared residuals on a per-team basis
for a given set of weights.

generate_preprocessed_data.py : Creates a collection of csv files (one per team) with the data from TeamStatistics.csv.
