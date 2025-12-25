import json
import os
import csv

def lambda_handler(event, context):
    file_name = "calculated_weights.csv"  # Default to 'default_file.txt' if not specified
    scores = [0, 0, 0]

    body = event["queryStringParameters"]

    team_1 = body.get('team1', '')
    team_2 = body.get('team2', '')
    score_1 = float(body.get('score1', ''))
    score_2 = float(body.get('score2', ''))

    try:
        # Construct the full path to the file within the Lambda deployment package
        # Files are typically placed in the same directory as the lambda_handler.py
        file_path = os.path.join(os.path.dirname(__file__), file_name)

        with open(file_path, 'r', newline='') as f:
            data_file_reader = csv.DictReader(f)

            #content = []
            #for row in data_file_reader:
            #    scores.append(row[' slope'])

            
            for row in data_file_reader:
                if row['team'] == team_1:
                    slope = float(row[' slope'])
                    print(slope)
                    yintercept = float(row[' yintercept'])
                    ## Calculate the score for team 1
                    scores[0] = slope * score_1 + yintercept

                if row['team'] == team_2:
                    slope = float(row[' slope'])
                    yintercept = float(row[' yintercept'])
                    ## Calcuate the score for team 2
                    scores[1] = slope * score_2 + yintercept

            scores[2] = scores[0] + scores[1]  

        response_body = {
            'message': f'Successfully read file: {file_name}',
            'content': scores
        }
        status_code = 200

    except FileNotFoundError:
        response_body = {
            'message': f'Error: File "{file_name}" not found.'
        }
        status_code = 404
    except Exception as e:
        response_body = {
            'message': f'An unexpected error occurred: {str(e)}'
        }
        status_code = 500

    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(response_body)
    }

