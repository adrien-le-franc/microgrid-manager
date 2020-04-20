# python 3
# this class combines all basic features of a generic player


class Player:

	def __init__(self):
		# some player might not have parameters
		self.parameters = 3

	def take_decision(self, time):
		# TO BE COMPLETED
		return 0

	def compute_load(self, time):
		load = self.take_decision(time)
		# do stuff ?
		return load

	def observe(self, time, data_scenario, price,data_player):
		# save observations for decision making
		pass

	def reset(self):
		# reset all observed data
		pass