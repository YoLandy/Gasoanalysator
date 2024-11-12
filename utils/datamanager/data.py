import json


class DataManager:
    CONFIG_FILEPATH = "data.json"

    def get_data():
        with open(DataManager.CONFIG_FILEPATH) as f:
            data = json.load(f)
        return data

    def set_data(data):
        with open(DataManager.CONFIG_FILEPATH, "w") as outfile:
            json.dump(data, outfile, indent=4)

    def get_param(param_name):
        data = DataManager.get_data()
        return data[param_name]

    def save_param(param_name, param):
        data = DataManager.get_data()
        data[param_name] = param
        DataManager.set_data(data)
