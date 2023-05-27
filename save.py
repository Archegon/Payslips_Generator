import json


class Savefile:
    def __init__(self, path):
        self.path = path
        self.save_dict = {}

    def save(self):
        with open(self.path, 'w') as save_file:
            json.dump(self.save_dict, save_file, indent=4)

    def load(self):
        try:
            with open(self.path, 'r') as save_file:
                self.save_dict = json.load(save_file)
        except FileNotFoundError:
            try:
                with open(self.path, 'w+') as save_file:
                    self.save_dict = json.load(save_file)
            except json.decoder.JSONDecodeError:
                self.save_dict = {}
        except json.decoder.JSONDecodeError:
            self.save_dict = {}

        return self.save_dict

    def update(self, save_dict):
        self.save_dict = self.load()
        self.save_dict.update(save_dict)
        self.save()