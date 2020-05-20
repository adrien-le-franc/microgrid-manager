import os
import json
import argparse
import git
from git import Repo



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--players', type=str, required=True, 
        help='path to players.json file')
    args = parser.parse_args()
    
    this_dir = os.path.dirname(os.path.abspath(__file__))
    
    with open(args.players) as f:
            players = json.load(f)
    
    for key, val in players.items():     
        repo = Repo(os.path.join(this_dir, "players", val['folder']))
        repo.remotes.origin.pull()  #pull each player
