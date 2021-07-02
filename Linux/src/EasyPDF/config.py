from configparser import ConfigParser


class Config():
    def __init__(self, configFile):
        self.config = ConfigParser()
        self.config.read(configFile)
        print(list(self.config.keys()))

    def __getitem__(self, key):
        return self.config[key]


if __name__ == "__main__":
    config = Config("../config.ini")
