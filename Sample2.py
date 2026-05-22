import random  #This provides access to randomization functions and will used to shuffle the roles randomly
import os  #will used to interact with the operating system such as clearing the screen
from getpass import getpass  #will b used to take input from players without showing it on the screen ...for secrecy in roles..........
from collections import defaultdict  # A dictionary subclass that returns a default value if key is missing ...used for counting votes easily....



class DakatiGame:
    def __init__(self):
        #it Clears the terminal screen at the beginning of the game
        os.system('cls' if os.name == 'nt' else 'clear')  #it uses 'cls' on Windows and 'clear' on Linux/macOs.........

        print("--------------Welcome to the Dakati Game--------------")
        print("-----------A social deduction game for exactly 8 players----------\n")

        #it will gett and store names of all 8 players
        self.player_names = self._register_players()

        #this dictionary to store player data "role and alive status"
        self.players = {}

        #this List to store eliminated players
        self.eliminated = []

        #to keep track of votes in each round, initialized to 0 for missing keys automatically
        self.current_votes = defaultdict(int)

        #Target selected by thieves "to be killed"
        self.thieves_target = None

        #player protected by the angel guesss
        self.angel_choice = None

        #track current round number of game.....s
        self.round = 1

        #assign roles like Thief, Angel, Citizen randomly to players......
        self._assign_roles()

        # Allow thieves to know their partner thief secretly
        self._reveal_thieves()

        # Introduce roles to each player one by one privately
        self._introduce_roles()

    def _register_players(self):
        print("------- PLAYER REGISTRATION ------\n")
        players = []
        for i in range(1, 9):
            while True:
                name = getpass(f"Player {i}, enter your name (hidden): ").strip()
                if name and name not in players:
                    players.append(name)
                    break
                print("Invalid name! Must be unique and non-empty")
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







    def _voting_phase(self):
        print(f"\n------- ROUND {self.round}: VOTING PHASE ---------")
        self.current_votes = defaultdict(int)
        alive_players = [name for name, data in self.players.items() 
                        if data['alive']]

        for voter in alive_players:
            options = [p for p in alive_players if p != voter]
            
            if self.players[voter]['role'] == 'Thief':
                partner = self.players[voter]['known_thieves'][0]
                options = [p for p in options if p != partner]
            
            vote = self._get_hidden_choice(
                f"{voter}, vote to eliminate:", 
                voter, 
                options
            )
            self.current_votes[vote] += 1

        if self.current_votes:
            max_votes = max(self.current_votes.values())
            candidates = [p for p, v in self.current_votes.items() if v == max_votes]
            eliminated = random.choice(candidates) if len(candidates) > 1 else candidates[0]
            
            if self.players[eliminated]['role'] == 'Citizen':
                print("\nMasoom citizen mar gaya! (Innocent citizen died!)")
            elif self.players[eliminated]['role'] == 'Thief':
                print("\nEk chor mar gaya! (A thief died!)")
            else:
                print("\nAngel bhi mar gaya! (Angel died!)")
            
            self._eliminate(eliminated, "voting")
            return eliminated
        return None

    def _thieves_phase(self):
        thieves = [name for name, data in self.players.items() 
                 if data['alive'] and data['role'] == 'Thief']
        if not thieves:
            return

        targets = [name for name, data in self.players.items() if data['alive']]
        
        print("\n=== THIEVES' PHASE ===")
        print("All players close your eyes!")
        input("Press Enter when ready...")
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Thieves {' and '.join(thieves)} open your eyes!")
        print("Choose target:", ', '.join(targets))
        
        self.thieves_target = input("Target to kill: ").strip()
        while self.thieves_target not in targets:
            print("Invalid target!")
            self.thieves_target = input("Target to kill: ").strip()
        
        print("Thieves close your eyes!")
        input("Press Enter to continue...")

    def _angel_phase(self):
        angel = next((name for name, data in self.players.items() 
                     if data['alive'] and data['role'] == 'Angel'), None)
        if not angel or not self.thieves_target:
            return

        if not self.players[self.thieves_target]['alive']:
            return

        print("\n=== ANGEL'S PHASE ===")
        print("Angel open your eyes!")
        input("Press Enter when ready...")
        
        options = [name for name, data in self.players.items() if data['alive']]
        
        self.angel_choice = self._get_hidden_choice(
            f"Angel {angel}, choose someone to save (can choose anyone):",
            angel,
            options
        )

        if self.angel_choice == self.thieves_target:
            print("\nJo chor citizen ko marna chahte the wo angel ki wja se bach gaya")
            print("(The citizen thieves wanted to kill was saved by Angel!)")
        else:
            if self.players[self.thieves_target]['role'] in ['Citizen', 'Angel']:
                print("\nAngel ne galat guess kia! Masoom citizen mar gaya!")
                print("(Angel guessed wrong! Innocent citizen died!)")
                self._eliminate(self.thieves_target, "thieves")
                
                if self.thieves_target == angel:
                    print("\nAngel khud ko nahi bacha paya! Angel mar gaya!")
                    print("(Angel failed to save themselves! Angel died!)")

        print("Angel close your eyes ")
        input("Press Enter to continue...")

    def _get_hidden_choice(self, prompt, player, options):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{player}'s turn")
        print(prompt)
        print("Options:", ", ".join(options))
        
        while True:
            choice = getpass("Your choice (hidden): ").strip()
            if choice in options:
                return choice
            print("Invalid choice! Try again.")

    def _eliminate(self, player, reason):
        self.players[player]['alive'] = False
        self.eliminated.append(player)
        
        if player == self.angel_choice and reason == "thieves":
            print(f"\n{player} Angel ne khud ko nahi bacha saka or mar gaya")
            print(f"({player} Angel failed to save themselves and died")

    def _check_win_conditions(self):
        alive_thieves = sum(1 for data in self.players.values() 
                          if data['alive'] and data['role'] == 'Thief')
        alive_citizens = sum(1 for data in self.players.values() 
                            if data['alive'] and data['role'] in ['Citizen', 'Angel'])

        if alive_thieves == 0:
            print("\n-------CITIZENS WIN! All thieves eliminated-------")
            return True
        elif alive_thieves >= alive_citizens:
            print("\n------THIEVES WIN! They outnumber citizens-------")
            return True
        return False

    def play(self):
        while True:
            print(f"\n------ROUND {self.round}------")
            
            eliminated_in_voting = self._voting_phase()
            self._thieves_phase()
            self._angel_phase()
            
            print("\n------ROUND RESULTS------")
            if eliminated_in_voting:
                role = self.players[eliminated_in_voting]['role']
                if role == 'Thief':
                    print("1. Ek chor pakra gaya aur mara gaya")
                else:
                    print("1. Voting se ek player eliminate hua")
            
            if self.thieves_target and not self.players[self.thieves_target]['alive']:
                print("2. Thieves ka target eliminate hua")
            elif self.thieves_target:
                print("2. Angel ne target ko bacha lia")
            
            if self._check_win_conditions(): break
            
            print("\nCurrent Status:")
            print("Alive:", ", ".join(
                [name for name, data in self.players.items() if data['alive']]))
            print("Eliminated:", ", ".join(self.eliminated) if self.eliminated else "None")
            
            self.round += 1
            input("\nPress Enter to continue...")
            os.system('cls' if os.name == 'nt' else 'clear')
        
        self._show_final_results()

    def _show_final_results(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=== FINAL RESULTS ===")
        for name, data in self.players.items():
            status = "ALIVE" if data['alive'] else "ELIMINATED"
            print(f"{name}: {data['role']} ({status})")

if __name__ == "__main__":
    game = DakatiGame()
    game.play()