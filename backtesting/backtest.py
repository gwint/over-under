import csv
import pprint
import requests

from pathlib import Path

WEIGHTS_FILE = "./calculated_weights.csv"
TESTING_GAME_DATA_FILE = "/home/gregory/Downloads/archive/GameDataForTesting.csv"
PLAY_BY_PLAY_DATA_DIR = "/home/gregory/Downloads/25-26-season"

ODDS_API_KEY = "7273e9fafc3995992cde8244590ac0ad"

NBA_TEAMS_TO_CITIES = {
    "hawks": "atlanta",
    "celtics": "boston",
    "nets": "brooklyn",
    "hornets": "charlotte",
    "bulls": "chicago",
    "cavaliers": "cleveland",
    "mavericks": "dallas",
    "nuggets": "denver",
    "pistons": "detroit",
    "warriors": "golden state",
    "rockets": "houston",
    "pacers": "indiana",
    "clippers": "los angeles",
    "lakers": "los angeles",
    "grizzlies": "memphis",
    "heat": "miami",
    "bucks": "milwaukee",
    "timberwolves": "minnesota",
    "pelicans": "new orleans",
    "knicks": "new york",
    "thunder": "oklahoma city",
    "magic": "orlando",
    "76ers": "philadelphia",
    "suns": "phoenix",
    "trail blazers": "portland",
    "kings": "sacramento",
    "spurs": "san antonio",
    "raptors": "toronto",
    "jazz": "utah",
    "wizards": "washington"
}

NBA_TEAM_ACRONYMS = {
    'hawks': 'ATL',
    'celtics': 'BOS',
    'nets': 'BKN',
    'hornets': 'CHA',
    'bulls': 'CHI',
    'cavaliers': 'CLE',
    'mavericks': 'DAL',
    'nuggets': 'DEN',
    'pistons': 'DET',
    'warriors': 'GSW',
    'rockets': 'HOU',
    'pacers': 'IND',
    'clippers': 'LAC',
    'lakers': 'LAL',
    'grizzlies': 'MEM',
    'heat': 'MIA',
    'bucks': 'MIL',
    'timberwolves': 'MIN',
    'pelicans': 'NOP',
    'knicks': 'NYK',
    'thunder': 'OKC',
    'magic': 'ORL',
    '76ers': 'PHI',
    'suns': 'PHX',
    'trail blazers': 'POR',
    'kings': 'SAC',
    'spurs': 'SAS',
    'raptors': 'TOR',
    'jazz': 'UTA',
    'wizards': 'WAS'
}

def get_row_key(row_data):
    game_date = row_data["gameDateTimeEst"]
    team_name = row_data["teamName"].strip().lower()
    opponent_name = row_data["opponentTeamName"].strip().lower()

    return f"{game_date}:{':'.join(sorted([team_name, opponent_name]))}"

def get_clean_timestamp(timestamp: str): 
    return timestamp.split('.')[0] + "Z"

def get_halftime_timestamp(game_date, team_1_name, team_2_name):
    ## TODO: Path doesn't look like it can be generated fully due to unguessable numbers included.  Check for inclusion of date, and team acronyms while looping through the directory to find it.
    play_by_play_directory_path = Path(PLAY_BY_PLAY_DATA_DIR)
    relevant_play_by_play_file = ""
    for item in play_by_play_directory_path.iterdir():
        if NBA_TEAM_ACRONYMS[team_1_name] in item.name and NBA_TEAM_ACRONYMS[team_2_name] in item.name and game_date in item.name:
            #print(item.name)
            relevant_play_by_play_file = item.name
            break
            
    ## TODO: Read the correct file and find the row for the second 'end of period' (halftime) and get the actual time.
    with open(f"{PLAY_BY_PLAY_DATA_DIR}/{relevant_play_by_play_file}", 'r') as play_by_play:
        play_by_play_reader = csv.DictReader(play_by_play)
        end_of_period_count = 0
        for row in play_by_play_reader:
            event_type = row["event_type"]
            event_time = row["time_actual"]
            if event_type == "end of period":
                end_of_period_count += 1
                #print(event_type, event_time)

                if end_of_period_count == 2:
                    return get_clean_timestamp(event_time)

        raise Exception(f"Unable to find halftime in {PLAY_BY_PLAY_DATA_DIR}/{relevant_play_by_play_file}")

def get_halftime_point_total_line(game_date, team_1_name, team_2_name):
    halftime_datetime = get_halftime_timestamp(game_date, team_1_name, team_2_name)
    #print("halftime_datetime:", halftime_datetime)

    ## Assume start of halftime.
    point_total_line_endpoint = f"https://api.the-odds-api.com/v4/historical/sports/basketball_nba/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=totals&oddsFormat=american&date={halftime_datetime}"
    ## TODO: Send request using requests
    line_response = requests.get(point_total_line_endpoint)
    if line_response.status_code == 200:
        data = line_response.json()["data"]
        ##print(data)
        ## TODO: Find the game using the team names, and draftkings
        full_team_1_name = f"{NBA_TEAMS_TO_CITIES[team_1_name]} {team_1_name}"
        full_team_2_name = f"{NBA_TEAMS_TO_CITIES[team_2_name]} {team_2_name}"
        #print("calculated team names:", full_team_1_name, full_team_2_name)
        ## TODO: Iterate through bookmakers until you find draftkings line and return it.
        
        single_outcome_object = {}
        for betting_data in data:
            curr_home_team = betting_data["home_team"].lower()
            curr_away_team = betting_data["away_team"].lower()
            ##print("team names from betting api data:", curr_home_team, curr_away_team)
            if (curr_home_team == full_team_1_name and curr_away_team == full_team_2_name) or \
            (curr_home_team == full_team_2_name and curr_away_team == full_team_1_name):
                ##print("Looking through bookmakers...")
                for bookmaker_data in betting_data["bookmakers"]:
                    if bookmaker_data["key"] == "draftkings":
                        for market_data in bookmaker_data["markets"]:
                            if market_data["key"] == "totals":
                                for outcome in market_data["outcomes"]:
                                    single_outcome_object["line"] = outcome["point"]
                                    if outcome["name"] == "Over":
                                        single_outcome_object["over"] = outcome["price"]
                                    else:
                                        single_outcome_object["under"] = outcome["price"]

        return single_outcome_object

    else:
        return {}

def main():
    print(f"Performing a backtest using the game data in <file-path>...")
    print(f"Our per-game bet is $<dollar-amount> and we assume infinite bankroll")
    print(f"Model weights are being pulled from <weights-file>")

    ## TODO: Read in model weights and populate a dictionary.
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

        team_matchup_stats = {}
        with open(TESTING_GAME_DATA_FILE, 'r', newline='') as testing_data_file:
            testing_data_reader = csv.DictReader(testing_data_file)
            for testing_data in testing_data_reader:
                ## TODO: Figure out the key (<date>:<team_first>:<team_second>), teams in sorted order.
                row_key = get_row_key(testing_data)

                if row_key not in team_matchup_stats:
                    team_matchup_stats[row_key] = []

                team_matchup_stats[row_key].append(testing_data)

                ##print(testing_data["teamName"], testing_data["teamScore"], estimated_total, testing_data["q1Points"], testing_data["q2Points"])

            wins = 0
            losses = 0
            pot = 1000.0
            bet_amount = 210.0
            
            for matchup in team_matchup_stats:
                team_1_row, team_2_row = tuple(team_matchup_stats[matchup])
                assert team_1_row["teamId"] == team_2_row["opponentTeamId"]
                assert team_2_row["teamId"] == team_1_row["opponentTeamId"]

                team_1_name = team_1_row["teamName"]
                team_2_name = team_2_row["teamName"]

                game_datetime = team_1_row["gameDateTimeEst"]
                game_datetime = game_datetime.split()[0]

                team_1_point_total = float(team_1_row["teamScore"])
                team_2_point_total = float(team_1_row["opponentScore"])

                ## TODO: Get team 1 scores in q1 and q2 along with point total
                team_1_first_half_score = float(team_1_row["q1Points"]) + float(team_1_row["q2Points"])
                ## TODO: Get team 2 scores in q1 and q2 along with point total
                team_2_first_half_score = float(team_2_row["q1Points"]) + float(team_2_row["q2Points"])

                team_1_name = team_1_row["teamName"].lower().strip()
                team_2_name = team_2_row["teamName"].lower().strip()

                team_1_slope = float(per_team_weights[team_1_name]["slope"])
                team_1_y_intercept = float(per_team_weights[team_1_name]["y_intercept"])
                #print(team_1_name, team_1_slope, team_1_y_intercept)

                team_2_slope = float(per_team_weights[team_2_name]["slope"])
                team_2_y_intercept = float(per_team_weights[team_2_name]["y_intercept"])

                team_1_estimated_total = team_1_slope * team_1_first_half_score + team_1_y_intercept
                team_2_estimated_total = team_2_slope * team_2_first_half_score + team_2_y_intercept

                estimated_total = team_1_estimated_total + team_2_estimated_total
                actual_total = team_1_point_total + team_2_point_total
                
                betting_line = get_halftime_point_total_line(game_datetime, team_1_name, team_2_name)
                #print("betting line:", betting_line)
                line = betting_line["line"]
                over_odds = betting_line["over"]
                under_odds = betting_line["under"]

                over_payoff = bet_amount * ((100 + abs(over_odds)) / abs(over_odds))
                under_payoff = bet_amount * ((100 + abs(float(under_odds))) / abs(float(under_odds)))

                pot -= bet_amount

                if estimated_total >= line:
                    ##print("Betting the over")
                    if actual_total < line:
                        print("lost the bet")
                        losses += 1
                    else:
                        print("won the best")
                        wins += 1
                        pot += under_payoff
                else:
                    #print("Betting the under")
                    if actual_total > line:
                        print("lost the best")
                        losses += 1
                    else:
                        print("won the best")
                        wins += 1
                        pot += over_payoff

                print("wins:", wins)
                print("losses:", losses)
                print("pot:", pot)

            print("wins:", wins)
            print("losses:", losses)
    
    ## TODO: Go through each game in the backtesting dataset: we need the team names, q1/q2 scores,
    ## total scores, and the betting lines for these games on draftkings.  We also need to get the
    ## calculated scores using the model weights.

main()
