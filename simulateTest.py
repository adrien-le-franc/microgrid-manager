# python 3

import json


class Manager():
    
    def __init__(self, path_to_player_file): #constructor
        
        self.horizon = 48
        self.dt = 0.5

        self.players = self.initialize_players(path_to_player_file)

    def initialize_players(self, json_file):

        with open(json_file) as f:
            players = json.load(f)

        new_players = {}

        for idx in players:

            mod = __import__("players.{}.player".format(players[idx]["folder"]), 
                fromlist=["Player"])
            Player = getattr(mod, "Player")
            new_player = Player() # if you want to initialize with parameters, you have to distinguish types of players... do we want that ?
            new_players[idx] = {"class":new_player, "type":players[idx]["type"]}

        return new_players