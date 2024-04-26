from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import csv
import os
from score_calculation import calculate_scores

app = Flask(__name__)
CORS(app)

# Path to the CSV files
PARTICIPANTS_CSV = 'participants.csv'
MATCHES_CSV = 'matches.csv'

def create_csv_if_not_exists(file_path, fieldnames=[]):
    if not os.path.exists(file_path):
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

create_csv_if_not_exists(PARTICIPANTS_CSV)
create_csv_if_not_exists(MATCHES_CSV)

def read_csv(file_path):
    data = []
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return data

def write_csv(file_path, data, fieldnames):
    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
    except Exception as e:
        print(f"An error occurred: {e}")


def add_csv(file_path, data, fieldnames):
    try:
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            for row in data:
                writer.writerow(row)
    except Exception as e:
        print(f"An error occurred: {e}")




@app.route('/get-participants', methods=['GET'])
def get_participants():
    participants = read_csv(PARTICIPANTS_CSV)
    return jsonify(participants)

@app.route('/get-participants-sort-score', methods=['GET'])
def get_participants_sort_score():
    participants = read_csv(PARTICIPANTS_CSV)
    sorted_participants = sorted(participants, key=lambda x: float(x['score']), reverse=True)
    return jsonify(sorted_participants)

@app.route('/get-participants-sort-name', methods=['GET'])
def get_participants_sort_name():
    participants = read_csv(PARTICIPANTS_CSV)
    sorted_participants = sorted(participants, key=lambda x: x['name'])
    return jsonify(sorted_participants)

@app.route('/add-participant', methods=['POST'])
def add_participant():
    new_participant = request.json
    participants = read_csv(PARTICIPANTS_CSV)

    # Generate a unique ID
    if participants:
        max_id = max(int(participant['id']) for participant in participants)
        new_id = max_id + 1
    else:
        new_id = 1  # Start from 1 if no participants are present

    new_participant['id'] = new_id

    fieldnames = ['id', 'name', 'score']
    add_csv(PARTICIPANTS_CSV, [new_participant], fieldnames)
    return jsonify({'message': 'Participant added successfully', 'id': new_id}), 200

@app.route('/remove-participant', methods=['POST'])
def remove_participant():
    participant_id = request.json['id']
    participants = read_csv(PARTICIPANTS_CSV)
    participants = [p for p in participants if p['id'] != participant_id]
    fieldnames = ['id', 'name', 'score']
    write_csv(PARTICIPANTS_CSV, participants, fieldnames)
    return jsonify({'message': 'Participant removed successfully'}), 200

@app.route('/edit-participant', methods=['POST'])
def edit_participant():
    updated_participant = request.json
    participants = read_csv(PARTICIPANTS_CSV)
    for p in participants:
        if p['id'] == updated_participant['id']:
            p['name'] = updated_participant['name']
            p['score'] = updated_participant['score']
            break
    fieldnames = ['id', 'name', 'score']
    write_csv(PARTICIPANTS_CSV, participants, fieldnames)
    return jsonify({'message': 'Participant updated successfully'}), 200

@app.route('/get-matches', methods=['GET'])
def get_matches():
    matches = read_csv(MATCHES_CSV)
    return jsonify(matches)

@app.route('/add-match', methods=['POST'])
def add_match():
    new_match = request.json
    fieldnames = ['match_id', 'round_id', 'participant1_id', 'participant2_id', 'participant1_wins', 'participant2_wins']
    add_csv(MATCHES_CSV, [new_match], fieldnames)
    return jsonify({'message': 'Match added successfully'}), 200

@app.route('/add-matches', methods=['POST'])
def add_matches():
    new_matches = request.json
    fieldnames = ['match_id', 'round_id', 'participant1_id', 'participant2_id', 'participant1_wins', 'participant2_wins']
    add_csv(MATCHES_CSV, new_matches, fieldnames)
    return jsonify({'message': 'Match added successfully'}), 200

@app.route('/remove-match', methods=['POST'])
def remove_match():
    match_id = request.json['match_id']
    matches = read_csv(MATCHES_CSV)
    matches = [m for m in matches if m['match_id'] != match_id]
    fieldnames = ['match_id', 'round_id', 'participant1_id', 'participant2_id', 'participant1_wins', 'participant2_wins']
    write_csv(MATCHES_CSV, matches, fieldnames)
    return jsonify({'message': 'Match removed successfully'}), 200

@app.route('/edit-match', methods=['POST'])
def edit_match():
    updated_match = request.json
    matches = read_csv(MATCHES_CSV)
    for m in matches:
        if m['match_id'] == updated_match['match_id']:
            m.update(updated_match)
            match_found = True
            break
    if not match_found:
        return jsonify({'message': 'Match not found'}), 404
    fieldnames = ['match_id', 'round_id', 'participant1_id', 'participant2_id', 'participant1_wins', 'participant2_wins']
    write_csv(MATCHES_CSV, matches, fieldnames)
    return jsonify({'message': 'Match updated successfully'}), 200

@app.route('/recalculate-scores', methods=['POST'])
def recalculate_scores():
    participants = read_csv(PARTICIPANTS_CSV)
    matches = read_csv(MATCHES_CSV)
    match_data = [(
        int(m['participant1_id']) - 1, 
        int(m['participant2_id']) - 1, 
        float(m['participant1_wins']), 
        float(m['participant2_wins'])
    ) for m in matches]

    scores = calculate_scores(match_data, len(participants))
    for p, s in zip(participants, scores):
        p['score'] = s

    # Write updated scores back to CSV
    fieldnames = ['id', 'name', 'score']
    write_csv(PARTICIPANTS_CSV, participants, fieldnames)

    return jsonify({'message': 'Scores recalculated successfully'}), 200


# from pairings import get_pairings
@app.route('/get-pairings', methods=['GET'])
def get_pairings_this():
    pairings = [[1,2],[2,1]]
    return pairings
    # participants = read_csv(PARTICIPANTS_CSV)
    # matches = read_csv(MATCHES_CSV)
    # match_data = [(
    #     int(m['participant1_id']) - 1, 
    #     int(m['participant2_id']) - 1, 
    #     float(m['participant1_wins']), 
    #     float(m['participant2_wins'])
    # ) for m in matches]

    # matrix = get_matrix(match_data, len(participants))
    # scores = calculate_scores(match_data, len(participants))
    # pairings = get_pairings(scores, matrix)
    # return jsonify(pairings)


@app.route('/')
def swiss_tourney_home():
    return render_template('swiss.html', title='Swiss Tourney')

if __name__ == '__main__':
    app.run(debug=True)

