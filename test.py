from simulate import Manager


manager = Manager("data/players.json", "data/prices.csv")
manager.players["1"]["player"].reset()
print("tests passed !")