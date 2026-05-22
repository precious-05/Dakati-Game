Project Progress: Dakati Game  
Module: Player_Registration(), Role_Assignment(), Thief_Reveal(), Role_Introduction()
Work Started: '3/05/2025'

___________________________________________________________________________________________

Module Overview:
The Player_Registration() method handles the secure registration of 8 unique players.
The _assign_roles() method randomly distributes game roles.
The _reveal_thieves() establishes thief partnerships.
The _introduce_roles() privately reveals roles to each player.

Key Features:
1: Hidden Input___ Names collected secretly using "getpass"
2: Validation___ Ensures names are non-empty and unique
3: Random Role Assignment___ Fisher-Yates shuffle for fairness
4: Secure Role Reveal___ Private console display with auto-clear
5: Thief Networking___ Establishes known thief relationships

___________________________________________________________________________________________
Implementation Details:

PYTHON Code Snippet:

def register_players(self):
    print(" PLAYER REGISTRATION \n")
    players = []
    for i in range(1, 9):
        while True:
            name = getpass(f"Player {i}, enter your name (hidden) ").strip()
            if name and name not in players:
                players.append(name)
                break
            print("Sorry!! Invalid name.. It Must be unique and non-empty")
    os.system('cls' if os.name == 'nt' else 'clear')
    return players

def _assign_roles(self):
    roles = ['Thief']*2 + ['Angel']*1 + ['Citizen']*5
    random.shuffle(roles)
    self.players = {
        name: {'role': role, 'alive': True}
        for name, role in zip(self.player_names, roles)
    }

def _reveal_thieves(self):
    thieves = [name for name, data in self.players.items() 
             if data['role'] == 'Thief']
    for thief in thieves:
        self.players[thief]['known_thieves'] = [
            t for t in thieves if t != thief
        ]

def _introduce_roles(self):
    for name, data in self.players.items():
        os.system('cls' if os.name == 'nt' else 'clear')
        if data['role'] == 'Thief':
            print(f"{name}: You are a THIEF")
            print(f"Your partner: {self.players[name]['known_thieves'][0]}")
        else:
            print(f"{name}: You are a {data['role'].upper()}")
        input("\nPress Enter to hide your role...")
    os.system('cls' if os.name == 'nt' else 'clear')

_________________________________________________________________________________________
"Libraries and Functions Used"
Component	|Purpose	|Documentation |Link
getpass	    |Secure name input         |Python Docs
os.system()	|Console clearing          |Python Docs
random.shuffle()|Fair role distribution |Python Docs
dict comprehension|Efficient data mapping|Python Docs
list comprehension|Thief identification |Python Docs
input()     |Role confirmation         |Python Docs
_________________________________________________________________________________________             

Technical Decisions
Security Architecture:
"getpass + console clearing maintains complete anonymity"

Thief Networking:
"known_thieves attribute enables coordinated gameplay"

Phased Role Reveal:
"Individual console clears prevent accidental role exposure"

Validation Framework:
"Multi-layer checks ensure game integrity"

_________________________________________________________________________________________       
Next Steps
Game Loop Development:
"Implementing voting mechanics"

_________________________________________________________________________________________       

Dependencies
Python 3.6+ "For security and randomization features"