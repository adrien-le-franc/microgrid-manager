from player import Player


parameters = 0
player = Player(parameters)

for t in range(48):
	load = player.compute_load(t)
	player.observe(t, 0, 0)

player.reset()

print("tests passed !")