import random
import os
from getpass import getpass
from collections import defaultdict



 

#--------------------Registration of each player------------------------    
def REGISTER_PLAYERS(self):
    print("-----PLAYERS REGISTRATION------")    
    players=[]
    for i in range(1,9):
        while True:
            name=getpass(f"Player {i} Please Enter Your Name: (Hidden): ").strip()
            if name and name not in players:
                players.append(name)
                break
            print("Sorry! Name is Invalid plz enter a valid name")
    os.system('cls' if os.name=='nt' else 'clear')
    return players        


def _assign_roles(self):
        roles = ['Thief']*2 + ['Angel']*1 + ['Citizen']*5
        random.shuffle(roles)
        self.players = {
            name: {'role': role, 'alive': True}
            for name, role in zip(self.player_names, roles)
        }