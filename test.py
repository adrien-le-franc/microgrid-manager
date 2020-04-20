import numpy as np
from simulate import Manager


manager = Manager("data/players.json")
manager.simulate(100)

loads=np.load("data_visualize/load simulation.npy")
bills=np.load("data_visualize/bill simulation.npy")
prices=np.load("data_visualize/price simulation.npy")
batteries1=np.load("data_visualize/battery stock simulation IC SF.npy")
batteries2=np.load("data_visualize/battery stock simulation CS.npy")
scenarios=np.load("data_visualize/scenario simulation.npy")
imbalances=np.load("data_visualize/imbalance simulation.npy")