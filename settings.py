import yaml


class Settings(dict):
    def __init__(self, file_name: str):
        with open(file_name, 'r') as f:
            super().__init__(yaml.load(f, yaml.Loader))

