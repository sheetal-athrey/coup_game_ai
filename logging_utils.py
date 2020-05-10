import json


def update_json(path_to_json, json_update_info):
    with open(path_to_json, "r+") as json_file:
        data = json.load(json_file)

    data.extend(json_update_info)

    with open(path_to_json, "w+") as json_file:
        json.dump(data, json_file)
