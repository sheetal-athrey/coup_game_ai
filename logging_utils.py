import json


def update_json(path_to_json, initial_cards, winner_index, player_types):
    data = json.load(path_to_json)
    data.append([initial_cards, winner_index, player_types])
    json.dumps(data, path_to_json)
