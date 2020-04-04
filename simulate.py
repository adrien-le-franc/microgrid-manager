import numpy as np


# importer les differents acteurs

from players.solar_farm import Solar_farm
from players.industrial_site import Industrial_site
from players.charging_station import Charging_station


class Manager():
    
    def __init__(self): #constructeur
        
        self.day = 24
        self.dt = 0.5
        self.nb_time_steps = int(jour/dt)

        self.players = {"charging_station": Charging_station(data_j1), 
            "solar_farm": Solar_farm(data_j2),
            "industrial_site": Industrial_site()}
            
        self.prices = np.zeros(48)
        
    

    

