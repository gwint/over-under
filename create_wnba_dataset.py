import pandas as pd
import csv

WNBA_HISTORICAL_PBP_FILE = "game_data/wnba_pbp_data_selenium_final.csv"
NUM_OVERTIMES_TO_TRACK = 4

def is_valid_score_in_dataframe(score_dataframe):
    if isinstance(score_dataframe, pd.DataFrame) and not score_dataframe.empty:
        for i in range(len(score_dataframe)):
            score_str = score_dataframe.iloc[i]["Score"]
            if isinstance(score_str, str) and "-" in score_str:
                parts = score_str.split("-")
                if len(parts) != 2 or not all(part.strip().isdigit() for part in parts):
                    return False
            else:
                return False

    return True

if __name__ == "__main__":
    ## Read in the historical play-by-play data.
    data_df = pd.read_csv(WNBA_HISTORICAL_PBP_FILE)
    print(data_df.columns)

    print(data_df["game_id"].unique())

    scores_csv_file = open('wnba_game_scores.csv', 'w', newline='')
    columns = [
        "game_id",
        "home_team_name",
        "home_team_h1_points", 
        "home_team_h2_points", 
        "home_team_q1_points", 
        "home_team_q2_points", 
        "home_team_q3_points", 
        "home_team_q4_points",
        "home_team_ot1_points",
        "home_team_ot2_points",
        "home_team_ot3_points",
        "home_team_ot4_points",
        "away_team_name", 
        "away_team_h1_points", 
        "away_team_h2_points", 
        "away_team_q1_points", 
        "away_team_q2_points", 
        "away_team_q3_points", 
        "away_team_q4_points",
        "away_team_ot1_points",
        "away_team_ot2_points",
        "away_team_ot3_points",
        "away_team_ot4_points"
    ]
    scores_writer = csv.DictWriter(scores_csv_file, fieldnames=columns)
    scores_writer.writeheader()

    all_data = []
    game_data = {}

    unique_game_ids = data_df["game_id"].unique()
    for game_id in unique_game_ids:
        print(game_id)
        game_year = int(game_id[:4])
        home_team_abbreviation = game_id[-3:]
        print("home team abbreviation:", home_team_abbreviation)
        curr_game_df = data_df[data_df["game_id"] == game_id]
        associated_team_names = curr_game_df["team"].unique()
        #print(associated_team_names)
        team_1_name = associated_team_names[0]
        team_2_name = associated_team_names[1]

        away_team_abbreviation = team_1_name if team_1_name != home_team_abbreviation else team_2_name
        print("away team abbreviation:", away_team_abbreviation)

        print("{} vs. {}".format(team_1_name, team_2_name))
        #print(curr_game_df)

        ## Get first quarter and second quarter points for each team.

        ## There may be many filters we need to use because "End of 1st half" isn't always used.  "2nd Half" is another one that gets used.
        first_quarter_row_mask = (curr_game_df["event"] == "End of 1st half")
        back_up_first_quarter_row_mask = (curr_game_df["event"] == "2nd Half")
        ## If there is no score in this row, need to shift up until we hit a row with the score.
        row_above = curr_game_df[first_quarter_row_mask.shift(-1, fill_value=False)]
        #print("row above", row_above.shape)
        if not is_valid_score_in_dataframe(row_above):
            row_above = curr_game_df[first_quarter_row_mask.shift(-2, fill_value=False)]
        #print(row_above)
        if row_above.empty:
            ## If there is no score in this row, need to shift up until we hit a row with the score.  Only for games before the rule change.
            row_above = curr_game_df[back_up_first_quarter_row_mask.shift(-1, fill_value=False)]
            print(row_above)
            if row_above.empty:
                post_rule_change_mask = (curr_game_df["event"] == "End of 2nd quarter")
                row_above = curr_game_df[post_rule_change_mask.shift(-1, fill_value=False)]
                if not is_valid_score_in_dataframe(row_above):
                    row_above = curr_game_df[post_rule_change_mask.shift(-2, fill_value=False)]
                    assert not row_above.empty, "Couldn't find a row indicating the end of the first quarter for game id: {}".format(game_id)
                
        first_half_scores = row_above[["Score"]]
        #print(first_half_scores)
        assert len(first_half_scores) == 2, "Expected two rows for the two teams' first half scores."

        scores_split = first_half_scores["Score"].str.split("-")
        print(scores_split.iloc[0])
        print(scores_split.iloc[1])
        
        team_1_h1_pts = 0
        team_2_h1_pts = 0
        if game_year < 2006:
            if len(scores_split.iloc[0]) == 2 and len(scores_split.iloc[1]) == 2 and is_valid_score_in_dataframe(row_above):
                print("calculating max for both teams halftime points")
                team_1_h1_pts = max(int(scores_split.iloc[0][0]), int(scores_split.iloc[1][0]))
                team_2_h1_pts = max(int(scores_split.iloc[0][1]), int(scores_split.iloc[1][1]))
            elif len(scores_split.iloc[0]) == 2:
                try:
                    team_1_h1_pts = int(scores_split.iloc[0][0])
                    team_2_h1_pts = int(scores_split.iloc[0][1])
                except ValueError:
                    print("ValueError encountered while parsing halftime scores for game id: {}. Scores split: {}".format(game_id, scores_split.iloc[0]))
                    team_1_h1_pts = int(scores_split.iloc[1][0])
                    team_2_h1_pts = int(scores_split.iloc[1][1])
            elif len(scores_split.iloc[1]) == 2:
                team_1_h1_pts = int(scores_split.iloc[1][0])
                team_2_h1_pts = int(scores_split.iloc[1][1])
            else:
                raise ValueError("Couldn't parse the first half scores for game id: {}".format(game_id))

        home_team_h1_points = 0
        away_team_h1_points = 0
        if team_1_name == home_team_abbreviation:
            home_team_h1_points = team_1_h1_pts
            away_team_h1_points = team_2_h1_pts
        else:
            home_team_h1_points = team_2_h1_pts
            away_team_h1_points = team_1_h1_pts


        ## Get second half scores for each game.
        second_half_row_mask = (curr_game_df["event"] == "End of 2nd half")
        row_above = curr_game_df[second_half_row_mask.shift(-1, fill_value=False)]
        if row_above.empty or not is_valid_score_in_dataframe(row_above):
            row_above = curr_game_df[second_half_row_mask.shift(-2, fill_value=False)]
            if row_above.empty or not is_valid_score_in_dataframe(row_above):
                print("No rows found, using backup indicators")
                ## Find last row of the game for each team and check if there is a score there.  Some rows don't have a "End of 2nd half" event.
                team_1_name_mask = (curr_game_df["team"] == team_1_name)
                team_1_last_row = curr_game_df[team_1_name_mask].iloc[-1]
                team_2_name_mask = (curr_game_df["team"] == team_2_name)
                team_2_last_row = curr_game_df[team_2_name_mask].iloc[-1]
                row_above = pd.concat([team_1_last_row.to_frame().T, team_2_last_row.to_frame().T], ignore_index=True)
                print(row_above)

                if not is_valid_score_in_dataframe(row_above):
                    ## Try shfiting up from the last row as a last resort.  This should always yield a valid score because some row should definitely have a score.
                    row_from_bottom_index = -1
                    while not is_valid_score_in_dataframe(row_above):
                        row_from_bottom_index -= 1
                        team_1_row = curr_game_df[team_1_name_mask].iloc[row_from_bottom_index]
                        team_2_row = curr_game_df[team_2_name_mask].iloc[row_from_bottom_index]
                        row_above = pd.concat([team_1_row.to_frame().T, team_2_row.to_frame().T], ignore_index=True)
                        print(row_above)
                        
                    #assert not row_above.empty, "Couldn't find a row indicating the end of the second half for game id: {}".format(game_id)

        second_half_scores = row_above[["Score"]]
        print(second_half_scores)
        assert len(second_half_scores) == 2, "Expected two rows for the two teams' second half scores."

        scores_split = second_half_scores["Score"].str.split("-")
        print(scores_split.iloc[0])
        print(scores_split.iloc[1])

        team_1_h2_pts = 0
        team_2_h2_pts = 0
        if game_year < 2006:
            if len(scores_split.iloc[0]) == 2 and len(scores_split.iloc[1]) == 2 and is_valid_score_in_dataframe(row_above):
                print("calculating max for both teams second half points")
                team_1_h2_pts = max(int(scores_split.iloc[0][0]), int(scores_split.iloc[1][0])) - team_1_h1_pts
                team_2_h2_pts = max(int(scores_split.iloc[0][1]), int(scores_split.iloc[1][1])) - team_2_h1_pts
            elif len(scores_split.iloc[0]) == 2:
                try:
                    team_1_h2_pts = int(scores_split.iloc[0][0]) - team_1_h1_pts
                    team_2_h2_pts = int(scores_split.iloc[0][1]) - team_2_h1_pts
                except ValueError:
                    print("ValueError encountered while parsing second half scores for game id: {}. Scores split: {}".format(game_id, scores_split.iloc[0]))
                    team_1_h2_pts = int(scores_split.iloc[1][0]) - team_1_h1_pts
                    team_2_h2_pts = int(scores_split.iloc[1][1]) - team_2_h1_pts
            elif len(scores_split.iloc[1]) == 2:
                team_1_h2_pts = int(scores_split.iloc[1][0]) - team_1_h1_pts
                team_2_h2_pts = int(scores_split.iloc[1][1]) - team_2_h1_pts
            else:
                raise ValueError("Couldn't parse the second half scores for game id: {}".format(game_id))

        home_team_h2_points = 0
        away_team_h2_points = 0
        if team_1_name == home_team_abbreviation:
            home_team_h2_points = team_1_h2_pts
            away_team_h2_points = team_2_h2_pts
        else:
            home_team_h2_points = team_2_h2_pts
            away_team_h2_points = team_1_h2_pts

        ## TODO: Get the first quarter and third quarter scores for games after the rule change i 2006 where halves were changed to quarters.
        first_quarter_row_mask = (curr_game_df["event"] == "End of 1st quarter")

        row_above_end_of_q1 = curr_game_df[first_quarter_row_mask.shift(-1, fill_value=False)]
        if not is_valid_score_in_dataframe(row_above_end_of_q1):
            row_above_end_of_q1 = curr_game_df[first_quarter_row_mask.shift(-2, fill_value=False)]

        if not row_above_end_of_q1.empty:
            first_quarter_scores = row_above_end_of_q1[["Score"]]
            print(first_quarter_scores)
            assert len(first_quarter_scores) == 2, "Expected two rows for the two teams' first quarter scores."

            scores_split = first_quarter_scores["Score"].str.split("-")
            print("q1 scores (1):", scores_split.iloc[0])
            print("q1 scores (2):", scores_split.iloc[1])

        team_1_q1_pts = 0
        team_2_q1_pts = 0
        if game_year >= 2006:
            if len(scores_split.iloc[0]) == 2 and len(scores_split.iloc[1]) == 2 and is_valid_score_in_dataframe(row_above_end_of_q1):
                print("calculating max for both teams second half points")
                team_1_q1_pts = max(int(scores_split.iloc[0][0]), int(scores_split.iloc[1][0]))
                team_2_q1_pts = max(int(scores_split.iloc[0][1]), int(scores_split.iloc[1][1]))
            elif len(scores_split.iloc[0]) == 2:
                try:
                    team_1_q1_pts = int(scores_split.iloc[0][0])
                    team_2_q1_pts = int(scores_split.iloc[0][1])
                except ValueError:
                    print("ValueError encountered while parsing q1 scores for game id: {}. Scores split: {}".format(game_id, scores_split.iloc[0]))
                    team_1_q1_pts = int(scores_split.iloc[1][0])
                    team_2_q1_pts = int(scores_split.iloc[1][1])
            elif len(scores_split.iloc[1]) == 2:
                team_1_q1_pts = int(scores_split.iloc[1][0])
                team_2_q1_pts = int(scores_split.iloc[1][1])
            else:
                raise ValueError("Couldn't parse the first quarter scores for game id: {}".format(game_id))

        home_team_q1_points = 0
        away_team_q1_points = 0
        if team_1_name == home_team_abbreviation:
            home_team_q1_points = team_1_q1_pts
            away_team_q1_points = team_2_q1_pts
        else:
            home_team_q1_points = team_2_q1_pts
            away_team_q1_points = team_1_q1_pts
            
        ## TODO: Get end of 2nd quarter scores.
        second_quarter_row_mask = (curr_game_df["event"] == "End of 2nd quarter")

        row_above_end_of_q2 = curr_game_df[second_quarter_row_mask.shift(-1, fill_value=False)]
        if not is_valid_score_in_dataframe(row_above_end_of_q2):
            row_above_end_of_q2 = curr_game_df[second_quarter_row_mask.shift(-2, fill_value=False)]

        if not row_above_end_of_q2.empty:
            second_quarter_scores = row_above_end_of_q2[["Score"]]
            print(second_quarter_scores)
            assert len(second_quarter_scores) == 2, "Expected two rows for the two teams' second quarter scores."

            scores_split = second_quarter_scores["Score"].str.split("-")
            print("q2 scores (1):", scores_split.iloc[0])
            print("q2 scores (2):", scores_split.iloc[1])

        team_1_q2_pts = 0
        team_2_q2_pts = 0
        if game_year >= 2006:
            if len(scores_split.iloc[0]) == 2 and len(scores_split.iloc[1]) == 2 and is_valid_score_in_dataframe(row_above_end_of_q2):
                print("calculating max for both teams second half points")
                team_1_q2_pts = max(int(scores_split.iloc[0][0]), int(scores_split.iloc[1][0])) - team_1_q1_pts
                team_2_q2_pts = max(int(scores_split.iloc[0][1]), int(scores_split.iloc[1][1])) - team_2_q1_pts
            elif len(scores_split.iloc[0]) == 2:
                try:
                    team_1_q2_pts = int(scores_split.iloc[0][0]) - team_1_q1_pts
                    team_2_q2_pts = int(scores_split.iloc[0][1]) - team_2_q1_pts
                except ValueError:
                    print("ValueError encountered while parsing q2 scores for game id: {}. Scores split: {}".format(game_id, scores_split.iloc[0]))
                    team_1_q2_pts = int(scores_split.iloc[1][0]) - team_1_q1_pts
                    team_2_q2_pts = int(scores_split.iloc[1][1]) - team_2_q1_pts
            elif len(scores_split.iloc[1]) == 2:
                team_1_q2_pts = int(scores_split.iloc[1][0]) - team_1_q1_pts
                team_2_q2_pts = int(scores_split.iloc[1][1]) - team_2_q1_pts
            else:
                raise ValueError("Couldn't parse the second quarter scores for game id: {}".format(game_id))

        home_team_q2_points = 0
        away_team_q2_points = 0
        if team_1_name == home_team_abbreviation:
            home_team_q2_points = team_1_q2_pts
            away_team_q2_points = team_2_q2_pts
        else:
            home_team_q2_points = team_2_q2_pts
            away_team_q2_points = team_1_q2_pts

        third_quarter_row_mask = (curr_game_df["event"] == "End of 3rd quarter")
        row_above_end_of_q3 = curr_game_df[third_quarter_row_mask.shift(-1, fill_value=False)]
        if not is_valid_score_in_dataframe(row_above_end_of_q3):
            row_above_end_of_q3 = curr_game_df[third_quarter_row_mask.shift(-2, fill_value=False)]

        if not row_above_end_of_q3.empty:
            third_quarter_scores = row_above_end_of_q3[["Score"]]
            print(third_quarter_scores)
            assert len(third_quarter_scores) == 2, "Expected two rows for the two teams' third quarter scores."

            scores_split = third_quarter_scores["Score"].str.split("-")
            print("q3 scores (1):", scores_split.iloc[0])
            print("q3 scores (2):", scores_split.iloc[1])

        team_1_q3_pts = 0
        team_2_q3_pts = 0
        if game_year >= 2006:
            if len(scores_split.iloc[0]) == 2 and len(scores_split.iloc[1]) == 2 and is_valid_score_in_dataframe(row_above_end_of_q3):
                print("calculating max for both teams third quarter points")
                team_1_q3_pts = max(int(scores_split.iloc[0][0]), int(scores_split.iloc[1][0])) - team_1_q2_pts - team_1_q1_pts
                team_2_q3_pts = max(int(scores_split.iloc[0][1]), int(scores_split.iloc[1][1])) - team_2_q2_pts - team_2_q1_pts
            elif len(scores_split.iloc[0]) == 2:
                try:
                    team_1_q3_pts = int(scores_split.iloc[0][0]) - team_1_q2_pts - team_1_q1_pts
                    team_2_q3_pts = int(scores_split.iloc[0][1]) - team_2_q2_pts - team_2_q1_pts
                except ValueError:
                    print("ValueError encountered while parsing q3 scores for game id: {}. Scores split: {}".format(game_id, scores_split.iloc[0]))
                    team_1_q3_pts = int(scores_split.iloc[1][0]) - team_1_q2_pts - team_1_q1_pts
                    team_2_q3_pts = int(scores_split.iloc[1][1]) - team_2_q2_pts - team_2_q1_pts
            elif len(scores_split.iloc[1]) == 2:
                team_1_q3_pts = int(scores_split.iloc[1][0]) - team_1_q2_pts - team_1_q1_pts
                team_2_q3_pts = int(scores_split.iloc[1][1]) - team_2_q2_pts - team_2_q1_pts
            else:
                raise ValueError("Couldn't parse the first quarter scores for game id: {}".format(game_id))

        home_team_q3_points = 0
        away_team_q3_points = 0
        if team_1_name == home_team_abbreviation:
            home_team_q3_points = team_1_q3_pts
            away_team_q3_points = team_2_q3_pts
        else:
            home_team_q3_points = team_2_q3_pts
            away_team_q3_points = team_1_q3_pts

        ## TODO: Get 4th quarter scores.
        fourth_quarter_row_mask = (curr_game_df["event"] == "End of 4th quarter")
        row_above_end_of_q4 = curr_game_df[fourth_quarter_row_mask.shift(-1, fill_value=False)]
        if not is_valid_score_in_dataframe(row_above_end_of_q4):
            row_above_end_of_q4 = curr_game_df[fourth_quarter_row_mask.shift(-2, fill_value=False)]

        if not row_above_end_of_q4.empty:
            fourth_quarter_scores = row_above_end_of_q4[["Score"]]
            print(fourth_quarter_scores)
            assert len(fourth_quarter_scores) == 2, "Expected two rows for the two teams' fourth quarter scores."

            scores_split = fourth_quarter_scores["Score"].str.split("-")
            print("q4 scores (1):", scores_split.iloc[0])
            print("q4 scores (2):", scores_split.iloc[1])

        team_1_q4_pts = 0
        team_2_q4_pts = 0
        if game_year >= 2006:
            if len(scores_split.iloc[0]) == 2 and len(scores_split.iloc[1]) == 2 and is_valid_score_in_dataframe(row_above_end_of_q4):
                print("calculating max for both teams fourth quarter points")
                team_1_q4_pts = max(int(scores_split.iloc[0][0]), int(scores_split.iloc[1][0])) - team_1_q3_pts - team_1_q2_pts - team_1_q1_pts
                team_2_q4_pts = max(int(scores_split.iloc[0][1]), int(scores_split.iloc[1][1])) - team_2_q3_pts - team_2_q2_pts - team_2_q1_pts
            elif len(scores_split.iloc[0]) == 2:
                try:
                    team_1_q4_pts = int(scores_split.iloc[0][0]) - team_1_q3_pts - team_1_q2_pts - team_1_q1_pts
                    team_2_q4_pts = int(scores_split.iloc[0][1]) - team_2_q3_pts - team_2_q2_pts - team_2_q1_pts
                except ValueError:
                    print("ValueError encountered while parsing q4 scores for game id: {}. Scores split: {}".format(game_id, scores_split.iloc[0]))
                    team_1_q4_pts = int(scores_split.iloc[1][0]) - team_1_q3_pts - team_1_q2_pts - team_1_q1_pts
                    team_2_q4_pts = int(scores_split.iloc[1][1]) - team_2_q3_pts - team_2_q2_pts - team_2_q1_pts
            elif len(scores_split.iloc[1]) == 2:
                team_1_q4_pts = int(scores_split.iloc[1][0]) - team_1_q3_pts - team_1_q2_pts - team_1_q1_pts
                team_2_q4_pts = int(scores_split.iloc[1][1]) - team_2_q3_pts - team_2_q2_pts - team_2_q1_pts
            else:
                raise ValueError("Couldn't parse the first quarter scores for game id: {}".format(game_id))

        home_team_q4_points = 0
        away_team_q4_points = 0
        if team_1_name == home_team_abbreviation:
            home_team_q4_points = team_1_q4_pts
            away_team_q4_points = team_2_q4_pts
        else:
            home_team_q4_points = team_2_q4_pts
            away_team_q4_points = team_1_q4_pts

        ## TODO: Fetch overtime scores for games that went into overtime.
        overtime_to_ordinal_mapping = {
            1: "1st",
            2: "2nd",
            3: "3rd",
            4: "4th"
        }

        team_1_ot_scores = [0 for _ in range(NUM_OVERTIMES_TO_TRACK)]
        team_2_ot_scores = [0 for _ in range(NUM_OVERTIMES_TO_TRACK)]

        home_team_ot_scores = [0 for _ in range(NUM_OVERTIMES_TO_TRACK)]
        away_team_ot_scores = [0 for _ in range(NUM_OVERTIMES_TO_TRACK)]
        for overtime in range(1, NUM_OVERTIMES_TO_TRACK + 1):
            overtime_row_mask = (curr_game_df["event"] == f"End of {overtime_to_ordinal_mapping[overtime]} overtime")
            row_above_end_of_ot = curr_game_df[overtime_row_mask.shift(-1, fill_value=False)]
            if not is_valid_score_in_dataframe(row_above_end_of_ot):
                row_above_end_of_ot = curr_game_df[overtime_row_mask.shift(-2, fill_value=False)]

            if not row_above_end_of_ot.empty:
                ot_scores = row_above_end_of_ot[["Score"]]
                print("OT{} scores".format(overtime), ot_scores)
                assert len(ot_scores) == 2, "Expected two rows for the two teams' OT{} scores.".format(overtime)

                scores_split = ot_scores["Score"].str.split("-")
                print("OT{} scores (1):".format(overtime), scores_split.iloc[0])
                print("OT{} scores (2):".format(overtime), scores_split.iloc[1])

                team_1_ot_pts = 0
                team_2_ot_pts = 0
                if len(scores_split.iloc[0]) == 2 and len(scores_split.iloc[1]) == 2 and is_valid_score_in_dataframe(row_above_end_of_ot):
                    print("calculating max for both teams fourth quarter points")
                    if game_year < 2006:
                        team_1_ot_pts = max(int(scores_split.iloc[0][0]), int(scores_split.iloc[1][0])) - sum(team_1_ot_scores[:overtime-1]) - team_1_h2_pts - team_1_h1_pts
                        team_2_ot_pts = max(int(scores_split.iloc[0][1]), int(scores_split.iloc[1][1])) - sum(team_2_ot_scores[:overtime-1]) - team_2_h2_pts - team_2_h1_pts
                    else:
                        team_1_ot_pts = max(int(scores_split.iloc[0][0]), int(scores_split.iloc[1][0])) - sum(team_1_ot_scores[:overtime-1]) - team_1_q4_pts - team_1_q3_pts - team_1_q2_pts - team_1_q1_pts
                        team_2_ot_pts = max(int(scores_split.iloc[0][1]), int(scores_split.iloc[1][1])) - sum(team_2_ot_scores[:overtime-1]) - team_2_q4_pts - team_2_q3_pts - team_2_q2_pts - team_2_q1_pts
                elif len(scores_split.iloc[0]) == 2:
                    try:
                        if game_year < 2006:
                            team_1_ot_pts = int(scores_split.iloc[0][0]) - sum(team_1_ot_scores[:overtime-1]) - team_1_h2_pts - team_1_h1_pts
                            team_2_ot_pts = int(scores_split.iloc[0][1]) - sum(team_2_ot_scores[:overtime-1]) - team_2_h2_pts - team_2_h1_pts
                        else:
                            team_1_ot_pts = int(scores_split.iloc[0][0]) - sum(team_1_ot_scores[:overtime-1]) - team_1_q4_pts - team_1_q3_pts - team_1_q2_pts - team_1_q1_pts
                            team_2_ot_pts = int(scores_split.iloc[0][1]) - sum(team_2_ot_scores[:overtime-1]) - team_2_q4_pts - team_2_q3_pts - team_2_q2_pts - team_2_q1_pts
                    except ValueError:
                        print("ValueError encountered while parsing ot scores for game id: {}. Scores split: {}".format(game_id, scores_split.iloc[0]))
                        if game_year < 2006:
                            team_1_ot_pts = int(scores_split.iloc[1][0]) - sum(team_1_ot_scores[:overtime-1]) - team_1_h2_pts - team_1_h1_pts
                            team_2_ot_pts = int(scores_split.iloc[1][1]) - sum(team_2_ot_scores[:overtime-1]) - team_2_h2_pts - team_2_h1_pts
                        else:
                            team_1_ot_pts = int(scores_split.iloc[1][0]) - sum(team_1_ot_scores[:overtime-1]) - team_1_q4_pts - team_1_q3_pts - team_1_q2_pts - team_1_q1_pts
                            team_2_ot_pts = int(scores_split.iloc[1][1]) - sum(team_2_ot_scores[:overtime-1]) - team_2_q4_pts - team_2_q3_pts - team_2_q2_pts - team_2_q1_pts
                elif len(scores_split.iloc[1]) == 2:
                    if game_year < 2006:
                        team_1_ot_pts = int(scores_split.iloc[1][0]) - sum(team_1_ot_scores[:overtime-1]) - team_1_h2_pts - team_1_h1_pts
                        team_2_ot_pts = int(scores_split.iloc[1][1]) - sum(team_2_ot_scores[:overtime-1]) - team_2_h2_pts - team_2_h1_pts
                    else:
                        team_1_ot_pts = int(scores_split.iloc[1][0]) - sum(team_1_ot_scores[:overtime-1]) - team_1_q4_pts - team_1_q3_pts - team_1_q2_pts - team_1_q1_pts
                        team_2_ot_pts = int(scores_split.iloc[1][1]) - sum(team_2_ot_scores[:overtime-1]) - team_2_q4_pts - team_2_q3_pts - team_2_q2_pts - team_2_q1_pts
                else:
                    raise ValueError("Couldn't parse the overtime scores for game id: {}".format(game_id))

                team_1_ot_scores[overtime - 1] = team_1_ot_pts
                team_2_ot_scores[overtime - 1] = team_2_ot_pts

        if team_1_name == home_team_abbreviation:
            home_team_ot_scores = team_1_ot_scores
            away_team_ot_scores = team_2_ot_scores
        else:
            home_team_ot_scores = team_2_ot_scores
            away_team_ot_scores = team_1_ot_scores

        print("home team ot points: ", home_team_ot_scores)
        print("away team ot points: ", away_team_ot_scores)

        game_data[game_id] = {
            team_1_name: {
                "h1_pts": team_1_h1_pts,
                "h2_pts": team_1_h2_pts
            },
            team_2_name: {
                "h1_pts": team_2_h1_pts,
                "h2_pts": team_2_h2_pts
            }
        }

        single_game_data = {
            "game_id": game_id,
            "home_team_name": home_team_abbreviation,
            "home_team_h1_points": home_team_h1_points, 
            "home_team_h2_points": home_team_h2_points, 
            "home_team_q1_points": home_team_q1_points, 
            "home_team_q2_points": home_team_q2_points, 
            "home_team_q3_points": home_team_q3_points, 
            "home_team_q4_points": home_team_q4_points,
            "home_team_ot1_points": home_team_ot_scores[0],
            "home_team_ot2_points": home_team_ot_scores[1],
            "home_team_ot3_points": home_team_ot_scores[2],
            "home_team_ot4_points": home_team_ot_scores[3],
            "away_team_name": away_team_abbreviation, 
            "away_team_h1_points": away_team_h1_points, 
            "away_team_h2_points": away_team_h2_points, 
            "away_team_q1_points": away_team_q1_points, 
            "away_team_q2_points": away_team_q2_points,
            "away_team_q3_points": away_team_q3_points, 
            "away_team_q4_points": away_team_q4_points,
            "away_team_ot1_points": away_team_ot_scores[0],
            "away_team_ot2_points": away_team_ot_scores[1],
            "away_team_ot3_points": away_team_ot_scores[2],
            "away_team_ot4_points": away_team_ot_scores[3]
        }
        all_data.append(single_game_data)

        #print(row_above)

    scores_writer.writerows(all_data)

    print(game_data)