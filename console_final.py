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
        #resgitered exactly 8 players with hidden input and ensure names are unique
        players = []
        print("Player Registration:\n")
        for i in range(1, 9):
            while True:
                # getpass hides the input so other players can't see who's entering the name
                name = getpass(f"Player {i}, enter your name (hidden): ").strip()  # .strip() removes extra spaces
                if name and name not in players:  # Ensures non-empty and unique names
                    players.append(name)
                    break
                print("Name must be unique and non-empty. Please try again.")
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen after registration
        return players

    def _assign_roles(self):
        # Assign roles randomly using shuffle
        roles = ['Thief'] * 2 + ['Angel'] * 1 + ['Citizen'] * 5  # Predefined role list
        random.shuffle(roles)  # Shuffles role list so assignment is random and fair

        # Assign each role to a player and mark them as alive initially
        self.players = {
            name: {'role': role, 'alive': True}
            for name, role in zip(self.player_names, roles)  # zip pairs each player with a role
        }

    def _reveal_thieves(self):
        # Inform each thief of their fellow thief's identity (secretly)
        thieves = [name for name, data in self.players.items() if data['role'] == 'Thief']
        for thief in thieves:
            # Assign the other thief's name (excluding current one) to 'known_thieves' key
            self.players[thief]['known_thieves'] = [t for t in thieves if t != thief]

    def _introduce_roles(self):
        # Display role info privately to each player
        for name, data in self.players.items():
            os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen before showing role
            role = data['role']
            print(f"{name}, your role is: {role}")
            if role == 'Thief':
                partner = self.players[name]['known_thieves'][0]
                print(f"Your partner is: {partner}")
            input("\nPress Enter to proceed to the next player...")  # Wait for player before moving on
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear after all players see their roles

    def _get_alive_players(self):
        # Return a list of all players who are still alive
        return [name for name, data in self.players.items() if data['alive']]

    def _voting_phase(self):
        # Allow alive players to vote out a suspicious player
        print(f"\nRound {self.round}: Voting Phase\n")
        alive = self._get_alive_players()
        self.current_votes.clear()  # Clear old votes

        for voter in alive:
            while True:
                print(f"\n{voter}, it's your turn to vote.")
                vote = input("Enter the name of the player you suspect: ").strip()
                if vote in alive and vote != voter:  # Can't vote for yourself
                    self.current_votes[vote] += 1
                    break
                print("Invalid vote. Make sure you choose a living player other than yourself.")

        # Determine player with maximum votes
        max_votes = max(self.current_votes.values())  # Finds highest number of votes
        top_candidates = [p for p, v in self.current_votes.items() if v == max_votes]

        # Handle tie (no one out) or eliminate top-voted player
        if len(top_candidates) == 1:
            eliminated = top_candidates[0]
            self.players[eliminated]['alive'] = False  # Mark eliminated
            self.eliminated.append(eliminated)
            print(f"\n{eliminated} has been voted out.")
        else:
            print("\nVoting resulted in a tie. No one is eliminated this round.")

    def _thieves_phase(self):
        #A secret phase where thieves choose someone to eliminate
        print("\nThieves Phase:")
        thieves = [p for p, data in self.players.items() if data['role'] == 'Thief' and data['alive']]
        if len(thieves) < 2:
            print("One or both thieves are dead.... No action this round....")
            self.thieves_target = None
            return

        for thief in thieves:
            while True:
                print(f"\n{thief}, choose a player to eliminate.")
                # getpass hides the input so thieves can act secretly
                target = getpass("Enter the name (hidden): ").strip()
                if target in self._get_alive_players() and target not in thieves:
                    self.thieves_target = target
                    return
                print("Invalid choice---- You cannot eliminate another thief or a dead player----")

    def _angel_phase(self):
        #herengel selects one player to protect from elimination
        print("\nAngel's Phase:")
        angel = next((p for p, data in self.players.items()
                      if data['role'] == 'Angel' and data['alive']), None)
        if not angel:
            print("Angel is not alive  😢  No one is protected")
            self.angel_choice = None
            return

        while True:
            print(f"\n{angel}, choose a player to protect.")
            protect = getpass("Enter the name (hidden): ").strip()
            if protect in self._get_alive_players():
                self.angel_choice = protect
                return
            print("Invalid choice. Select someone who is still alive.")

    def _apply_thieves_result(self):
        #eliminate the player chosen by thieves unless protected by angel
        if self.thieves_target:
            if self.thieves_target == self.angel_choice:
                print(f"\n{self.thieves_target} was targeted but protected by the Angel.")
            else:
                self.players[self.thieves_target]['alive'] = False
                self.eliminated.append(self.thieves_target)
                print(f"\n{self.thieves_target} was eliminated by the Thieves.")

    def _check_game_over(self):
        #determine whether the game is over "one side has wonn"
        alive = self._get_alive_players()
        thieves = [p for p in alive if self.players[p]['role'] == 'Thief']
        citizens = [p for p in alive if self.players[p]['role'] != 'Thief']

        if not thieves:
            print("\nGame Over! Citizens and Angel win!")
            return True
        elif len(thieves) >= len(citizens):
            print("\nGame Over! Thieves win!")
            return True
        return False  #the game continues

    def play(self):
        #Main loop to keep playing rounds until game ends
        print("----------The game has officially started---------\n")
        while True:
            self._voting_phase()
            if self._check_game_over():
                break

            self._thieves_phase()
            self._angel_phase()
            self._apply_thieves_result()

            if self._check_game_over():
                break

            self.round += 1  #proceed to next round

        print("\n----------Thank you for playing Dakati Game----------")
        print("Eliminated players are:", ', '.join(self.eliminated))

# Start the game only if this script is run directly
if __name__ == "__main__":
    DakatiGame().play()
