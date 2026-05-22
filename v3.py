from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.clock import Clock
import random
from collections import defaultdict

class RoleRevealButton(Button):
    pass

class PlayerButton(Button):
    pass

class DakatiGame(BoxLayout):
    current_phase = StringProperty("")
    round_number = NumericProperty(1)
    alive_players = ListProperty([])
    eliminated_players = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self.padding = dp(20)
        
        # Game state variables
        self.players = {}
        self.player_names = []
        self.current_votes = defaultdict(int)
        self.thieves_target = None
        self.angel_choice = None
        self.current_player_viewing = None
        self.eliminated_in_voting = None
        
        # UI Setup
        self.setup_background()
        self.show_welcome_screen()

    def setup_background(self):
        with self.canvas.before:
            Color(0.08, 0.08, 0.15, 1)  # Dark blue background
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        Window.bind(size=self.update_background)

    def update_background(self, instance, value):
        self.rect.size = value

    def show_welcome_screen(self):
        self.clear_widgets()
        
        title = Label(
            text="[b]DAKATI GAME[/b]",
            markup=True,
            font_size=dp(36),
            color=(0.9, 0.9, 0.1, 1),
            size_hint=(1, 0.3)
        )
        
        subtitle = Label(
            text="A Social Deduction Game for 8 Players",
            font_size=dp(20),
            color=(0.8, 0.8, 0.8, 1)
        )
        
        start_btn = Button(
            text="START GAME",
            size_hint=(None, None),
            size=(dp(250), dp(60)),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.2, 0.6, 0.2, 1),
            font_size=dp(22),
            bold=True
        )
        start_btn.bind(on_press=self.start_registration)
        
        main_layout = BoxLayout(orientation='vertical', spacing=dp(20))
        main_layout.add_widget(title)
        main_layout.add_widget(subtitle)
        main_layout.add_widget(start_btn)
        
        self.add_widget(main_layout)

    def start_registration(self, instance):
        self.clear_widgets()
        self.current_phase = "REGISTRATION"
        
        header = Label(
            text="Player Registration",
            font_size=dp(28),
            color=(0.9, 0.9, 0.1, 1),
            size_hint=(1, None),
            height=dp(50)
        )
        
        input_grid = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None
        )
        input_grid.bind(minimum_height=input_grid.setter('height'))
        
        self.player_inputs = []
        for i in range(8):
            input_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
            input_box.add_widget(Label(
                text=f"Player {i+1}:",
                size_hint=(0.3, 1),
                color=(0.8, 0.8, 0.8, 1)
            ))
            
            player_input = TextInput(
                multiline=False,
                size_hint=(0.7, 1),
                background_normal='',
                background_color=(0.15, 0.15, 0.25, 1),
                foreground_color=(1, 1, 1, 1),
                cursor_color=(1, 1, 1, 1)
            )
            self.player_inputs.append(player_input)
            input_box.add_widget(player_input)
            input_grid.add_widget(input_box)
        
        scroll = ScrollView(size_hint=(1, 0.8))
        scroll.add_widget(input_grid)
        
        submit_btn = Button(
            text="CONFIRM PLAYERS",
            size_hint=(None, None),
            size=(dp(250), dp(60)),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.2, 0.4, 0.8, 1),
            font_size=dp(20)
        )
        submit_btn.bind(on_press=self.validate_registration)
        
        self.add_widget(header)
        self.add_widget(scroll)
        self.add_widget(submit_btn)

    def validate_registration(self, instance):
        self.player_names = [input.text.strip() for input in self.player_inputs]
        
        if any(not name for name in self.player_names):
            self.show_error_popup("All player names must be non-empty!")
            return
        
        if len(set(self.player_names)) != 8:
            self.show_error_popup("All player names must be unique!")
            return
        
        self.assign_roles()

    def assign_roles(self):
        roles = ['Thief']*2 + ['Angel']*1 + ['Citizen']*5
        random.shuffle(roles)
        self.players = {
            name: {'role': role, 'alive': True}
            for name, role in zip(self.player_names, roles)
        }
        
        # Reveal only partner names to thieves (not roles)
        thieves = [name for name, data in self.players.items() if data['role'] == 'Thief']
        for thief in thieves:
            self.players[thief]['known_thieves'] = [
                t for t in thieves if t != thief
            ]
        
        self.show_role_reveal_screen()

    def show_role_reveal_screen(self):
        self.current_phase = "ROLE_REVEAL"
        self.current_player_index = 0
        self.update_role_reveal()

    def update_role_reveal(self):
        self.clear_widgets()
        
        if self.current_player_index >= len(self.player_names):
            self.start_game_loop()
            return
            
        player = self.player_names[self.current_player_index]
        role_data = self.players[player]
        
        header = Label(
            text=f"{player}'s Role",
            font_size=dp(28),
            color=(0.9, 0.9, 0.1, 1),
            size_hint=(1, 0.2)
        )
        
        role_box = BoxLayout(
            orientation='vertical',
            size_hint=(0.8, 0.5),
            pos_hint={'center_x': 0.5},
            spacing=dp(20)
        )
        
        role_type = Label(
            text=f"[b]{role_data['role'].upper()}[/b]",
            markup=True,
            font_size=dp(36),
            color=(0.2, 0.8, 0.4, 1) if role_data['role'] == 'Citizen' else 
                 (0.8, 0.2, 0.2, 1) if role_data['role'] == 'Thief' else 
                 (0.4, 0.4, 0.9, 1)
        )
        
        role_box.add_widget(role_type)
        
        if role_data['role'] == 'Thief':
            partner_label = Label(
                text=f"Other thieves: {', '.join(role_data['known_thieves'])}",
                font_size=dp(24),
                color=(0.9, 0.6, 0.1, 1)
            )
            role_box.add_widget(partner_label)
        
        continue_btn = Button(
            text="CONTINUE",
            size_hint=(None, None),
            size=(dp(200), dp(50)),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.3, 0.3, 0.8, 1)
        )
        continue_btn.bind(on_press=self.next_role_reveal)
        
        self.add_widget(header)
        self.add_widget(role_box)
        self.add_widget(continue_btn)

    def next_role_reveal(self, instance):
        self.current_player_index += 1
        self.update_role_reveal()

    def start_game_loop(self):
        self.current_phase = "GAME_LOOP"
        self.round_number = 1
        self.update_alive_players()
        self.show_voting_phase()

    def update_alive_players(self):
        self.alive_players = [name for name, data in self.players.items() if data['alive']]
        self.eliminated_players = [name for name, data in self.players.items() if not data['alive']]

    def show_voting_phase(self):
        self.clear_widgets()
        self.current_phase = "VOTING"
        self.current_votes = defaultdict(int)
        self.current_voter_index = 0
        self.update_voting_screen()

    def update_voting_screen(self):
        if self.current_voter_index >= len(self.alive_players):
            self.process_votes()
            return
        
        voter = self.alive_players[self.current_voter_index]
        role_data = self.players[voter]

        

        
        
        self.clear_widgets()
        
        header = Label(
            text=f"Round {self.round_number}: Voting Phase",
            font_size=dp(24),
            color=(0.9, 0.9, 0.1, 1),
            size_hint=(1, 0.15)
        )
        
        instruction = Label(
            text=f"{voter}, vote to eliminate:",
            font_size=dp(20),
            color=(0.8, 0.8, 0.8, 1),
            size_hint=(1, 0.1)
        )
        
        # Get voting options based on role
        # Get voting options
        options = [p for p in self.alive_players if p != voter]

        # Thieves cannot vote for other thieves
        if role_data['role'] == 'Thief':
            options = [p for p in options if self.players[p]['role'] != 'Thief']

        # If no options left (shouldn't happen in normal game), skip voting
        if not options:
            self.current_voter_index += 1
            self.update_voting_screen()
            return
        
        grid = GridLayout(cols=2, spacing=dp(15), padding=dp(20), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for player in options:
            btn = PlayerButton(
                text=player,
                size_hint_y=None,
                height=dp(60),
                background_normal='',
                background_color=(0.2, 0.3, 0.5, 1)
            )
            btn.player_name = player
            btn.bind(on_press=lambda x, p=player: self.record_vote(voter, p))
            grid.add_widget(btn)
        
        scroll = ScrollView(size_hint=(1, 0.6))
        scroll.add_widget(grid)
        
        status = Label(
            text=f"Alive: {', '.join(self.alive_players)}\nEliminated: {', '.join(self.eliminated_players) if self.eliminated_players else 'None'}",
            font_size=dp(16),
            color=(0.7, 0.7, 0.7, 1),
            size_hint=(1, 0.15),
            halign='left',
            valign='top'
        )
        
        self.add_widget(header)
        self.add_widget(instruction)
        self.add_widget(scroll)
        self.add_widget(status)

    def record_vote(self, voter, target):
        self.current_votes[target] += 1
        self.current_voter_index += 1
        self.update_voting_screen()

    def process_votes(self):
    # Check if all votes are zero or no votes exist
        if not self.current_votes or all(votes == 0 for votes in self.current_votes.values()):
            self.show_popup(
                "No Elimination",
                "No one received enough votes to be eliminated!",
                self.show_thieves_phase
            )
            return

        max_votes = max(self.current_votes.values())
        candidates = [p for p, v in self.current_votes.items() if v == max_votes]

        # Randomly eliminate if tie (multiple players with max votes)
        eliminated = random.choice(candidates) if len(candidates) > 1 else candidates[0]

        self.players[eliminated]['alive'] = False
        self.eliminated_players.append(eliminated)
        self.eliminated_in_voting = eliminated

        role = self.players[eliminated]['role']
        if role == 'Citizen':
            message = "Masoom citizen mar gaya! (Innocent citizen died!)"
        elif role == 'Thief':
            message = "Ek chor mar gaya! (A thief died!)"
        else:
            message = "Angel bhi mar gaya! (Angel died!)"

        self.show_popup(
            "Voting Result",
            f"{eliminated} was eliminated!\n{message}",
            self.show_thieves_phase
        )

    def show_thieves_phase(self):
        self.current_phase = "THIEVES"
        thieves = [name for name, data in self.players.items() 
                  if data['alive'] and data['role'] == 'Thief']
        
        if not thieves:
            self.show_angel_phase()
            return
            
        self.thieves_target = None
        self.clear_widgets()
        
        header = Label(
            text="Thieves' Phase",
            font_size=dp(28),
            color=(0.9, 0.2, 0.2, 1),
            size_hint=(1, 0.2)
        )
        
        instruction = Label(
            text=f"Thieves {' & '.join(thieves)}, choose a target to kill:",
            font_size=dp(20),
            color=(0.8, 0.8, 0.8, 1),
            size_hint=(1, 0.1)
        )
        
        targets = [name for name, data in self.players.items() if data['alive']]
        grid = GridLayout(cols=2, spacing=dp(15), padding=dp(20), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for player in targets:
            btn = PlayerButton(
                text=player,
                size_hint_y=None,
                height=dp(60),
                background_normal='',
                background_color=(0.5, 0.2, 0.2, 1)
            )
            btn.player_name = player
            btn.bind(on_press=lambda x, p=player: self.set_thieves_target(p))
            grid.add_widget(btn)
        
        scroll = ScrollView(size_hint=(1, 0.6))
        scroll.add_widget(grid)
        
        self.add_widget(header)
        self.add_widget(instruction)
        self.add_widget(scroll)

    def set_thieves_target(self, target):
        self.thieves_target = target
        self.show_angel_phase()

    def show_angel_phase(self):
        self.current_phase = "ANGEL"
        angel = next((name for name, data in self.players.items() 
                     if data['alive'] and data['role'] == 'Angel'), None)
        
        if not angel or not self.thieves_target:
            self.show_round_results()
            return
            
        self.angel_choice = None
        self.clear_widgets()
        
        header = Label(
            text="Angel's Phase",
            font_size=dp(28),
            color=(0.4, 0.4, 0.9, 1),
            size_hint=(1, 0.2)
        )
        
        instruction = Label(
            text=f"Angel {angel}, choose someone to save (can be anyone, including yourself):",
            font_size=dp(20),
            color=(0.8, 0.8, 0.8, 1),
            size_hint=(1, 0.1)
        )
        
        targets = [name for name, data in self.players.items() if data['alive']]
        grid = GridLayout(cols=2, spacing=dp(15), padding=dp(20), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for player in targets:
            btn = PlayerButton(
                text=player,
                size_hint_y=None,
                height=dp(60),
                background_normal='',
                background_color=(0.3, 0.3, 0.7, 1)
            )
            btn.player_name = player
            btn.bind(on_press=lambda x, p=player: self.set_angel_choice(p))
            grid.add_widget(btn)
        
        scroll = ScrollView(size_hint=(1, 0.6))
        scroll.add_widget(grid)
        
        self.add_widget(header)
        self.add_widget(instruction)
        self.add_widget(scroll)

    def set_angel_choice(self, target):
        self.angel_choice = target
        
        if self.angel_choice == self.thieves_target:
            message = "Jo chor citizen ko marna chahte the wo bach gaya Angel ki wajah se!\n(The citizen thieves wanted to kill was saved by Angel!)"
        else:
            # Only eliminate the target if it's a citizen or angel (not a thief)
            if self.players[self.thieves_target]['role'] in ['Citizen', 'Angel']:
                self.players[self.thieves_target]['alive'] = False
                self.eliminated_players.append(self.thieves_target)
                
                if self.thieves_target == target and target == next((name for name, data in self.players.items() 
                         if data['alive'] and data['role'] == 'Angel'), None):
                    message = "Angel khud ko nahi bacha paya! Angel mar gaya!\n(Angel failed to save themselves! Angel died!)"
                else:
                    message = "Angel ne galat guess kia! Masoom citizen mar gaya!\n(Angel guessed wrong! Innocent citizen died!)"
            else:
                message = "The thieves' target was a fellow thief!\nNo one was eliminated."
        
        self.show_popup(
            "Angel's Decision",
            message,
            self.show_round_results
        )

    def show_round_results(self):
        self.clear_widgets()
        self.current_phase = "RESULTS"
        
        header = Label(
            text=f"Round {self.round_number} Results",
            font_size=dp(28),
            color=(0.9, 0.9, 0.1, 1),
            size_hint=(1, 0.15)
        )
        
        results_box = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint=(1, 0.6)
        )
        
        alive_label = Label(
            text=f"Alive Players: {', '.join(self.alive_players)}",
            font_size=dp(20),
            color=(0.2, 0.8, 0.2, 1)
        )
        
        eliminated_label = Label(
            text=f"Eliminated Players: {', '.join(self.eliminated_players) if self.eliminated_players else 'None'}",
            font_size=dp(20),
            color=(0.8, 0.2, 0.2, 1)
        )
        
        results_box.add_widget(alive_label)
        results_box.add_widget(eliminated_label)
        
        continue_btn = Button(
            text="CONTINUE TO NEXT ROUND",
            size_hint=(None, None),
            size=(dp(300), dp(60)),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.2, 0.6, 0.2, 1),
            font_size=dp(20)
        )
        continue_btn.bind(on_press=self.check_win_conditions)
        
        self.add_widget(header)
        self.add_widget(results_box)
        self.add_widget(continue_btn)

    def check_win_conditions(self, instance):
        alive_thieves = sum(1 for data in self.players.values() 
                          if data['alive'] and data['role'] == 'Thief')
        alive_citizens = sum(1 for data in self.players.values() 
                           if data['alive'] and data['role'] in ['Citizen', 'Angel'])
        
        if alive_thieves == 0:
            self.show_final_results("CITIZENS WIN!\nAll thieves have been eliminated!")
        elif alive_thieves >= alive_citizens:
            self.show_final_results("THIEVES WIN!\nThey outnumber the citizens!")
        else:
            self.round_number += 1
            self.show_voting_phase()

    def show_final_results(self, message):
        self.clear_widgets()
        self.current_phase = "GAME_OVER"
        
        header = Label(
            text="Game Over",
            font_size=dp(36),
            color=(0.9, 0.2, 0.2, 1),
            size_hint=(1, 0.15)
        )
        
        result_msg = Label(
            text=message,
            font_size=dp(24),
            color=(0.9, 0.9, 0.1, 1),
            size_hint=(1, 0.1)
        )
        
        roles_box = GridLayout(
            cols=2,
            spacing=dp(10),
            padding=dp(20),
            size_hint_y=None
        )
        roles_box.bind(minimum_height=roles_box.setter('height'))
        
        for name, data in self.players.items():
            status = "ALIVE" if data['alive'] else "ELIMINATED"
            color = (0.2, 0.8, 0.2, 1) if data['alive'] else (0.8, 0.2, 0.2, 1)
            
            player_label = Label(
                text=name,
                font_size=dp(18),
                color=(0.8, 0.8, 0.8, 1),
                size_hint_x=0.6
            )
            
            role_label = Label(
                text=f"{data['role'].upper()} ({status})",
                font_size=dp(18),
                color=color,
                size_hint_x=0.4
            )
            
            roles_box.add_widget(player_label)
            roles_box.add_widget(role_label)
        
        scroll = ScrollView(size_hint=(1, 0.6))
        scroll.add_widget(roles_box)
        
        restart_btn = Button(
            text="PLAY AGAIN",
            size_hint=(None, None),
            size=(dp(200), dp(60)),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.2, 0.4, 0.8, 1)
        )
        restart_btn.bind(on_press=self.restart_game)
        
        self.add_widget(header)
        self.add_widget(result_msg)
        self.add_widget(scroll)
        self.add_widget(restart_btn)

    def restart_game(self, instance):
        self.__init__()

    def show_popup(self, title, message, callback):
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        content.add_widget(Label(
            text=message,
            font_size=dp(18),
            color=(0, 0, 0, 1)
        ))
        
        btn = Button(
            text="OK",
            size_hint=(1, None),
            height=dp(50),
            background_normal='',
            background_color=(0.2, 0.6, 0.2, 1)
        )
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.5),
            separator_color=(0.2, 0.6, 0.2, 1)
        )
        
        btn.bind(on_press=popup.dismiss)
        btn.bind(on_press=lambda x: callback())
        content.add_widget(btn)
        popup.open()

    def show_error_popup(self, message):
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        content.add_widget(Label(
            text=message,
            font_size=dp(18),
            color=(0, 0, 0, 1)
        ))
        
        btn = Button(
            text="OK",
            size_hint=(1, None),
            height=dp(50),
            background_normal='',
            background_color=(0.8, 0.2, 0.2, 1)
        )
        
        popup = Popup(
            title="Error",
            content=content,
            size_hint=(0.8, 0.4),
            separator_color=(0.8, 0.2, 0.2, 1)
        )
        
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

class DakatiApp(App):
    def build(self):
        self.title = 'Dakati Game - Social Deduction'
        Window.size = (900, 700)
        return DakatiGame()

if __name__ == '__main__':
    DakatiApp().run()