import numpy as np
from simulate import Manager
import time
import visualize as vis
import os

name='Premiere_simulation_1000j'
this_dir = os.path.dirname(os.path.abspath(__file__))
t = time.time()

manager = Manager(os.path.join(this_dir, "data", "players.json"),
	os.path.join(this_dir, "data", "prices.csv"))

manager.simulate(1000,name)


# All npy files are dictionaries (inside a 1 length array)

##Données par joueurs

loads=np.load(name+"/data_visualize/load_simulation.npy",allow_pickle=True) 
# keys : players  -- objects : nb_simul*nb_time_steps

bills=np.load(name+"/data_visualize/bill_simulation.npy",allow_pickle=True)
# keys : players  -- objects : nb_simul*nb_time_steps

batteries_IC_SF=np.load(name+"/data_visualize/battery_stock_simulation_IC_SF.npy",allow_pickle=True)
# keys : players (except CS)  -- objects : nb_simul*(nb_time_steps+1)

batteries_CS=np.load(name+"/data_visualize/battery_stock_simulation_CS.npy",allow_pickle=True) 
# keys : players (only CS) -- objects : nb_simul*nb_cars*(nb_time_steps+1)

scenarios_IC_SF=np.load(name+"/data_visualize/scenario_simulation_IC_SF.npy",allow_pickle=True) 
# keys : players (except CS)  -- objects : nb_simul*nb_time_steps

scenarios_CS=np.load(name+"/data_visualize/scenario_simulation_CS.npy",allow_pickle=True) 
# keys : players (only CS)  -- objects : nb_simul*2(departures/arrivals)*nb_cars



##Données communes

imbalances=np.load(name+"/data_visualize/imbalance_simulation.npy",allow_pickle=True)
# keys : demand/supply  -- objects : nb_simul*nb_time_steps

grid_load=np.load(name+"/data_visualize/grid_load_simulation.npy",allow_pickle=True)
# keys : demand/supply  -- objects : nb_simul*nb_time_steps

prices=np.load(name+"/data_visualize/price_simulation.npy",allow_pickle=True)
# keys : internal/external_purchase/external_sale  -- objects : nb_simul*nb_time_steps



print(time.time()-t)

###Affichage des graphes :

#affichage chargement



vis.plottotal(loads[0],'kW','Average loads for player','Loads','chargement',name)

#affichage facture"

vis.plottotal(bills[0],'€','Average bills for player','Bills','facture',name)

#affichage batterie IC, SF"

vis.plottotal(batteries_IC_SF[0],'kWh','Average battery level for player','Level','battery',name)

#affichage batterie CS"

vis.plotCS(batteries_CS[0],'kWh','Average battery level for player','Level', 'battery',name)

#affichage scenario IC_SF"

vis.plottotal(scenarios_IC_SF[0],'kW','Parameter for player','Sunlight/Demand','parametre',name)

#affichage imbalances"

vis.plot_2(imbalances[0],'%','Imbalance between demand and supply on the grid','figure_imbalances.png',name)

#affichage grid_load"

vis.plot_2(grid_load[0],'kW','Internal energy balance','figure_grid_load.png',name)

#affichage prices"

vis.plot_3(prices[0],'€/kWh',"Electricity price ",'figure_prices.png',name)

print(time.time()-t)