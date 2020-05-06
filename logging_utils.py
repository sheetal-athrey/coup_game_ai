import json


def update_json(path_to_json, initial_cards, winner_index, player_types):
    print("path_to_json", path_to_json)
    with open(path_to_json, "r+") as json_file:
        data = json.load(json_file)
        print([initial_cards, winner_index, player_types])
    data.append([initial_cards, winner_index, player_types])
        # json.dumps(data, json_file)

    with open(path_to_json, "w+") as json_file:
        data = json.dump(data, json_file)
        print("DATA dumps", data)