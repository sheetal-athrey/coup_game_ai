import json


def update_json(path_to_json, initial_cards, winner_index, player_types):
    with open(path_to_json, "r+") as json_file:
        data = json.load(json_file)

    data.append([initial_cards, winner_index, player_types])

    with open(path_to_json, "w+") as json_file:
        json.dump(data, json_file)
