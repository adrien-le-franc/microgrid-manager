# python 3
#
# script for initializing the game from a players.json file
# optional improvements: git clone, perform tests


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
		
		# initialize data folders
		try:
			os.makedirs(os.path.join(this_dir, "data", val['folder'])) 
		except OSError as err:
			if os.path.isdir(os.path.join(this_dir, "data", val['folder'])):
				pass
			else:
				print(err)

		# initialize player folders, git clone & test ?
		try:
			os.makedirs(os.path.join(this_dir, "players", val['folder'])) 
			
		except OSError as err:
			if os.path.isdir(os.path.join(this_dir, "players", val['folder'])):
				pass
			else:
				print(err)
		Repo.clone_from(val['url'],os.path.join(this_dir, "players", val['folder'])) #clone each player
			
		
