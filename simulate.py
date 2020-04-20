# python 3

import json
import numpy as np
import random

## Data
prices=np.loadtxt("data/prices.csv") #internal prices, external purchase prices, external sale prices

pv_scenarios=np.loadtxt("data/pv.csv") #photovoltaic production per slot, 100 scenarios
ldem_scenarios=np.loadtxt("data/load.csv")  #industrial needs per slot, 100 scenarios
planning_scenarios=np.genfromtxt("data/t_dep_arr.csv",delimiter= ";") #departure and arrival time of each car, 100 scenarios

class Manager():
    
    def __init__(self, path_to_player_file): #constructor
        
        self.horizon = 48
        self.dt = 0.5
        
        self.nb_players = 0
        self.details_players = {"charging_station":0,"industrial_consumer":0,"solar_farm":0}

        self.players = self.initialize_players(path_to_player_file)
        
        
        self.prices = {"internal" : prices[0, :], "external_purchase" : prices[1, :], "external_sale" : prices[2, :]}
        self.imbalance=np.zeros((2,self.horizon))
        self.scenario={"planning":np.zeros((2,4)),"sunshine":np.zeros(self.horizon),"industrial demand":np.zeros(self.horizon)}
        
        

    def initialize_players(self, json_file):

        with open(json_file) as f:
            players = json.load(f)
            

        new_players = {}

        for idx in players:
            
            self.details_players[players[idx]["type"]] +=1
            
            self.nb_players+=1
            mod = __import__("players.{}.player".format(players[idx]["folder"]), 
                fromlist=["Player"])
            Player = getattr(mod, "Player")
            new_player = Player() # if you want to initialize with parameters, you have to distinguish types of players... do we want that ?
            
            new_players[idx] = {"class":new_player, "type":players[idx]["type"]}
            

        return new_players
        

    def initialize_prices(self, path_to_price_file):
        pass
        
           ##Compute the energy balance on a slot
    def energy_balance(self, time):

        demand = 0
        supply = 0

        for idx,dico in self.players.items():
            
            player = dico["class"]

            player.compute_load(time)
            load = player.load[time]

            if load >= 0: #if the player needs energy
                demand += load
            else:         #if the player supply energy
                supply -= load

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
            proportion_internal_supply=internal_exchange/demand
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
    
## Draw a scenario for the day
    
    def draw_random_scenario(self):
        
        pv=pv_scenarios[random.randint(0,len(pv_scenarios)-1)] #sunshine data
        ldem=ldem_scenarios[random.randint(0,len(ldem_scenarios)-1)] #industrial consumer need 
        p=random.randint(0,len(planning_scenarios[0])/2 -1) 
        planning=np.array([planning_scenarios[:,2*p], planning_scenarios[:,2*p+1]]) #departure and arrival of each car
        self.scenario["planning"]=planning
        self.scenario["sunshine"]=pv
        self.scenario["industrial demand"]=ldem
        
        return pv,ldem,planning


## Transmit data to the player

    def give_info(self,t,pv,ldem,planning):
        data_scenario = { "sun" : pv[t],"demand" : ldem[t],"departures" : planning[0], "arrivals" : planning[1]}
        
        if t>0:
            prices = {"internal" : self.prices["internal"][t-1],"external_sale" : self.prices["external_sale"][t-1],"external_purchase" : self.prices["external_purchase"][t-1]}
            
            
            
        for idx,dico in self.players.items():
            
            player = dico["class"]
            
            if t>0:
                player.observe(t,data_scenario,prices,{"proportion_internal_demand": self.imbalance[0][t-1],"proportion_internal_supply":self.imbalance[1][t-1]})
            else:
                player.observe(t,data_scenario,{},{})



## Playing one party 

    def play(self):
        
        pv,ldem,planning=self.draw_random_scenario()
        
            
        for t in range(self.horizon): # main loop
            
            self.give_info(t,pv,ldem,planning)
            demand, supply = self.energy_balance(t)
            self.compute_bills(t, demand, supply)

    
    def reset(self):
        
        self.imbalance=np.zeros((2,self.horizon))
        self.scenario={"planning":np.zeros((2,4)),"sunshine":np.zeros(self.horizon),"industrial demand":np.zeros(self.horizon)}
        
        for idx,dico in self.players.items():
            
            player = dico["class"]
            player.reset() 
    
    
    
    def simulate(self,nb_simulation):
        
        # keys={"charging_station":0,"solar_farm":1,"industrial_consumer":2}
        
        tab_load=np.zeros((self.nb_players,nb_simulation,self.horizon))
        tab_bill=np.zeros((self.nb_players,nb_simulation,self.horizon))
        
        tab_price={"internal" : np.zeros((nb_simulation,self.horizon)), "external_purchase" : np.zeros((nb_simulation,self.horizon)), "external_sale" : np.zeros((nb_simulation,self.horizon))}
        
        
        tab_battery_stock_IC_SF = np.zeros((self.details_players["industrial_consumer"]+self.details_players["industrial_consumer"],nb_simulation,self.horizon+1))
        
        tab_battery_stock_CS = np.zeros((self.details_players["charging_station"],nb_simulation,4,self.horizon+1))
        
        tab_scenario= {"planning":np.zeros((nb_simulation,2,4)),"sunshine":np.zeros((nb_simulation,self.horizon)),"industrial demand":np.zeros((nb_simulation,self.horizon))}
        
        tab_imbalance = np.zeros((nb_simulation,2,self.horizon))
        
        for i in range(nb_simulation):
                    
            self.play()
            
            
            for type in ["planning","sunshine","industrial demand"]:
                tab_scenario[type][i]=self.scenario[type]
                
            tab_imbalance[i] = self.imbalance
            
            for idx,dico in self.players.items():
            
                player = dico["class"]
                
                
                tab_load[int(idx), i, :] = player.load
                tab_bill[int(idx), i, :] = player.bill
                
                if dico["type"]=="charging_station":
                    
                    new_bat = np.concatenate((player.battery_stock["slow"],player.battery_stock["fast"]),axis=1)
                    
                    new_bat = np.transpose(new_bat)
                    
                    tab_battery_stock_CS[int(idx)-self.details_players["industrial_consumer"]-self.details_players["industrial_consumer"],i,:,:] = new_bat
                else:
                    tab_battery_stock_IC_SF[int(idx),i,:] = player.battery_stock
                    
                
            for type in ["internal","external_purchase","external_sale"]:
                tab_price[type][i]=self.prices[type]
                    
            
            self.reset()
            
            
        np.save("data_visualize/imbalance simulation",tab_imbalance)
        np.save("data_visualize/load simulation",tab_load)
        np.save("data_visualize/bill simulation",tab_bill)
        np.save("data_visualize/price simulation",tab_price)
        np.save("data_visualize/battery stock simulation IC SF",tab_battery_stock_IC_SF)
        np.save("data_visualize/battery stock simulation CS",tab_battery_stock_CS)
        np.save("data_visualize/scenario simulation",tab_scenario)
        np.save("data_visualize/scenario simulation",tab_scenario)
        

