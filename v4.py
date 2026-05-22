from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty, StringProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior 
import random
from collections import defaultdict
import os

# Load custom KV language strings
Builder.load_string('''
<PlayerCard>:
    orientation: 'vertical'
    size_hint: (None, None)
    size: (dp(120), dp(160))
    canvas.before:
        Color:
            rgba: (0.1, 0.1, 0.2, 1) if not root.selected else (0.3, 0.2, 0.4, 1)
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [15,]
        Color:
            rgba: (0.8, 0.2, 0.2, 1) if not root.alive else (0.2, 0.8, 0.2, 1)
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, 15]
            width: 2
    Label:
        text: root.player_name
        font_size: '16sp'
        bold: True
        color: (1, 1, 1, 1)
        size_hint_y: None
        height: dp(30)
    Image:
        source: root.role_icon
        size_hint: (1, 0.7)
        allow_stretch: True
    Label:
        text: root.role if root.show_role else '?'
        font_size: '14sp'
        color: (1, 1, 1, 1)
        size_hint_y: None
        height: dp(20)

<RoleRevealScreen>:
    orientation: 'vertical'
    padding: dp(20)
    spacing: dp(20)
    Image:
        source: 'assets/role_background.png'
        allow_stretch: True
        keep_ratio: False
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: dp(200)
        spacing: dp(10)
        Label:
            text: 'You are the...'
            font_size: '24sp'
            color: (1, 1, 1, 1)
        Label:
            text: root.role.upper()
            font_size: '36sp'
            bold: True
            color: (0.9, 0.8, 0.1, 1)
        Label:
            text: root.role_description
            font_size: '16sp'
            color: (1, 1, 1, 1)
            text_size: self.width, None
    Button:
        text: 'Continue'
        size_hint: (None, None)
        size: (dp(200), dp(50))
        pos_hint: {'center_x': 0.5}
        background_normal: ''
        background_color: (0.2, 0.6, 0.2, 1)
        on_press: root.dismiss()
''')

# Custom Widgets
class PlayerCard(ButtonBehavior, BoxLayout):  # Changed to include ButtonBehavior
    player_name = StringProperty('')
    role = StringProperty('')
    role_icon = StringProperty('')
    alive = BooleanProperty(True)
    show_role = BooleanProperty(False)
    selected = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)  # Fully transparent

class RoleRevealScreen(ModalView):
    role = StringProperty('')
    role_description = StringProperty('')

class DakatiGame(BoxLayout):
    current_phase = StringProperty("")
    round_number = NumericProperty(1)
    alive_players = ListProperty([])
    eliminated_players = ListProperty([])
    background_image = ObjectProperty(None)

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
            self.background = Rectangle(source='assets/game_bg.jpg', 
                                     size=Window.size, 
                                     pos=self.pos)
        Window.bind(size=self.update_background)

    def update_background(self, instance, value):
        self.background.size = value

    def show_welcome_screen(self):
        self.clear_widgets()
        
        # Main container with background
        main_layout = BoxLayout(orientation='vertical', spacing=dp(20))
        
        # Logo and title
        logo = Image(source='assets/logo.png', 
                    size_hint=(1, 0.4),
                    allow_stretch=True,
                    keep_ratio=True)
        
        # Start button with animation
        start_btn = Button(
            text="START GAME",
            size_hint=(None, None),
            size=(dp(250), dp(60)),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.8, 0.2, 0.2, 1),
            font_size=dp(22),
            bold=True
        )
        anim = Animation(background_color=(0.9, 0.3, 0.3, 1), duration=0.5) + \
               Animation(background_color=(0.8, 0.2, 0.2, 1), duration=0.5)
        anim.repeat = True
        anim.start(start_btn)
        
        start_btn.bind(on_press=self.start_registration)
        
        main_layout.add_widget(logo)
        main_layout.add_widget(start_btn)
        
        self.add_widget(main_layout)

    def start_registration(self, instance):
        self.clear_widgets()
        self.current_phase = "REGISTRATION"
        
        # Animated header
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.2))
        title = Label(
            text="PLAYER REGISTRATION",
            font_size=dp(28),
            color=(0.9, 0.9, 0.1, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1)
        )
        anim = Animation(font_size=dp(32), duration=0.7) + \
               Animation(font_size=dp(28), duration=0.7)
        anim.repeat = True
        anim.start(title)
        header.add_widget(title)
        
        # Input Grid with scroll
        input_grid = GridLayout(
            cols=1,
            spacing=dp(15),
            size_hint_y=None,
            padding=dp(20)
        )
        input_grid.bind(minimum_height=input_grid.setter('height'))
        
        self.player_inputs = []
        for i in range(8):
            input_box = BoxLayout(orientation='horizontal', 
                                 size_hint_y=None, 
                                 height=dp(60),
                                 spacing=dp(10))
            
            # Player number with icon
            num_box = BoxLayout(orientation='horizontal',
                              size_hint=(0.2, 1))
            num_box.add_widget(Image(source=f'assets/player_{i+1}.png',
                                  size_hint=(0.4, 1),
                                  allow_stretch=True))
            num_box.add_widget(Label(
                text=f"P{i+1}:",
                font_size=dp(18),
                color=(0.9, 0.9, 0.9, 1),
                size_hint=(0.6, 1))
            )
            
            player_input = TextInput(
                multiline=False,
                size_hint=(0.8, 1),
                background_normal='',
                background_color=(0.15, 0.15, 0.25, 0.8),
                foreground_color=(1, 1, 1, 1),
                cursor_color=(1, 1, 1, 1),
                font_size=dp(18),
                hint_text=f"Player {i+1} Name",
                padding=dp(10)
            )
            self.player_inputs.append(player_input)
            input_box.add_widget(num_box)
            input_box.add_widget(player_input)
            input_grid.add_widget(input_box)
        
        scroll = ScrollView(size_hint=(1, 0.7))
        scroll.add_widget(input_grid)
        
        # Submit button
        submit_btn = Button(
            text="CONFIRM PLAYERS",
            size_hint=(None, None),
            size=(dp(300), dp(60)),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.2, 0.4, 0.8, 1),
            font_size=dp(20),
            bold=True
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
        
        # Set role icons
        role_icons = {
            'Thief': 'assets/thief_icon.png',
            'Angel': 'assets/angel_icon.png',
            'Citizen': 'assets/citizen_icon.png'
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
        if self.current_player_index >= len(self.player_names):
            self.start_game_loop()
            return
            
        player = self.player_names[self.current_player_index]
        role_data = self.players[player]
        
        # Create role reveal screen
        role_screen = RoleRevealScreen()
        role_screen.role = role_data['role']
        
        # Set role descriptions
        role_descriptions = {
            'Thief': 'Work with your partner to eliminate citizens at night',
            'Angel': 'Protect players from the thieves each night',
            'Citizen': 'Find and eliminate the thieves through voting'
        }
        role_screen.role_description = role_descriptions[role_data['role']]
        
        # Add partner info for thieves
        if role_data['role'] == 'Thief':
            role_screen.role_description += f"\n\nYour partner: {', '.join(role_data['known_thieves'])}"
        
        role_screen.bind(on_dismiss=lambda x: self.next_role_reveal())
        role_screen.open()

    def next_role_reveal(self):
        self.current_player_index += 1
        Clock.schedule_once(lambda dt: self.update_role_reveal(), 0.5)

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

        # Header with animation
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.15))
        phase_label = Label(
            text=f"Round {self.round_number}: Voting Phase",
            font_size=dp(24),
            color=(0.9, 0.9, 0.1, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1)
        )
        anim = Animation(color=(1, 1, 0.5, 1), duration=0.5) + \
               Animation(color=(0.9, 0.9, 0.1, 1), duration=0.5)
        anim.repeat = True
        anim.start(phase_label)

        instruction = Label(
            text=f"{voter}, vote to eliminate:",
            font_size=dp(20),
            color=(0.8, 0.8, 0.8, 1)
        )
        header.add_widget(phase_label)
        header.add_widget(instruction)

        # Get voting options based on role
        options = [p for p in self.alive_players if p != voter]
        if role_data['role'] == 'Thief':
            options = [p for p in options if p not in role_data['known_thieves']]

        # Create player cards grid
        grid = GridLayout(cols=4, spacing=dp(15), padding=dp(20), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        for player in options:
            card = PlayerCard()
            card.player_name = player
            card.role = self.players[player]['role']
            card.role_icon = 'assets/question_mark.png'
            card.alive = self.players[player]['alive']
            card.show_role = False

            # Bind using on_release
            card.bind(on_release=lambda x, p=player: self.record_vote(voter, p))
            grid.add_widget(card)
            
        scroll = ScrollView(size_hint=(1, 0.7))
        scroll.add_widget(grid)

        # Current status
        status_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.15))

        alive_box = BoxLayout(orientation='vertical', size_hint=(0.5, 1))
        alive_box.add_widget(Label(
            text="Alive Players:",
            font_size=dp(16),
            color=(0.2, 0.8, 0.2, 1)
        ))
        alive_box.add_widget(Label(
            text=", ".join(self.alive_players),
            font_size=dp(14),
            color=(0.8, 0.8, 0.8, 1)
        ))

        eliminated_box = BoxLayout(orientation='vertical', size_hint=(0.5, 1))
        eliminated_box.add_widget(Label(
            text="Eliminated Players:",
            font_size=dp(16),
            color=(0.8, 0.2, 0.2, 1)
        ))
        eliminated_box.add_widget(Label(
            text=", ".join(self.eliminated_players) if self.eliminated_players else 'None',
            font_size=dp(14),
            color=(0.8, 0.8, 0.8, 1)
        ))

        status_box.add_widget(alive_box)
        status_box.add_widget(eliminated_box)

        self.add_widget(header)
        self.add_widget(scroll)
        self.add_widget(status_box)


 

    def record_vote(self, voter, target):
        self.current_votes[target] += 1
        self.current_voter_index += 1
        self.update_voting_screen()

    def process_votes(self):
        if not self.current_votes:
            self.show_thieves_phase()
            return
            
        max_votes = max(self.current_votes.values())
        candidates = [p for p, v in self.current_votes.items() if v == max_votes]
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
            self.show_thieves_phase,
            'assets/eliminated.png'
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

        # Header with animation
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.15))
        phase_label = Label(
            text="Thieves' Phase",
            font_size=dp(28),
            color=(0.9, 0.2, 0.2, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1)
        )
        anim = Animation(color=(1, 0.3, 0.3, 1), duration=0.5) + \
               Animation(color=(0.9, 0.2, 0.2, 1), duration=0.5)
        anim.repeat = True
        anim.start(phase_label)

        instruction = Label(
            text=f"Thieves {' & '.join(thieves)}, choose a target to kill:",
            font_size=dp(20),
            color=(0.8, 0.8, 0.8, 1)
        )
        header.add_widget(phase_label)
        header.add_widget(instruction)

        # Get valid targets - can't be thieves themselves
        targets = []
        for name, data in self.players.items():
            if data['alive'] and data['role'] != 'Thief':
                targets.append(name)

        # Create player cards grid
        grid = GridLayout(cols=4, spacing=dp(15), padding=dp(20), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        for player in targets:
            card = PlayerCard()
            card.player_name = player
            card.role = self.players[player]['role']
            card.role_icon = 'assets/question_mark.png'
            card.alive = self.players[player]['alive']
            card.show_role = False

            # Bind using on_release
            card.bind(on_release=lambda x, p=player: self.set_thieves_target(p))
            grid.add_widget(card)

        scroll = ScrollView(size_hint=(1, 0.7))
        scroll.add_widget(grid)

        # Current status
        status_box = self.create_status_box()

        self.add_widget(header)
        self.add_widget(scroll)
        self.add_widget(status_box)

    

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
        
        # Header with animation
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.15))
        phase_label = Label(
            text="Angel's Phase",
            font_size=dp(28),
            color=(0.4, 0.4, 0.9, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1)
        )
        anim = Animation(color=(0.5, 0.5, 1, 1), duration=0.5) + \
               Animation(color=(0.4, 0.4, 0.9, 1), duration=0.5)
        anim.repeat = True
        anim.start(phase_label)
        
        instruction = Label(
            text=f"Angel {angel}, choose someone to save (can be anyone, including yourself):",
            font_size=dp(20),
            color=(0.8, 0.8, 0.8, 1)
        )
        header.add_widget(phase_label)
        header.add_widget(instruction)
        
        # All alive players are options
        targets = [name for name, data in self.players.items() if data['alive']]
        
        # Create player cards grid
        grid = GridLayout(cols=4, spacing=dp(15), padding=dp(20), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for player in targets:
            card = PlayerCard()
            card.player_name = player
            card.role = self.players[player]['role']
            card.role_icon = 'assets/question_mark.png'
            card.alive = self.players[player]['alive']
            card.show_role = False
            
            # Bind using on_release
            card.bind(on_release=lambda x, p=player: self.set_angel_choice(p))
            grid.add_widget(card)
        
        scroll = ScrollView(size_hint=(1, 0.7))
        scroll.add_widget(grid)
        
        # Current status
        status_box = self.create_status_box()
        
        self.add_widget(header)
        self.add_widget(scroll)
        self.add_widget(status_box)

    

    def set_angel_choice(self, target):
        self.angel_choice = target
        
        if self.angel_choice == self.thieves_target:
            message = "Jo chor citizen ko marna chahte the wo bach gaya Angel ki wajah se!\n(The citizen thieves wanted to kill was saved by Angel!)"
            image = 'assets/saved.png'
        else:
            # Only eliminate the target if it's a citizen or angel (not a thief)
            if self.players[self.thieves_target]['role'] in ['Citizen', 'Angel']:
                self.players[self.thieves_target]['alive'] = False
                self.eliminated_players.append(self.thieves_target)
                
                if self.thieves_target == target and target == next((name for name, data in self.players.items() 
                         if data['alive'] and data['role'] == 'Angel'), None):
                    message = "Angel khud ko nahi bacha paya! Angel mar gaya!\n(Angel failed to save themselves! Angel died!)"
                    image = 'assets/angel_died.png'
                else:
                    message = "Angel ne galat guess kia! Masoom citizen mar gaya!\n(Angel guessed wrong! Innocent citizen died!)"
                    image = 'assets/citizen_died.png'
            else:
                message = "The thieves' target was a fellow thief!\nNo one was eliminated."
                image = 'assets/nothing.png'
        
        self.show_popup(
            "Angel's Decision",
            message,
            self.show_round_results,
            image
        )

    def create_status_box(self):
        status_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.15))
        
        alive_box = BoxLayout(orientation='vertical', size_hint=(0.5, 1))
        alive_box.add_widget(Label(
            text="Alive Players:",
            font_size=dp(16),
            color=(0.2, 0.8, 0.2, 1)
        ))
        alive_box.add_widget(Label(
            text=", ".join(self.alive_players),
            font_size=dp(14),
            color=(0.8, 0.8, 0.8, 1)
        ))
        
        eliminated_box = BoxLayout(orientation='vertical', size_hint=(0.5, 1))
        eliminated_box.add_widget(Label(
            text="Eliminated Players:",
            font_size=dp(16),
            color=(0.8, 0.2, 0.2, 1)
        ))
        eliminated_box.add_widget(Label(
            text=", ".join(self.eliminated_players) if self.eliminated_players else 'None',
            font_size=dp(14),
            color=(0.8, 0.8, 0.8, 1)
        ))
        
        status_box.add_widget(alive_box)
        status_box.add_widget(eliminated_box)
        return status_box

    def show_round_results(self):
        self.clear_widgets()
        self.current_phase = "RESULTS"
        
        # Header with animation
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.15))
        phase_label = Label(
            text=f"Round {self.round_number} Results",
            font_size=dp(28),
            color=(0.9, 0.9, 0.1, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1)
        )
        anim = Animation(color=(1, 1, 0.5, 1), duration=0.5) + \
               Animation(color=(0.9, 0.9, 0.1, 1), duration=0.5)
        anim.repeat = True
        anim.start(phase_label)
        header.add_widget(phase_label)
        
        # Results display
        results_box = BoxLayout(orientation='vertical', size_hint=(1, 0.7))
        
        # Add animation for eliminated player if any
        if self.eliminated_in_voting:
            eliminated_card = PlayerCard()
            eliminated_card.player_name = self.eliminated_in_voting
            eliminated_card.role = self.players[self.eliminated_in_voting]['role']
            eliminated_card.role_icon = f'assets/{self.players[self.eliminated_in_voting]["role"].lower()}_icon.png'
            eliminated_card.alive = False
            eliminated_card.show_role = True
            eliminated_card.size_hint = (None, None)
            eliminated_card.size = (dp(200), dp(250))
            eliminated_card.pos_hint = {'center_x': 0.5}
            
            # Add elimination animation
            anim = Animation(opacity=0, duration=1.5) + Animation(opacity=1, duration=0)
            anim.start(eliminated_card)
            
            results_box.add_widget(eliminated_card)
        
        # Status box
        status_box = self.create_status_box()
        
        # Continue button
        continue_btn = Button(
            text="CONTINUE TO NEXT ROUND",
            size_hint=(None, None),
            size=(dp(300), dp(60)),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.2, 0.6, 0.2, 1),
            font_size=dp(20),
            bold=True
        )
        continue_btn.bind(on_press=self.check_win_conditions)
        
        self.add_widget(header)
        self.add_widget(results_box)
        self.add_widget(status_box)
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
        
        # Background effect
        with self.canvas.before:
            Color(0, 0, 0, 0.7)
            Rectangle(size=Window.size, pos=self.pos)
        
        # Main container
        main_layout = BoxLayout(orientation='vertical', spacing=dp(20))
        
        # Result header
        header = Label(
            text="GAME OVER",
            font_size=dp(36),
            color=(0.9, 0.2, 0.2, 1),
            outline_width=3,
            outline_color=(0, 0, 0, 1),
            size_hint=(1, 0.2)
        )
        
        # Result message
        result_msg = Label(
            text=message,
            font_size=dp(24),
            color=(0.9, 0.9, 0.1, 1),
            size_hint=(1, 0.1)
        )
        
        # Player roles grid
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
            
            # Player card
            player_card = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
            
            # Player name
            player_label = Label(
                text=name,
                font_size=dp(18),
                color=(0.8, 0.8, 0.8, 1),
                size_hint_x=0.4,
                halign='left'
            )
            
            # Role and status
            role_box = BoxLayout(orientation='horizontal', size_hint_x=0.6)
            
            role_icon = Image(
                source=f'assets/{data["role"].lower()}_icon.png',
                size_hint=(0.2, 1),
                allow_stretch=True
            )
            
            role_label = Label(
                text=f"{data['role'].upper()} ({status})",
                font_size=dp(18),
                color=color,
                size_hint=(0.8, 1),
                halign='left'
            )
            
            role_box.add_widget(role_icon)
            role_box.add_widget(role_label)
            
            player_card.add_widget(player_label)
            player_card.add_widget(role_box)
            roles_box.add_widget(player_card)
        
        scroll = ScrollView(size_hint=(1, 0.6))
        scroll.add_widget(roles_box)
        
        # Restart button
        restart_btn = Button(
            text="PLAY AGAIN",
            size_hint=(None, None),
            size=(dp(200), dp(60)),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.2, 0.4, 0.8, 1),
            font_size=dp(20),
            bold=True
        )
        restart_btn.bind(on_press=self.restart_game)
        
        main_layout.add_widget(header)
        main_layout.add_widget(result_msg)
        main_layout.add_widget(scroll)
        main_layout.add_widget(restart_btn)
        
        self.add_widget(main_layout)

    def restart_game(self, instance):
        self.__init__()

    def show_popup(self, title, message, callback, image=None):
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        if image:
            content.add_widget(Image(
                source=image,
                size_hint=(1, 0.6),
                allow_stretch=True
            ))
        
        content.add_widget(Label(
            text=message,
            font_size=dp(18),
            color=(0, 0, 0, 1),
            size_hint=(1, 0.4),
            text_size=(Window.width*0.7, None)
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
            size_hint=(0.8, 0.6),
            separator_color=(0.2, 0.6, 0.2, 1),
            title_size=dp(20),
            title_color=(0, 0, 0, 1)
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
        Window.size = (1000, 750)
        return DakatiGame()

if __name__ == '__main__':
    # Create assets directory if it doesn't exist
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    # Note: In a real app, you would need to provide these image files
    # For now we'll just run with placeholder paths
    DakatiApp().run()