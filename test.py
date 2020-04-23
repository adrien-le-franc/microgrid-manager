import numpy as np
from simulate import Manager
import time

t = time.time()



manager = Manager("data/players.json","data/prices.csv")
manager.simulate(100)


# All npy files are dictionaries (inside a 1 length array)

##Données par joueurs

loads=np.load("data_visualize/load_simulation.npy") 
# keys : players  -- objects : nb_simul*nb_time_steps

bills=np.load("data_visualize/bill_simulation.npy") 
# keys : players  -- objects : nb_simul*nb_time_steps

batteries_IC_SF=np.load("data_visualize/battery_stock_simulation_IC_SF.npy") 
# keys : players (except CS)  -- objects : nb_simul*(nb_time_steps+1)

batteries_CS=np.load("data_visualize/battery_stock_simulation_CS.npy") 
# keys : players (only CS) -- objects : nb_simul*nb_cars*(nb_time_steps+1)

scenarios_IC_SF=np.load("data_visualize/scenario_simulation_IC_SF.npy") 
# keys : players (except CS)  -- objects : nb_simul*nb_time_steps

scenarios_CS=np.load("data_visualize/scenario_simulation_CS.npy") 
# keys : players (only CS)  -- objects : nb_simul*2(departures/arrivals)*nb_cars




##Données communes

imbalances=np.load("data_visualize/imbalance_simulation.npy")
# keys : demand/supply  -- objects : nb_simul*nb_time_steps

grid_load=np.load("data_visualize/grid_load_simulation.npy")
# keys : demand/supply  -- objects : nb_simul*nb_time_steps

prices=np.load("data_visualize/price_simulation.npy")
# keys : internal/external_purchase/external_sale  -- objects : nb_simul*nb_time_steps



print(time.time()-t)


