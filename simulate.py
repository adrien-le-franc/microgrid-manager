import numpy 


# import the different players

from players.Solar_Farm import SolarFarm
from players.IC import IndustrialConsumer
from players.charging_station import ChargingStation

## Data

L_pv=[0]*48 #photovoltaic production per slot
L_dem=[0]*48 #industrial needs per slot
prices=numpy.loadtxt("prices_class_1.csv")
Planning=[[16,36] for i in range(4)] #departure and arrival of the 4 EV (8 a.m and 6 p.m for everyone for now)


class Manager():
    
    def __init__(self): #constructor
        
        self.day = 24
        self.dt = 0.5
        self.horizon = int(self.day/self.dt) #nb of time steps

        self.players = {"charging_station": ChargingStation(), 
            "solar_farm": SolarFarm(),
            "industrial_site": IndustrialConsumer(0,0)}  #To be modified
            
        self.prices = {"internal" : prices[0, :], "external_purchase" : prices[1, :], "external_sale" : prices[2, :]}
        
    
    

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
    
        internal_exchange=min(demand,supply)  #what is going to be exchange on the grid
        external_exchange=abs(total_load)   #the quantity of energy in surplus on the grid
        internal_price=self.prices["internal"][time]
        external_selling_price=self.prices["external_sale"][time]
        external_purchasing_price=self.prices["external_purchase"][time]

        if total_load>=0:  #if there is not enough energy on the grid

            for name, player in self.players.items():

                load=player.load[time]

                if load>0: #if the player needs energy

                    cost= (internal_price*(internal_exchange/demand) + external_purchasing_price*(external_exchange/demand))*load*dt
                            #the players pays in proportion on and off the grid for his demand
                    player.bill[time] += cost
                    player.information["proportion_internal_demand"][time] = internal_exchange/demand

                elif load<0: #if the player supply energy

                    revenue=internal_price*load*dt #there is enough demand of engery on the grid
                    player.bill[time] += revenue
                    player.information["proportion_internal_supply"][time]=1

        else :   #if the offer is too consequent on the grid

            for name, player in self.players.items():

                load=player.load[time]

                if load>0: #if the player needs energy

                    cost=internal_price*load*dt  #there is enough energy produced on the grid
                    player.bill[time] += cost
                    player.information["proportion_internal_demand"][time] = 1

                elif load<0:  #if the player supply energy

                    revenue= (internal_price*(internal_exchange/supply) + external_selling_price*(external_exchange/supply))*load*dt
                            #the players pays in proportion of his supply
                    player.bill[time] += revenue
                    player.information["proportion_internal_supply"][time]=internal_exchange/supply

    ##Playing one party 

    def play(self):
        
        for name, player in self.players.items():
            player.prices=self.prices
            
        for t in range(self.horizon): # main loop
            load, demand, supply = self.energy_balance(t)
            self.compute_bills(t, load, demand, supply)
