import numpy as np


# import the different players

from players.solar_farm import Solar_farm
from players.industrial_site import Industrial_site
from players.charging_station import Charging_station


class Manager():
    
    def __init__(self): #constructor
        
        self.day = 24
        self.dt = 0.5
        self.horizon = int(day/dt) #nb of time steps

        self.players = {"charging_station": Charging_station(), 
            "solar_farm": Solar_farm(),
            "industrial_site": Industrial_site()}  #To be modified
            
        self.prices = np.zeros(48) # no external exchanges for now.
        
    
        ## Data

    L_pv=[0]*self.horizon  #photovoltaic production per slot
    L_dem=[0]*self.horizon  #industrial needs per slot
    Price=[0]*self.horizon #price reference per slot
    Planning=[[16,36] for i in range(4)] #departure and arrival of the 4 EV (8 a.m and 6 p.m for everyone for now)


    ##Compute the energy balance on a slot
    def energy_balance(self, time):

        total_load = 0
        demand = 0
        supply = 0

        for name, player in self.players.items():

            player.compute_load(time)
            load = player.load[time]

            if load >= 0: #if the player needs energy
                demand += load
            else:         #if the player supply energy
                supply -= load
            total_load += load   #measure the balance

        return total_load, demand, supply


    ## Compute the bill of each players 
    def compute_bills(self, time, load, demand, supply):

        purchase = self.prices[time]*demand*self.dt  #sum of purchases on the grid
        sale = self.prices[time]*supply*self.dt  #sum of sales on the grid

        for name, player in self.players.items():
            
            
            #first idea for setting the prices :
            
            if demand != 0:  
                player.information["grid_buy_price"][time+1] = purchase / (demand*self.dt) #purchasing price per unit of energy
            if supply != 0:
                player.information["grid_sell_price"][time+1] = sale / (supply*self.dt) #selling price per unit of energy
    
            load = player.load[time]
            if load == 0:
                continue

            if load >= 0:  #if the player needs energy
                cost = purchase * load / demand   #the player pays its proportion of purchase
                player.bill[time] += cost
                player.information["my_buy_price"][time+1] = purchase / (demand*self.dt)
            else:   #if the player supply energy
                revenue = sale * load / supply
                player.bill[time] += revenue  #the player earns its proportion of supply
                player.information["my_sell_price"][time+1] = sale / (supply*self.dt)

    ##Playing one party 

    def play(self):
        #non flexible varibale to introduce here
        for t in range(self.horizon): # main loop
            load, demand, supply = self.energy_balance(t)
            self.compute_bills(t, load, demand, supply)
        
    

    

