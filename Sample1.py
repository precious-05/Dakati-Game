"""
DAKATI GAME - Final Perfect Implementation
Follows ALL rules exactly as specified
"""

import random
import os
from getpass import getpass
from collections import defaultdict

class DakatiGame:
    def __init__(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=== DAKATI GAME ===")
        print("A Social Deduction Game for 8 Players\n")
        
        # Game state
        self.player_names = self._register_players()
        self.players = {}
        self.eliminated = []
        self.current_votes = defaultdict(int)
        self.thieves_target = None
        self.angel_choice = None
        self.round = 1
        
        # Setup
        self._assign_roles()
        self._reveal_thieves()
        self._introduce_roles()

    def _register_players(self):
        """Register 8 players with hidden input"""
        print("=== PLAYER REGISTRATION ===\n")
        players = []
        for i in range(1, 9):
            while True:
                name = getpass(f"Player {i}, enter your name (hidden): ").strip()
                if name and name not in players:
                    players.append(name)
                    break
                print("Invalid name! Must be unique and non-empty.")
        os.system('cls' if os.name == 'nt' else 'clear')
        return players

    def _assign_roles(self):
        """Assign 2 Thieves, 1 Angel, 5 Citizens"""
        roles = ['Thief']*2 + ['Angel']*1 + ['Citizen']*5
        random.shuffle(roles)
        self.players = {
            name: {'role': role, 'alive': True}
            for name, role in zip(self.player_names, roles)
        }

    def _reveal_thieves(self):
        """Thieves know each other (but not Angel)"""
        thieves = [name for name, data in self.players.items() 
                 if data['role'] == 'Thief']
        for thief in thieves:
            self.players[thief]['known_thieves'] = [
                t for t in thieves if t != thief
            ]

    def _introduce_roles(self):
        """Private role reveal"""
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
        """Voting phase - thieves never vote against each other"""
        print(f"\n=== ROUND {self.round}: VOTING PHASE ===")
        self.current_votes = defaultdict(int)
        alive_players = [name for name, data in self.players.items() 
                        if data['alive']]

        for voter in alive_players:
            options = [p for p in alive_players if p != voter]
            
            # Thieves remove their partner from voting options
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
        """Thieves select target (can be anyone)"""
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
        """Angel attempts save (can save anyone including thieves)"""
        angel = next((name for name, data in self.players.items() 
                     if data['alive'] and data['role'] == 'Angel'), None)
        if not angel or not self.thieves_target:
            return

        # Check if target is still alive
        if not self.players[self.thieves_target]['alive']:
            return

        print("\n=== ANGEL'S PHASE ===")
        print("Angel open your eyes!")
        input("Press Enter when ready...")
        
        # Angel can save ANYONE (including thieves)
        options = [name for name, data in self.players.items() if data['alive']]
        
        self.angel_choice = self._get_hidden_choice(
            f"Angel {angel}, choose someone to save (can be anyone):",
            angel,
            options
        )

        if self.angel_choice == self.thieves_target:
            print("\nJo chor citizen ko marna chahte the wo bach gaya Angel ki wajah se!")
            print("(The citizen thieves wanted to kill was saved by Angel!)")
        else:
            print("\nAngel citizen ko nahi bacha saka, citizen mar gaya!")
            print("(Angel couldn't save the citizen, citizen died!)")
            self._eliminate(self.thieves_target, "thieves")
        
        print("Angel close your eyes!")
        input("Press Enter to continue...")

    def _get_hidden_choice(self, prompt, player, options):
        """Get hidden input from player"""
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
        """Mark player as eliminated"""
        self.players[player]['alive'] = False
        self.eliminated.append(player)

    def _check_win_conditions(self):
        """Check win conditions"""
        alive_thieves = sum(1 for data in self.players.values() 
                          if data['alive'] and data['role'] == 'Thief')
        alive_citizens = sum(1 for data in self.players.values() 
                            if data['alive'] and data['role'] in ['Citizen', 'Angel'])

        if alive_thieves == 0:
            print("\n=== CITIZENS WIN! All thieves eliminated ===")
            return True
        elif alive_thieves >= alive_citizens:
            print("\n=== THIEVES WIN! They outnumber citizens ===")
            return True
        return False

    def play(self):
        """Run the full game with correct phase order"""
        while True:
            print(f"\n=== ROUND {self.round} ===")
            
            # Correct phase order:
            eliminated_in_voting = self._voting_phase()  # Phase 1: Voting
            self._thieves_phase()                       # Phase 2: Thieves select target
            self._angel_phase()                         # Phase 3: Angel attempts save
            
            # Final announcements
            print("\n=== ROUND RESULTS ===")
            if eliminated_in_voting:
                role = self.players[eliminated_in_voting]['role']
                if role == 'Thief':
                    print("1. Ek chor pakra gaya aur mara gaya!")
                else:
                    print("1. Voting se ek player eliminate hua!")
            
            if self.thieves_target and not self.players[self.thieves_target]['alive']:
                print("2. Thieves ka target eliminate hua!")
            elif self.thieves_target:
                print("2. Angel ne target ko bacha lia!")
            
            if self._check_win_conditions(): break
            
            # Round end
            print("\nCurrent Status:")
            print("Alive:", ", ".join(
                [name for name, data in self.players.items() if data['alive']]))
            print("Eliminated:", ", ".join(self.eliminated) if self.eliminated else "None")
            
            self.round += 1
            input("\nPress Enter to continue...")
            os.system('cls' if os.name == 'nt' else 'clear')
        
        self._show_final_results()

    def _show_final_results(self):
        """Reveal all roles at game end"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=== FINAL RESULTS ===")
        for name, data in self.players.items():
            status = "ALIVE" if data['alive'] else "ELIMINATED"
            print(f"{name}: {data['role']} ({status})")

# Run the game
if __name__ == "__main__":
    game = DakatiGame()
    game.play()