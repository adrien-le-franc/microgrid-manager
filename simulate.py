# python 3

import json
import numpy as np
import random
import os


class Manager():
    
    def __init__(self, path_to_player_file, path_to_price_file):
        
        self.horizon = 48
        self.dt = 0.5
        
        self.nb_tot_players = 0
        self.nb_players = {"charging_station":0,"industrial_consumer":0,"solar_farm":0}

        self.players = self.initialize_players(path_to_player_file)
        self.prices = self.initialize_prices(path_to_price_file)
        self.data_scenario=self.initialize_data_scenario()
        
        self.imbalance=np.zeros((2,self.horizon))
        self.grid_load={"demand": np.zeros(self.horizon), "supply": np.zeros(self.horizon) }
        
        self.scenario={}

    def initialize_players(self, json_file):
        """initialize all players"""

        with open(json_file) as f:
            players = json.load(f)
            
        new_players = {}

        for idx in players:
            
            self.nb_players[players[idx]["type"]] +=1
            self.nb_tot_players+=1

            mod = __import__("players.{}.player".format(players[idx]["folder"]), 
                fromlist=["Player"])
            Player = getattr(mod, "Player")
            new_player = Player() 
            new_players[idx] = {"class":new_player, "type":players[idx]["type"],
                "name":players[idx]["folder"] }
            
        return new_players

    def initialize_prices(self, path_to_price_file):
        """initialize daily prices"""

        prices=np.loadtxt(path_to_price_file) #internal trade, external purchase, external sale
        dico_prices={"internal" : prices[0, :], "external_purchase" : prices[1, :], 
            "external_sale" : prices[2, :]}

        return dico_prices

    def initialize_data_scenario(self):
        """initialize daily scenarios"""
        
        this_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(this_dir, "data")
        dico_data_scenario={}
        
        for idx,dico in self.players.items():
            
            if dico["type"] == "charging_station":
                
                dico_data_scenario[dico["name"]] = np.genfromtxt(os.path.join(data_dir, 
                    dico["name"], "data.csv"), delimiter=";") #departure and arrival time of each car
        
            else:
                dico_data_scenario[dico["name"]] = np.loadtxt(os.path.join(data_dir, 
                    dico["name"], "data.csv"))
            
        return dico_data_scenario
        
## Draw a scenario for the day
    
    def draw_random_scenario(self):
        
        
        for idx,dico in self.players.items():
            
            if dico["type"] == "charging_station":
                # p=random.randint(0,len(self.data_scenario[dico["name"]])/2 -1) 
                p=random.randint(0,99) 
                planning=np.array([self.data_scenario[dico["name"]][:,2*p], self.data_scenario[dico["name"]][:,2*p+1]])
                
                self.scenario[dico["name"]] = planning
                #print(planning)
                
            else:
                self.scenario[dico["name"]] = self.data_scenario[dico["name"]][random.randint(0,len(self.data_scenario[dico["name"]])-1)]




           ##Compute the energy balance on a slot
    def energy_balance(self, time):

        demand = 0
        supply = 0
        

        for idx,dico in self.players.items():
            
            player = dico["class"]
            
            if dico["type"] == "charging_station":
                departure=[0]*4  #departure[i]=1 if the car i leaves the station at t
                arrival=[0]*4    #arrival[i]=1 if the car i arrives in the station at t
                
                for i in range(4):
                    if time==self.scenario[dico["name"]][0,i]:
                        departure[i]=1
                    if time==self.scenario[dico["name"]][1,i]:
                        arrival[i]=1
                
                data_to_player = {"departures":departure , "arrivals":arrival}
                                
                
            else:
                data_to_player = self.scenario[dico["name"]][time]
            
            player.compute_load(time,data_to_player)
            
            load = player.load[time]


            if load >= 0: #if the player needs energy
                demand += load
            else:         #if the player supply energy
                supply -= load
        
        self.grid_load["demand"][time]=demand
        self.grid_load["supply"][time]=supply
        
        return  demand, supply


    ## Compute the bill of each players 
    def compute_bills(self, time, demand, supply):
        total_load=demand-supply    #total load of the grid
        internal_exchange=min(demand,supply)  #what is going to be exchange on the grid
        external_exchange=abs(total_load)   #the quantity of energy in surplus on the grid
        internal_price=self.prices["internal"][time]
        external_selling_price=self.prices["external_sale"][time]
        external_purchasing_price=self.prices["external_purchase"][time]

        if total_load>=0:  #if there is not enough energy on the grid
            
            proportion_internal_demand=internal_exchange/demand
            proportion_internal_supply=1
            
            self.imbalance[0][time] = proportion_internal_demand
            self.imbalance[1][time] = proportion_internal_supply

            for idx,dico in self.players.items():
                
                player = dico["class"]

                load=player.load[time]

                if load>0: #if the player needs energy

                    cost= (internal_price*(proportion_internal_demand) + external_purchasing_price*(1-proportion_internal_demand))*load*self.dt
                            #the players pays in proportion on and off the grid for his demand
                    player.bill[time] += cost

                elif load<0: #if the player supply energy

                    revenue=internal_price*load*self.dt #there is enough demand of engery on the grid
                    player.bill[time] += revenue
        

        else :   #if the offer is too consequent on the grid
            
            proportion_internal_demand=1
            proportion_internal_supply=internal_exchange/supply
            self.imbalance[0][time] = proportion_internal_demand
            self.imbalance[1][time] = proportion_internal_supply
            
            for idx,dico in self.players.items():
            
                player = dico["class"]
                
                
                load=player.load[time]

                if load>0: #if the player needs energy

                    cost=internal_price*load*self.dt  #there is enough energy produced on the grid
                    player.bill[time] += cost

                elif load<0:  #if the player supply energy

                    revenue= (internal_price*(proportion_internal_supply) + external_selling_price*(1-proportion_internal_supply))*load*self.dt
                            #the players pays in proportion of his supply
                    player.bill[time] += revenue
    



## Transmit data to the player

    def give_info(self,t):
        
        
    #the manager informs the price of the last slot
        prices = {"internal" : self.prices["internal"][t],"external_sale" : self.prices["external_sale"][t],"external_purchase" : self.prices["external_purchase"][t]}
            
            
            
        for idx,dico in self.players.items():
            
            player = dico["class"]
            
            if dico["type"] == "charging_station":
                
                # departure=[0]*4  #departure[i]=1 if the car i leaves the station at t
                # arrival=[0]*4    #arrival[i]=1 if the car i arrives in the station at t
                # 
                # for i in range(4):
                #     if t==self.scenario[dico["name"]][0,i]:
                #         departure[i]=1
                #     if t==self.scenario[dico["name"]][1,i]:
                #         arrival[i]=1
                # 
                # data_to_player = {"departures":departure , "arrivals":arrival}
                
                data_to_player = 0
                
                
            else:
                
                data_to_player = self.scenario[dico["name"]][t]
            
            player.observe(t,data_to_player,prices,{"proportion_internal_demand": self.imbalance[0][t],"proportion_internal_supply":self.imbalance[1][t]})
           



## Playing one party 

    def play(self):
        
        self.draw_random_scenario()
        
        
        for t in range(self.horizon): # main loop
            
            demand, supply = self.energy_balance(t)
            self.compute_bills(t, demand, supply)
            self.give_info(t)
    
    def reset(self):
        #reset the attributes of the manager
        self.imbalance=np.zeros((2,self.horizon))
        self.scenario={}
        
        for idx,dico in self.players.items(): #reset the attributes of thes players
            
            player = dico["class"]
            player.reset() 
    

    
    
    def simulate(self,nb_simulation,simulation_name):
        
        ##create a folder
        for name in [simulation_name, simulation_name+"/data_visualize", 
            simulation_name+"/plot"]:
            
            try:
                os.mkdir(name)
            except OSError as err:
                if os.path.isdir(name):
                    pass
                else:
                    print(err)
        
        ##Init tabs infos
        
        
        
        tab_scenario_IC_SF = {}
        tab_scenario_CS = {}
        tab_load = {}
        tab_bill = {}
        tab_battery_stock_IC_SF = {}
        tab_battery_stock_CS = {}
        
        for idx,dico in self.players.items():
            
            name = dico["name"]
            tab_load[name] = np.zeros((nb_simulation,self.horizon))
            tab_bill[name] = np.zeros((nb_simulation,self.horizon))
            
            if dico["type"]=="charging_station":
                tab_scenario_CS[name] = np.zeros((nb_simulation,2,4))
                tab_battery_stock_CS[name] = np.zeros((nb_simulation,4,self.horizon+1))
                
            else:
                tab_scenario_IC_SF[name] = np.zeros((nb_simulation,self.horizon))
                tab_battery_stock_IC_SF[name] = np.zeros((nb_simulation,self.horizon+1))
        
        
        tab_price={"internal" : np.zeros((nb_simulation,self.horizon)), "external_purchase" : np.zeros((nb_simulation,self.horizon)), "external_sale" : np.zeros((nb_simulation,self.horizon))}
        
        
        tab_grid_load = {"demand" : np.zeros((nb_simulation,self.horizon)) , "supply" : np.zeros((nb_simulation,self.horizon))}
        
        
        tab_imbalance = {"demand" : np.zeros((nb_simulation,self.horizon)) , "supply" : np.zeros((nb_simulation,self.horizon))}
        
        
        
        
        for i in range(nb_simulation):
                    
            self.play()
            
            tab_grid_load["demand"][i]=self.grid_load["demand"]
            tab_grid_load["supply"][i]=self.grid_load["supply"]
            
            tab_imbalance["demand"][i] = self.imbalance[0]
            tab_imbalance["supply"][i] = self.imbalance[1]
            
                
            
            for type in ["internal","external_purchase","external_sale"]:
                tab_price[type][i]=self.prices[type]

            
            for idx,dico in self.players.items():
            
                player = dico["class"]
                name = dico["name"]
                
                
                tab_load[name][i] = player.load
                tab_bill[name][i] = player.bill
                
                
                if dico["type"]=="charging_station":
                    
                    tab_scenario_CS[name][i] = self.scenario[name]
                    
                    
                    new_bat = np.concatenate((player.battery_stock["slow"],player.battery_stock["fast"]),axis=1)
                    new_bat = np.transpose(new_bat)
                    
                    tab_battery_stock_CS[name][i] = new_bat
                    
                else:
                    tab_scenario_IC_SF[name][i] = self.scenario[name]
                    
                    
                    tab_battery_stock_IC_SF[name][i] = player.battery_stock
                    
                
            
            
            self.reset()
            
            
        np.save(simulation_name+"/data_visualize/imbalance_simulation",np.array([tab_imbalance]))
        np.save(simulation_name+"/data_visualize/load_simulation",np.array([tab_load]))
        np.save(simulation_name+"/data_visualize/bill_simulation",np.array([tab_bill]))
        np.save(simulation_name+"/data_visualize/price_simulation",np.array([tab_price]))
        np.save(simulation_name+"/data_visualize/battery_stock_simulation_IC_SF",np.array([tab_battery_stock_IC_SF]))
        np.save(simulation_name+"/data_visualize/battery_stock_simulation_CS",np.array([tab_battery_stock_CS]))
        np.save(simulation_name+"/data_visualize/scenario_simulation_IC_SF",np.array([tab_scenario_IC_SF]))
        np.save(simulation_name+"/data_visualize/scenario_simulation_CS",np.array([tab_scenario_CS]))
        np.save(simulation_name+"/data_visualize/grid_load_simulation",np.array([tab_grid_load]))
        