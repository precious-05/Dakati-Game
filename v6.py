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
import random
from collections import defaultdict
import os
# Add these imports at the top of your file
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Line, StencilPop, StencilPush, StencilUse
from kivy.animation import Animation
from kivy.uix.modalview import ModalView

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
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.2, 1
        Rectangle:
            pos: self.pos
            size: self.size
    orientation: 'vertical'
    padding: dp(20)
    spacing: dp(20)
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: dp(300)
        spacing: dp(20)
        Label:
            text: 'YOU ARE THE...'
            font_size: '36sp'
            bold: True
            color: (1, 1, 1, 1)
            outline_width: 2
            outline_color: (0, 0, 0, 1)
        Image:
            source: root.role_image
            size_hint: (1, 0.6)
            allow_stretch: True
        Label:
            text: root.role.upper()
            font_size: '48sp'
            bold: True
            color: (0.9, 0.8, 0.1, 1)
            outline_width: 2
            outline_color: (0, 0, 0, 1)
        Label:
            text: root.player_name
            font_size: '24sp'
            bold: True
            color: (0.7, 0.7, 1, 1)
        Label:
            text: root.role_description
            font_size: '18sp'
            bold: True
            color: (1, 1, 1, 1)
            text_size: self.width, None
    Button:
        text: 'Continue'
        size_hint: (None, None)
        size: (dp(200), dp(50))
        pos_hint: {'center_x': 0.5}
        background_normal: ''
        background_color: (0.2, 0.6, 0.2, 1)
        font_size: '18sp'
        bold: True
        on_press: root.dismiss()
''')

# Custom Widgets
class PlayerCard(BoxLayout):
    player_name = StringProperty('')
    role = StringProperty('')
    role_icon = StringProperty('')
    alive = BooleanProperty(True)
    show_role = BooleanProperty(False)
    selected = BooleanProperty(False)

class RoleRevealScreen(ModalView):
    role = StringProperty('')
    role_description = StringProperty('')
    player_name = StringProperty('')
    role_image = StringProperty('')


# Add these new classes before DakatiGame class
class AnimatedLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animation = None
        self.anim_done = False
        
    def start_animation(self):
        self.opacity = 0
        self.animation = (Animation(opacity=1, duration=1.5) + 
                         Animation(font_size=self.font_size * 1.2, duration=0.5) + 
                         Animation(font_size=self.font_size, duration=0.5))
        self.animation.bind(on_complete=lambda *args: setattr(self, 'anim_done', True))
        self.animation.start(self)



class PrinciplesScreen(ModalView):
    def __init__(self, on_dismiss_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.9)
        self.auto_dismiss = False
        self.on_dismiss_callback = on_dismiss_callback
        self.build_ui()
        
    def build_ui(self):
        self.layout = FloatLayout()
        
        # Background with animation
        with self.layout.canvas.before:
            self.bg = Rectangle(source='assets/principles_bg.jpg', 
                              size=self.size, 
                              pos=self.pos)
            Color(0, 0, 0, 0)
            self.overlay = Rectangle(size=self.size, pos=self.pos)
        
        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        title = AnimatedLabel(
            text="Game Principles",
            font_size=dp(28),
            bold=True,
            color=(0.9, 0.9, 0.1, 1),
            size_hint_y=None,
            height=dp(50))
        title.start_animation()
        
        scroll = ScrollView()
        content_box = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        content_box.bind(minimum_height=content_box.setter('height'))
        
        principles = [
            "1. The game has 8 players: 2 Thieves, 1 Angel, and 5 Citizens.",
            "2. During the day, all players vote to eliminate someone they suspect is a Thief.",
            "3. At night, the Thieves choose someone to kill (can't be another Thief).",
            "4. The Angel can choose to protect someone (including themselves) from being killed.",
            "5. If the Angel protects the Thieves' target, that player survives.",
            "6. If the Thieves outnumber the non-Thieves, they win immediately.",
            "7. If all Thieves are eliminated, the Citizens and Angel win.",
            "8. Players must keep their roles secret until they are eliminated."
        ]
        
        for principle in principles:
            lbl = Label(
                text=principle,
                font_size=dp(18),
                color=(0.9, 0.9, 0.9, 1),
                size_hint_y=None,
                height=dp(40),
                halign='left',
                text_size=(Window.width*0.85, None))
            content_box.add_widget(lbl)
            
        scroll.add_widget(content_box)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(20))
        back_btn = Button(
            text="Back",
            size_hint=(0, 0.99),  # Medium rectangular button
            pos_hint={'x': 0.03, 'y': 0.02},
            font_size='20sp',  # or smaller depending on design
            bold=True ,       # Bottom-left corner with slight margin,
            background_normal='',
            background_color=(0.2, 0.6, 0.2, 1))
        back_btn.bind(on_press=self.dismiss)
        
        btn_layout.add_widget(back_btn)
        
        content.add_widget(title)
        content.add_widget(scroll)
        content.add_widget(btn_layout)
        
        self.layout.add_widget(content)
        self.add_widget(self.layout)
        
        self.bind(size=self.update_bg, pos=self.update_bg)
        
    def update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos
        self.overlay.size = self.size
        self.overlay.pos = self.pos
        
    def on_dismiss(self):
        if self.on_dismiss_callback:
            self.on_dismiss_callback()
        return super().on_dismiss()
    
    

class RoleShowcaseScreen(ModalView):
    def __init__(self, on_dismiss_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.auto_dismiss = False
        self.on_dismiss_callback = on_dismiss_callback
        self.current_role_index = 0
        self.roles = [
            {
                'name': 'Thief',
                'description': 'Works with partner to eliminate citizens & Wins when thieves outnumber the others',
                'image': 'assets/thief_icon.png',
                'bg_color': (0.1, 0.1, 0.1, 0.1)
            },
            {
                'name': 'Angel',
                'description': 'Protects players from the thieves & Works with citizens to eliminate thieves',
                'image': 'assets/angel_icon.png',
                'bg_color': (0.1, 0.1, 0.1, 0.1)
            },
            {
                'name': 'Citizen',
                'description': 'Finds and eliminates thieves through voting & Wins when all thieves are eliminated',
                'image': 'assets/citizen_icon.png',
                'bg_color': (0.1, 0.1, 0.1, 0.1)
            }
        ]
        self.build_ui()
        self.show_role(0)
        
        
    def build_ui(self):
        self.layout = FloatLayout()
        
        # Background
        with self.layout.canvas.before:
            self.bg = Rectangle(source='assets/roles_bg.jpg', 
                             size=self.size, 
                             pos=self.pos)
            Color(0, 0, 0, 0)
            self.overlay = Rectangle(pos=self.pos, size=self.size)
        
        # Role display area
        self.role_box = BoxLayout(
            orientation='vertical',
            size_hint=(0.9, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.55},
            spacing=dp(20))
            
        # Next button with animation
        self.next_btn = Button(
            text="Next",
            size_hint=(0.27, 0.1),
            pos_hint={'center_x': 0.5,  'center_y':  0.1},
            background_normal='',
            font_size='18sp',
            bold=True,
            background_color=(0.2, 0.6, 0.2, 1),
            opacity=0)  # Initially hidden
        self.next_btn.bind(on_press=self.next_role)
        
        self.layout.add_widget(self.role_box)
        self.layout.add_widget(self.next_btn)
        self.add_widget(self.layout)
        
        self.bind(size=self.update_bg, pos=self.update_bg)
        
    def update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos
        self.overlay.size = self.size
        self.overlay.pos = self.pos
        
    def show_role(self, index):
        self.role_box.clear_widgets()
        role = self.roles[index]
        
        # Update background color
        with self.role_box.canvas.before:
            Color(*role['bg_color'])
            RoundedRectangle(pos=self.role_box.pos, 
                           size=self.role_box.size,
                           radius=[15,])
        
        # Animated title
        title = AnimatedLabel(
            text=role['name'],
            font_size=dp(36),
            bold=True,
            color=(0.9, 0.9, 0.1, 1),
            size_hint_y=None,
            height=dp(60))
        title.start_animation()
        
        # Role image with animation
        img = Image(
            source=role['image'],
            size_hint=(1, 0.6),
            allow_stretch=True,
            opacity=0)
        anim = (Animation(opacity=0, duration=0) + 
                Animation(opacity=1, duration=1.5, t='out_elastic'))
        anim.start(img)
        
        # Description
        desc = Label(
            text=role['description'],
            font_size=dp(22),
            color=(0.9, 0.9, 0.9, 1),
            size_hint_y=None,
            height=dp(100),
            text_size=(Window.width*0.85, None),
            halign='center',
            opacity=0)
        Animation(opacity=1, duration=1.5).start(desc)
        
        # Show next button after animations complete
        def show_next_button(dt):
            Animation(opacity=1, duration=1).start(self.next_btn)
            
        Clock.schedule_once(show_next_button, 2)
            
        self.role_box.add_widget(title)
        self.role_box.add_widget(img)
        self.role_box.add_widget(desc)
        
    def next_role(self, instance):
        self.current_role_index += 1
        if self.current_role_index >= len(self.roles):
            self.dismiss()
            if self.on_dismiss_callback:
                self.on_dismiss_callback()
        else:
            self.show_role(self.current_role_index)
            
    def on_dismiss(self):
        if self.on_dismiss_callback:
            self.on_dismiss_callback()
        return super().on_dismiss()
    
    
    
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
            Color(1, 1, 1, 1)
            self.background = Rectangle(source='assets/game_bg.jpg', 
                                     size=Window.size, 
                                     pos=self.pos)
        Window.bind(size=self.update_bg)

    def update_bg(self, *args):
        self.bg.size = Window.size
        self.overlay.size = Window.size

    def show_welcome_screen(self):
        self.clear_widgets()
        
    
    # Main container with background
        self.main_layout = FloatLayout()
    
    # Background with animation
        with self.main_layout.canvas.before:
            self.bg = Rectangle(source='assets/title_bg.jpg', 
                          size=Window.size, 
                          pos=self.pos)
            Color(0,0,0,0)
            self.overlay = Rectangle(size=Window.size, pos=self.pos)
    
    # Animated logo text
        self.logo_text = AnimatedLabel(
            #text="Dakati",
            font_size=dp(48),
            bold=True,
            color=(0.9, 0.2, 0.2, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(80),
            pos_hint={'center_x': 0.5, 'top': 0.9})
        self.logo_text.start_animation()
    
    # Principles button
        self.principles_btn = Button(
            text="Read Principles",
            size_hint=(0.2, 0.1),
            pos_hint={'center_x': 0.5, 'center_y': 0.19},
            background_normal='',
            bold= True,
            background_color=(0.2, 0.4, 0.8, 1),
            font_size=dp(20),
            opacity=0)  # Initially hidden

        # Start button with animation
        self.start_btn = Button(
            text="START GAME",
            size_hint=(0.2, 0.1),
            pos_hint={'center_x': 0.5, 'center_y': 0.08},
            background_normal='',
            background_color=(0.8, 0.2, 0.2, 1),
            font_size=dp(22),
            bold=True,
            opacity=0)  # Initially hidden

        # Add widgets
        self.main_layout.add_widget(self.logo_text)
        self.main_layout.add_widget(self.principles_btn)
        self.main_layout.add_widget(self.start_btn)
        self.add_widget(self.main_layout)

        # Animate principles button in
        Animation(opacity=1, duration=5).start(self.principles_btn)

    # Add arrow pointer after animation completes
        
        
        # Show start button after principles button is clicked or skipped
        def show_start_btn(dt):
            Animation(opacity=1, duration=5).start(self.start_btn)
            
        Clock.schedule_once(show_start_btn, 2)
    
        
    
    # Bind buttons
        self.principles_btn.bind(on_press=self.show_principles_screen)
        self.start_btn.bind(on_press=self.show_role_intro)
    
    # Update background on window resize
        Window.bind(size=self.update_bg)
    def show_principles_screen(self, instance):
    # Slide out welcome screen
        anim = Animation(x=-Window.width, duration=1, t='out_quad')
        anim.start(self.main_layout)
        # Show principles screen
        def show_principles(dt):
            self.principles_screen = PrinciplesScreen(on_dismiss_callback=self.on_principles_dismiss)
            self.principles_screen.open()
        Clock.schedule_once(show_principles, 0.7)
        
    def on_principles_dismiss(self):
    # Slide back in welcome screen
        self.main_layout.x = Window.width
        anim = Animation(x=0, duration=0.7, t='out_quad')
        anim.start(self.main_layout)
    def show_role_intro(self, instance):
    # Slide out welcome screen
        anim = Animation(y=-Window.height, duration=0.7, t='out_quad')
        anim.start(self.main_layout)
    
    # Show role showcase
        def show_roles(dt):
            self.role_screen = RoleShowcaseScreen(on_dismiss_callback=self.start_registration)
            self.role_screen.open()
        
        Clock.schedule_once(show_roles, 0.7)    
        
    def start_registration(self, instance=None):  # Make instance optional
        self.clear_widgets()
        self.current_phase = "REGISTRATION"
        # ===== ADD THESE NEW LINES FOR BACKGROUND =====
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.reg_bg = Rectangle(source='assets/register_bg.jpg', 
                                  size=Window.size, 
                                  pos=self.pos)
            Color(0, 0, 0, 0.6)
            self.reg_overlay = Rectangle(size=Window.size, pos=self.pos)
    # ===== END OF NEW BACKGROUND CODE =====
        # Animated header
        # Animated header
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.2))
        title = Label(
            text="PLAYER REGISTRATION",
            font_size=dp(28),
            color=(0.9, 0.9, 0.1, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1),
            opacity=0)  # Start hidden
    
    # Animate title in (modified animation)
        anim = (Animation(opacity=0, duration=0) + 
           Animation(opacity=1, duration=1.5, t='out_elastic'))
        anim.start(title)
        
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
            self.show_error_popup("The Player Name must be Non-Empty")
            return
        
        if len(set(self.player_names)) != 8:
            self.show_error_popup("All Players Names Must Be Unique")
            return
        
        self.assign_roles()

    def assign_roles(self):
        roles = ['Thief']*2 + ['Angel']*1 + ['Citizen']*5
        random.shuffle(roles)
        
        # Set role icons
        role_icons = {
            'Thief': 'assets/thief_icon.png',
            'Angel': 'assets/angel_icon.png',
            'Citizen': 'assets/citizen_icon.png'
        }
        
        self.players = {
            name: {
                'role': role, 
                'alive': True,
                'role_icon': role_icons[role]
            }
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
        if self.current_player_index >= len(self.player_names):
            self.start_game_loop()
            return
            
        player = self.player_names[self.current_player_index]
        role_data = self.players[player]
        
        # Create role reveal screen
        role_screen = RoleRevealScreen()
        role_screen.role = role_data['role']
        role_screen.player_name = player
        role_screen.role_image = role_data['role_icon']
        
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

    # [Rest of your existing methods remain exactly the same...]
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
        anim = Animation(color=(1, 1, 0.5, 1), duration=3) + \
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
            card.role_icon = 'assets/question_mark.png'  # Hide role during voting
            card.alive = self.players[player]['alive']
            card.show_role = False
            card.bind(on_touch_down=lambda instance, touch: self.on_card_touch(instance, touch, voter, player))
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

    def on_card_touch(self, instance, touch, voter, player):
        if instance.collide_point(*touch.pos):
            self.record_vote(voter, player)

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
            message = "Masoom citizen mar gaya 🥲😢"
        elif role == 'Thief':
            message = "Ek chor mar gaya 🤩"
        else:
            message = "Angel died 😭😢"
        
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
            text=f"Thieves {' & '.join(thieves)}, choose a target to kill 🎯",
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
            card.bind(on_touch_down=lambda instance, touch: self.on_thief_card_touch(instance, touch, player))
            grid.add_widget(card)
        
        scroll = ScrollView(size_hint=(1, 0.7))
        scroll.add_widget(grid)
        
        # Current status
        status_box = self.create_status_box()
        
        self.add_widget(header)
        self.add_widget(scroll)
        self.add_widget(status_box)

    def on_thief_card_touch(self, instance, touch, player):
        if instance.collide_point(*touch.pos):
            self.set_thieves_target(player)

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
            card.bind(on_touch_down=lambda instance, touch: self.on_angel_card_touch(instance, touch, player))
            grid.add_widget(card)
        
        scroll = ScrollView(size_hint=(1, 0.7))
        scroll.add_widget(grid)
        
        # Current status
        status_box = self.create_status_box()
        
        self.add_widget(header)
        self.add_widget(scroll)
        self.add_widget(status_box)

    def on_angel_card_touch(self, instance, touch, player):
        if instance.collide_point(*touch.pos):
            self.set_angel_choice(player)

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