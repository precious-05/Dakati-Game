from kivy.app import App
import math
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from kivy.graphics import StencilPush, StencilUse, StencilUnUse
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
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse, Line
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty, StringProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.lang import Builder
import random
from collections import defaultdict
import os
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.text import Label as CoreLabel

# Set mobile-friendly default font sizes
MOBILE_FONT_XL = '22sp'
MOBILE_FONT_LG = '18sp'
MOBILE_FONT_MD = '16sp'
MOBILE_FONT_SM = '14sp'
MOBILE_FONT_XS = '12sp'

# Card sizes for mobile
CARD_WIDTH = dp(65)
CARD_HEIGHT = dp(95)

# Configure soft input mode for mobile keyboard handling
Window.softinput_mode = 'pan'

# Load custom KV language strings with mobile sizing
Builder.load_string('''
<PlayerCard>:
    orientation: 'vertical'
    size_hint: (None, None)
    size: (dp(65), dp(95))
    canvas.before:
        Color:
            rgba: (0.1, 0.1, 0.2, 1) if not root.selected else (0.3, 0.2, 0.4, 1)
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [10,]
        Color:
            rgba: (0.8, 0.2, 0.2, 1) if not root.alive else (0.2, 0.8, 0.2, 1)
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, 10]
            width: 1.5
    Label:
        text: root.player_name
        font_size: '12sp'
        bold: True
        color: (1, 1, 1, 1)
        size_hint_y: None
        height: dp(25)
        text_size: self.width, None
        halign: 'center'
        valign: 'middle'
    Image:
        id: image
        source: root.role_icon
        size_hint: (1, 0.6)
        allow_stretch: True
        keep_ratio: True
    Label:
        text: root.role if root.show_role else '?'
        font_size: '10sp'
        color: (1, 1, 1, 1)
        size_hint_y: None
        height: dp(15)
        
<RoleRevealScreen>:
    canvas.before:
        Color:
            rgba: root.background_color
        Rectangle:
            source: root.background
            pos: self.pos
            size: self.size
            
    BoxLayout:
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(20)
        size_hint: (1, 1)
        
        Widget:
            size_hint_y: 0.15
            
        # Player Name
        Label:
            text: root.player_name
            font_size: '22sp'
            bold: True
            color: (1, 1, 1, 1)
            outline_width: 2.5
            outline_color: (0, 0, 0, 1)
            size_hint_y: None
            height: self.texture_size[1]
            halign: 'center'
        
        # Combined "Your Role is: [ROLE]"
        Label:
            text: root.role_text
            font_size: '18sp'
            bold: True
            color: (0.8, 0.5, 0.9, 1)
            outline_width: 2.5
            outline_color: (0, 0, 0, 1)
            size_hint_y: None
            height: self.texture_size[1]
            halign: 'center'
            
        Widget:
            size_hint_y: 0.35
            
        # Continue Button at bottom
        Button:
            text: 'Continue'
            size_hint: (0.8, None)
            height: dp(55)
            pos_hint: {'center_x': 0.5}
            background_normal: ''
            background_color: (0.2, 0.7, 0.2, 1)
            font_size: '16sp'
            bold: True
            on_press: root.dismiss()
''')

# Custom Widgets
class PlayerCard(ButtonBehavior, BoxLayout):
    player_name = StringProperty('')
    role = StringProperty('')
    role_icon = StringProperty('')
    alive = BooleanProperty(True)
    show_role = BooleanProperty(False)
    selected = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_card_pressed')
        
    def on_press(self):
        self.dispatch('on_card_pressed')
    
    def on_card_pressed(self, *args):
        if hasattr(self, 'callback'):
            self.callback(self.player_name)

class RoleRevealScreen(ModalView):
    role_text = StringProperty('')
    player_name = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background = 'assets/role_reveal_bg.jpg'
        self.background_color = (0.1, 0.1, 0.1, 0.1)
        self.size_hint = (0.95, 0.9)
        
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
        self.size_hint = (1, 1)
        self.auto_dismiss = False
        self.on_dismiss_callback = on_dismiss_callback
        self.build_ui()
        
    def build_ui(self):
        # Draw background on ModalView canvas, responsive and bound
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(source='assets/principles_bg.jpg', 
                              size=self.size, 
                              pos=self.pos)
            Color(0, 0, 0, 0.65) # Dark overlay for high readability
            self.overlay = Rectangle(size=self.size, pos=self.pos)
            
        self.bind(size=self.update_bg, pos=self.update_bg)
        
        self.layout = FloatLayout()
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))
        
        title = AnimatedLabel(
            text="Game Principles",
            font_size=MOBILE_FONT_XL,
            bold=True,
            color=(0.9, 0.9, 0.1, 1),
            size_hint_y=None,
            height=dp(40),
            halign='center'
        )
        title.start_animation()
        
        scroll = ScrollView()
        content_box = BoxLayout(orientation='vertical', spacing=dp(18), size_hint_y=None)
        content_box.bind(minimum_height=content_box.setter('height'))
        
        principles = [ 
            "1. The game has 8 players: 2 Thieves, 1 Angel and 5 normal Citizens. Everyone is called a citizen at first",
            "2. Only the two Thieves know each other's roles but they don't know who the Angel is",
            "3. The Angel doesn't know anyone's identity",
            "4. In Voting Phase all players vote to eliminate a suspicious player",
            "5. The player with most votes is eliminated",
            "6. In Thieves' Phase the two Thieves select one alive player to attack",
            "7. In Angel's Phase the Angel guesses who was targeted to save them",
            "8. If Angel guesses correctly, target is saved. If wrong, target is eliminated",
            "9. Game continues until Thieves are eliminated (Citizens win) or Thieves outnumber Citizens"
        ]
        
        for principle in principles:
            lbl = Label(
                text=principle,
                font_size=MOBILE_FONT_SM,
                bold=True,
                color=(1, 1, 0.9, 1),
                size_hint_y=None,
                height=dp(70),
                halign='left',
                valign='middle',
                outline_width=1.5,
                outline_color=(0, 0, 0, 1),
                size_hint_x=1
            )
            # Bind width to text_size to enable responsive text wrapping
            lbl.bind(width=lambda instance, val: setattr(instance, 'text_size', (val, None)))
            content_box.add_widget(lbl)
            
        scroll.add_widget(content_box)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        back_btn = Button(
            text="Back",
            size_hint=(1, 1),
            font_size=MOBILE_FONT_MD,
            bold=True,
            background_normal='',
            background_color=(0.2, 0.6, 0.2, 1))
        back_btn.bind(on_press=self.dismiss)
        
        btn_layout.add_widget(back_btn)
        
        content.add_widget(title)
        content.add_widget(scroll)
        content.add_widget(btn_layout)
        
        self.layout.add_widget(content)
        self.add_widget(self.layout)
        
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
                'description': '''Works with partner to eliminate citizens & Wins when thieves outnumber the others''',
                'image': 'assets/thief_icon.png',
                'bg_color': (0.1, 0.1, 0.15, 0.85)
            },
            {
                'name': 'Angel',
                'description': '''Protects players from the thieves & Works with citizens to eliminate thieves''',
                'image': 'assets/angel_icon.png',
                'bg_color': (0.1, 0.1, 0.15, 0.85)
            },
            {
                'name': 'Citizen',
                'description': '''Finds and eliminates thieves through voting & Wins when all thieves are eliminated''',
                'image': 'assets/citizen_icon.png',
                'bg_color': (0.1, 0.1, 0.15, 0.85)
            }
        ]
        self.build_ui()
        self.show_role(0)
        
    def build_ui(self):
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(source='assets/roles_bg.jpg', 
                              size=self.size, 
                              pos=self.pos)
            Color(0, 0, 0, 0.5)
            self.overlay = Rectangle(pos=self.pos, size=self.size)
            
        self.bind(size=self.update_bg, pos=self.update_bg)
        
        self.layout = FloatLayout()
        
        self.role_box = BoxLayout(
            orientation='vertical',
            size_hint=(0.85, 0.65),
            pos_hint={'center_x': 0.5, 'center_y': 0.55},
            spacing=dp(15),
            padding=dp(20))
            
        with self.role_box.canvas.before:
            self.role_color = Color(0.1, 0.1, 0.15, 0.85)
            self.role_box_bg = RoundedRectangle(
                pos=self.role_box.pos, 
                size=self.role_box.size,
                radius=[15,]
            )
            self.role_border_color = Color(0.3, 0.3, 0.5, 1)
            self.role_box_border = Line(
                rounded_rectangle=[self.role_box.x, self.role_box.y, self.role_box.width, self.role_box.height, 15],
                width=1.5
            )
            
        self.role_box.bind(pos=self.update_role_box_bg, size=self.update_role_box_bg)
            
        self.next_btn = Button(
            text="Next",
            size_hint=(0.6, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.12},
            background_normal='',
            font_size=MOBILE_FONT_MD,
            bold=True,
            background_color=(0.2, 0.6, 0.2, 1),
            opacity=0)
        self.next_btn.bind(on_press=self.next_role)
        
        self.layout.add_widget(self.role_box)
        self.layout.add_widget(self.next_btn)
        self.add_widget(self.layout)
        
    def update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos
        self.overlay.size = self.size
        self.overlay.pos = self.pos
        
    def update_role_box_bg(self, instance, value):
        self.role_box_bg.pos = instance.pos
        self.role_box_bg.size = instance.size
        self.role_box_border.rounded_rectangle = [
            instance.x, instance.y, instance.width, instance.height, 15
        ]
        
    def show_role(self, index):
        self.role_box.clear_widgets()
        role = self.roles[index]
        
        # Update colors dynamically
        self.role_color.rgba = role['bg_color']
        
        title = AnimatedLabel(
            text=role['name'].upper(),
            font_size=MOBILE_FONT_XL,
            bold=True,
            color=(0.9, 0.9, 0.1, 1),
            size_hint_y=None,
            outline_width=2,
            outline_color=(0, 0, 0, 1),
            height=dp(50),
            halign='center')
        title.start_animation()
        
        img = Image(
            source=role['image'],
            size_hint=(1, 0.55),
            allow_stretch=True,
            keep_ratio=True,
            opacity=0)
        anim = (Animation(opacity=0, duration=0) + 
                Animation(opacity=1, duration=1.5, t='out_quad'))
        anim.start(img)
        
        scroll = ScrollView(size_hint=(1, 0.3))
        desc = Label(
            text=role['description'],
            font_size=MOBILE_FONT_SM,
            color=(0.95, 0.95, 0.95, 1),
            size_hint_y=None,
            height=dp(80),
            halign='center',
            valign='middle',
            outline_color=(0,0,0,1),
            outline_width=1.5,
            bold=False,
            opacity=0)
        desc.bind(width=lambda instance, val: setattr(instance, 'text_size', (val, None)))
        Animation(opacity=1, duration=1.5).start(desc)
        scroll.add_widget(desc)
        
        def show_next_button(dt):
            Animation(opacity=1, duration=0.5).start(self.next_btn)
            
        Clock.schedule_once(show_next_button, 1.2)
            
        self.role_box.add_widget(title)
        self.role_box.add_widget(img)
        self.role_box.add_widget(scroll)
        
    def next_role(self, instance):
        self.current_role_index += 1
        if self.current_role_index >= len(self.roles):
            self.dismiss()
            if self.on_dismiss_callback:
                self.on_dismiss_callback()
        else:
            self.next_btn.opacity = 0
            self.show_role(self.current_role_index)
            
    def on_dismiss(self):
        if self.on_dismiss_callback:
            self.on_dismiss_callback()
        return super().on_dismiss()
    
class DakatiGame(BoxLayout):
    current_phase = StringProperty("")
    background_default = StringProperty('assets/default_bg.jpg')
    background_registration = StringProperty('assets/register_bg.jpg')
    background_role_reveal = StringProperty('assets/role_reveal_bg.jpg')
    background_voting = StringProperty('assets/voting_bg.jpg')
    background_thieves = StringProperty('assets/thieves_bg.jpg')
    background_angel = StringProperty('assets/angel_bg.jpg')
    background_results = StringProperty('assets/results_bg.jpg')
    background_gameover = StringProperty('assets/gameover_bg.jpg')
    background_principles = StringProperty('assets/principles_bg.jpg')
    round_number = NumericProperty(1)
    alive_players = ListProperty([])
    eliminated_players = ListProperty([])
    background_image = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(10)
        
        self.players = {}
        self.player_names = []
        self.current_votes = defaultdict(int)
        self.thieves_target = None
        self.angel_choice = None
        self.current_player_viewing = None
        self.eliminated_in_voting = None
        
        # We bind DakatiGame's size and pos to update background layout
        self.bind(size=self.update_bg, pos=self.update_bg)
        
        self.setup_background()
        self.show_welcome_screen()

    def setup_background(self, phase=None):
        """Set up background with proper aspect ratio scaling and zero instruction leaking"""
        if phase is None:
            bg_source = 'assets/default_bg.jpg'
        else:
            bg_source = getattr(self, f'background_{phase.lower()}', 'assets/default_bg.jpg')

        # Control overlay intensity depending on the game phase
        overlay_alpha = 0.7 if phase in ["GAMEOVER", "GAME_OVER"] else 0.0

        if not hasattr(self, 'bg_rect'):
            with self.canvas.before:
                Color(1, 1, 1, 1)
                self.bg_rect = Rectangle(
                    source=bg_source,
                    size=self._calculate_bg_size(self.size),
                    pos=self._calculate_bg_pos(self.size)
                )
                self.bg_overlay_color = Color(0, 0, 0, overlay_alpha)
                self.bg_overlay = Rectangle(
                    size=self.size,
                    pos=self.pos
                )
        else:
            self.bg_rect.source = bg_source
            self.bg_rect.size = self._calculate_bg_size(self.size)
            self.bg_rect.pos = self._calculate_bg_pos(self.size)
            self.bg_overlay_color.rgba = (0, 0, 0, overlay_alpha)
            self.bg_overlay.size = self.size
            self.bg_overlay.pos = self.pos
            
    def _calculate_bg_size(self, size):
        """Calculate size to maintain 9:16 aspect ratio while COVERING the entire screen (no black bars)"""
        w, h = size
        if h == 0:
            return (0, 0)
        window_ratio = w / h
        target_ratio = 9/16
        
        if window_ratio > target_ratio:
            # Viewport is wider, match width
            return (w, w / target_ratio)
        else:
            # Viewport is taller, match height
            return (h * target_ratio, h)

    def _calculate_bg_pos(self, size):
        """Center the background image"""
        bg_size = self._calculate_bg_size(size)
        return (
            (size[0] - bg_size[0]) / 2,
            (size[1] - bg_size[1]) / 2
        )        

    def update_bg(self, instance, value):
        """Update background when window size changes"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.size = self._calculate_bg_size(self.size)
            self.bg_rect.pos = self._calculate_bg_pos(self.size)
        if hasattr(self, 'bg_overlay'):
            self.bg_overlay.size = self.size
            self.bg_overlay.pos = self.pos

    def show_welcome_screen(self):
        self.clear_widgets()

        self.main_layout = FloatLayout()

        # Slideshow background
        self.slideshow_images = [
            'assets/slide1.jpg',
            'assets/slide2.jpg',
            'assets/slide3.jpg',
            'assets/slide4.jpg',
            'assets/slide5.jpg',
            'assets/slide6.jpg',
            'assets/slide7.jpg'
        ]
        self.current_slide = 0

        # Create slideshow image widget - full screen background (covers screen)
        self.slideshow = Image(
            source=self.slideshow_images[0],
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            allow_stretch=True,
            keep_ratio=False
        )
        self.main_layout.add_widget(self.slideshow)

        # Start slideshow immediately
        def start_slideshow(dt):
            def change_slide(dt):
                next_slide = (self.current_slide + 1) % len(self.slideshow_images)

                # Fade out current slide
                anim_out = Animation(opacity=0, duration=0.6)
                anim_out.start(self.slideshow)

                def update_and_fade_in(dt):
                    self.slideshow.source = self.slideshow_images[next_slide]
                    anim_in = Animation(opacity=1, duration=0.6)
                    anim_in.start(self.slideshow)
                    self.current_slide = next_slide

                Clock.schedule_once(update_and_fade_in, 0.6)

            self.slideshow_event = Clock.schedule_interval(change_slide, 5)

        Clock.schedule_once(start_slideshow, 0)

        # Prominent stylized Game Title
        title_label = Label(
            text="DAKATI\n[color=ffd700]THE THIEF GAME[/color]",
            markup=True,
            font_size='38sp',
            bold=True,
            halign='center',
            valign='middle',
            size_hint=(0.9, 0.25),
            pos_hint={'center_x': 0.5, 'center_y': 0.72},
            outline_width=2.5,
            outline_color=(0, 0, 0, 1),
            opacity=0
        )
        self.main_layout.add_widget(title_label)
        Animation(opacity=1, y=Window.height * 0.65, duration=1.5, t='out_quad').start(title_label)

        # Button card layout for glassmorphism grouping
        button_container = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint=(0.8, 0.22),
            pos_hint={'center_x': 0.5, 'center_y': 0.25},
            opacity=0
        )
        
        with button_container.canvas.before:
            Color(0.08, 0.08, 0.15, 0.65) # Sleek semi-transparent card background
            self.welcome_card_bg = RoundedRectangle(
                pos=button_container.pos,
                size=button_container.size,
                radius=[16,]
            )
            Color(0.3, 0.3, 0.5, 0.8)
            self.welcome_card_border = Line(
                rounded_rectangle=[button_container.x, button_container.y, button_container.width, button_container.height, 16],
                width=1.2
            )
            
        button_container.bind(pos=self._update_welcome_card, size=self._update_welcome_card)

        # Principles Button
        self.principles_btn = Button(
            text="Read Principles",
            size_hint=(1, 0.45),
            background_normal='',
            bold=True,
            background_color=(0.15, 0.35, 0.75, 1),
            font_size=MOBILE_FONT_MD
        )

        # Start Game Button
        self.start_btn = Button(
            text="START GAME",
            size_hint=(1, 0.45),
            background_normal='',
            background_color=(0.75, 0.15, 0.15, 1),
            font_size=MOBILE_FONT_MD,
            bold=True
        )
        
        button_container.add_widget(self.principles_btn)
        button_container.add_widget(self.start_btn)
        self.main_layout.add_widget(button_container)

        # Animate button container appearing
        Animation(opacity=1, duration=1.2).start(button_container)

        # Bind button events
        self.principles_btn.bind(on_press=self.show_principles_screen)
        self.start_btn.bind(on_press=self.show_role_intro)

        self.add_widget(self.main_layout)

    def _update_welcome_card(self, instance, value):
        self.welcome_card_bg.pos = instance.pos
        self.welcome_card_bg.size = instance.size
        self.welcome_card_border.rounded_rectangle = [
            instance.x, instance.y, instance.width, instance.height, 16
        ]

    def show_principles_screen(self, instance):
        if hasattr(self, 'slideshow_event'):
            self.slideshow_event.cancel()
        anim = Animation(x=-Window.width, duration=0.6, t='out_quad')
        anim.start(self.main_layout)
        
        def show_principles(dt):
            self.principles_screen = PrinciplesScreen(on_dismiss_callback=self.on_principles_dismiss)
            self.principles_screen.open()
        Clock.schedule_once(show_principles, 0.4)
        
    def on_principles_dismiss(self):
        self.main_layout.x = Window.width
        anim = Animation(x=0, duration=0.8, t='out_quad')
        anim.start(self.main_layout)
        self.show_welcome_screen()
        
    def show_role_intro(self, instance):
        if hasattr(self, 'slideshow_event'):
            self.slideshow_event.cancel()
        anim = Animation(y=-Window.height, duration=0.5, t='out_quad')
        anim.start(self.main_layout)
        
        def show_roles(dt):
            self.role_screen = RoleShowcaseScreen(on_dismiss_callback=self.start_registration)
            self.role_screen.open()
        
        Clock.schedule_once(show_roles, 0.4)
        
    def start_registration(self, instance=None):
        self.setup_background("registration")
        self.clear_widgets()
        self.current_phase = "REGISTRATION"

        header = BoxLayout(orientation='vertical', size_hint=(1, 0.15), spacing=dp(5))

        title = Label(
            text="PLAYER REGISTRATION",
            font_size=MOBILE_FONT_XL,
            bold=True,
            color=(0.9, 0.9, 0.1, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(40)
        )
        header.add_widget(title)

        instruction = Label(
            text="Enter names for all 8 players (must contain a number):",
            font_size=MOBILE_FONT_SM,
            bold=True,
            color=(0.95, 0.95, 0.95, 1),
            outline_width=1.5,
            outline_color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(30)
        )
        header.add_widget(instruction)

        input_grid = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(10)
        )
        input_grid.bind(minimum_height=input_grid.setter('height'))

        self.player_inputs = []
        for i in range(8):
            input_box = BoxLayout(orientation='horizontal', 
                                 size_hint_y=None, 
                                 height=dp(48),
                                 spacing=dp(8))

            num_box = BoxLayout(orientation='horizontal',
                              size_hint=(0.3, 1),
                              spacing=dp(4))
            num_box.add_widget(Image(source=f'assets/player_{i+1}.png',
                                  size_hint=(0.4, 1),
                                  allow_stretch=True,
                                  keep_ratio=True))
            num_box.add_widget(Label(
                text=f"P{i+1}:",
                font_size=MOBILE_FONT_SM,
                bold=True,
                color=(0.9, 0.9, 0.9, 1),
                outline_width=1.5,
                outline_color=(0, 0, 0, 1),
                size_hint=(0.6, 1))
            )

            player_input = TextInput(
                multiline=False,
                size_hint=(0.7, 1),
                background_normal='',
                background_color=(0.08, 0.08, 0.15, 0.8),
                foreground_color=(1, 1, 1, 1),
                hint_text_color=(0.6, 0.6, 0.7, 1),
                cursor_color=(1, 1, 1, 1),
                font_size=MOBILE_FONT_SM,
                hint_text=f"Name {i+1}",
                padding=[dp(10), dp(12), dp(10), dp(12)]
            )
            self.player_inputs.append(player_input)
            input_box.add_widget(num_box)
            input_box.add_widget(player_input)
            input_grid.add_widget(input_box)

        scroll = ScrollView(size_hint=(1, 0.7))
        scroll.add_widget(input_grid)

        submit_btn = Button(
            text="CONFIRM PLAYERS",
            size_hint=(0.85, None),
            height=dp(50),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.15, 0.55, 0.15, 1),
            font_size=MOBILE_FONT_MD,
            bold=True
        )
        submit_btn.bind(on_press=self.validate_registration)

        self.add_widget(header)
        self.add_widget(scroll)
        self.add_widget(submit_btn)

    def validate_registration(self, instance):
        self.player_names = [input.text.strip() for input in self.player_inputs]

        if any(not name for name in self.player_names):
            self.show_error_popup("Player names cannot be empty")
            return

        for name in self.player_names:
            if not any(char.isdigit() for char in name):
                self.show_error_popup("Each username must contain at least one number")
                return

        if len(set(self.player_names)) != len(self.player_names):
            self.show_error_popup("All Player names must be unique")
            return

        self.assign_roles()
        
    def assign_roles(self):
        roles = ['Thief']*2 + ['Angel']*1 + ['Citizen']*5
        random.shuffle(roles)
        
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
        
        thieves = [name for name, data in self.players.items() if data['role'] == 'Thief']
        for thief in thieves:
            self.players[thief]['known_thieves'] = [
                t for t in thieves if t != thief
            ]
        
        self.show_role_reveal_screen()

    def show_role_reveal_screen(self):
        self.clear_widgets()
        self.setup_background("role_reveal")
        
        self.current_phase = "ROLE_REVEAL"
        self.current_player_index = 0
        self.update_role_reveal()

    def update_role_reveal(self):
        if self.current_player_index >= len(self.player_names):
            self.start_game_loop()
            return

        player = self.player_names[self.current_player_index]
        role_data = self.players[player]

        role_screen = RoleRevealScreen()
        role_screen.player_name = player
        role_screen.role_text = 'Your Role is: ' + role_data['role'].upper()

        role_screen.bind(on_dismiss=lambda x: self.next_role_reveal())
        role_screen.open()
    
    def next_role_reveal(self):
        self.current_player_index += 1
        Clock.schedule_once(lambda dt: self.update_role_reveal(), 0.4)

    def start_game_loop(self):
        self.current_phase = "GAME_LOOP"
        self.round_number = 1
        self.update_alive_players()
        self.show_voting_phase()
    
    def show_voting_phase(self):
        self.setup_background("voting")
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

        # Header with phase information
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.14), spacing=dp(2))
        phase_label = Label(
            text=f"Round {self.round_number}: Voting Phase",
            font_size=MOBILE_FONT_LG,
            bold=True,
            color=(0.9, 0.9, 0.1, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1)
        )
        anim = Animation(color=(1, 1, 0.6, 1), duration=0.6) + \
               Animation(color=(0.9, 0.9, 0.1, 1), duration=0.6)
        anim.repeat = True
        anim.start(phase_label)

        instruction = Label(
            text=f"{voter}, vote to eliminate:",
            font_size=MOBILE_FONT_MD,
            bold=True,
            color=(0.95, 0.95, 0.95, 1),
            outline_width=1.5,
            outline_color=(0, 0, 0, 1)
        )
        header.add_widget(phase_label)
        header.add_widget(instruction)

        # Circular layout container
        circle_container = FloatLayout(size_hint=(1, 0.72))

        # Get available voting options
        options = [p for p in self.alive_players if p != voter]
        if role_data['role'] == 'Thief':
            options = [p for p in options if p not in role_data['known_thieves']]

        cards = []
        for player in options:
            card = PlayerCard()
            card.player_name = player
            card.role = self.players[player]['role']
            card.role_icon = 'assets/question_mark.png'
            card.alive = self.players[player]['alive']
            card.show_role = False
            card.size_hint = (None, None)
            
            # Adjust image size inside card
            card.ids.image.size_hint = (0.9, 0.55)
            card.ids.image.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

            card.bind(on_release=lambda x, p=player: self.record_vote(voter, p))
            circle_container.add_widget(card)
            cards.append(card)

        # Dynamic positioning logic bound to layout resizing
        def layout_cards(instance, value):
            num_options = len(cards)
            if num_options == 0:
                return

            center_x = instance.width / 2
            center_y = instance.height / 2
            radius = min(instance.width, instance.height) * 0.36

            base_card_width = dp(65)
            base_card_height = dp(95)

            if num_options > 5:
                scale_factor = 0.9 - (min(num_options, 8) - 5) * 0.08
                card_width = base_card_width * scale_factor
                card_height = base_card_height * scale_factor
            else:
                card_width = base_card_width
                card_height = base_card_height

            angle_step = 360 / num_options

            for idx, card_widget in enumerate(cards):
                angle = math.radians(idx * angle_step)
                x = center_x + radius * math.cos(angle) - card_width/2
                y = center_y + radius * math.sin(angle) - card_height/2
                
                card_widget.size = (card_width, card_height)
                card_widget.pos = (instance.x + x, instance.y + y)

        circle_container.bind(size=layout_cards, pos=layout_cards)
        Clock.schedule_once(lambda dt: layout_cards(circle_container, None), 0)

        status_box = self.create_status_box()

        self.add_widget(header)
        self.add_widget(circle_container)
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
        self.update_alive_players()
        self.eliminated_in_voting = eliminated

        role = self.players[eliminated]['role']
        if role == 'Citizen':
            message = "Masoom citizen mar gaya!"
            image = 'assets/eliminated.png'
        elif role == 'Thief':
            message = "Ek chor pakda gaya!"
            image = 'assets/thief_died.png'
        else:
            message = "Angel bhi mar gaya!"
            image = 'assets/angel_died.png'

        self.show_popup(
            "Voting Result",
            message,
            self.show_thieves_phase,
            image
        )
        
    def show_thieves_phase(self):
        self.setup_background("thieves")
        self.current_phase = "THIEVES"

        thieves = [name for name, data in self.players.items() 
                  if data['alive'] and data['role'] == 'Thief']

        if not thieves:
            self.show_angel_phase()
            return

        self.thieves_target = None
        self.clear_widgets()

        header = BoxLayout(orientation='vertical', size_hint=(1, 0.14))
        phase_label = Label(
            text="Thieves' Phase",
            font_size=MOBILE_FONT_LG,
            color=(0.9, 0.2, 0.2, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1)
        )
        anim = Animation(color=(1, 0.4, 0.4, 1), duration=0.6) + \
               Animation(color=(0.9, 0.2, 0.2, 1), duration=0.6)
        anim.repeat = True
        anim.start(phase_label)

        instruction = Label(
            text=f"Thieves {' & '.join(thieves)}, choose a target to kill 🎯",
            font_size=MOBILE_FONT_SM,
            outline_color=(0,0,0,1),
            outline_width=1.5,
            color=(0.9, 0.9, 0.9, 1)
        )
        header.add_widget(phase_label)
        header.add_widget(instruction)

        targets = [name for name, data in self.players.items() 
                  if data['alive'] and data['role'] != 'Thief']

        # Center the grid in a scroll view
        scroll = ScrollView(
            size_hint=(1, 0.72),
            pos_hint={'center_x': 0.5}
        )

        grid = GridLayout(
            spacing=dp(12),
            padding=dp(15),
            size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter('height'))
        scroll.add_widget(grid)

        # Dynamic layout adaptation for grid elements
        def adjust_grid(instance, value):
            col_width = CARD_WIDTH + dp(18)
            cols = max(3, int(instance.width / col_width))
            grid.cols = cols
            
            grid_card_width = (instance.width - dp(30) - (cols - 1) * grid.spacing[0]) / cols
            grid_card_height = grid_card_width * 1.45
            
            for child in grid.children:
                if isinstance(child, PlayerCard):
                    child.size = (grid_card_width, grid_card_height)

        scroll.bind(size=adjust_grid)

        for player in targets:
            card = PlayerCard()
            card.player_name = player
            card.role = self.players[player]['role']
            card.role_icon = 'assets/question_mark.png'
            card.alive = self.players[player]['alive']
            card.show_role = False
            card.size_hint = (None, None)
            card.bind(on_card_pressed=lambda instance, p=player: self.set_thieves_target(p))
            grid.add_widget(card)

        Clock.schedule_once(lambda dt: adjust_grid(scroll, None), 0)

        status_box = self.create_status_box()

        self.add_widget(header)
        self.add_widget(scroll)
        self.add_widget(status_box)    

    def set_thieves_target(self, target):
        print(f"Thieves selected: {target}")
        self.thieves_target = target
        
        self.show_popup(
            "Target Locked",
            f"Thieves have selected a target to eliminate.",
            self.show_angel_phase
        )

    def show_angel_phase(self):
        self.setup_background("angel")
        self.clear_widgets()
        self.current_phase = "ANGEL"
        angel = next((name for name, data in self.players.items() 
                     if data['alive'] and data['role'] == 'Angel'), None)
        
        if not angel or not self.thieves_target:
            self.show_round_results()
            return
            
        self.angel_choice = None
        self.clear_widgets()
        
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.14))
        phase_label = Label(
            text="Angel's Phase",
            font_size=MOBILE_FONT_LG,
            color=(0.4, 0.4, 0.9, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1)
        )
        anim = Animation(color=(0.5, 0.5, 1, 1), duration=0.6) + \
               Animation(color=(0.4, 0.4, 0.9, 1), duration=0.6)
        anim.repeat = True
        anim.start(phase_label)
        
        instruction = Label(
            text=f"Angel {angel}, choose someone to save:",
            font_size=MOBILE_FONT_SM,
            outline_color=(0,0,0,1),
            outline_width=1.5,
            bold=True,
            color=(0.9, 0.9, 0.1, 1)
        )
        header.add_widget(phase_label)
        header.add_widget(instruction)
        
        targets = [name for name, data in self.players.items() if data['alive']]
        
        # Center the grid in a scroll view
        scroll = ScrollView(
            size_hint=(1, 0.72),
            pos_hint={'center_x': 0.5}
        )
        
        grid = GridLayout(
            spacing=dp(12),
            padding=dp(15),
            size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter('height'))
        scroll.add_widget(grid)

        def adjust_grid_angel(instance, value):
            col_width = CARD_WIDTH + dp(18)
            cols = max(3, int(instance.width / col_width))
            grid.cols = cols
            
            grid_card_width = (instance.width - dp(30) - (cols - 1) * grid.spacing[0]) / cols
            grid_card_height = grid_card_width * 1.45
            
            for child in grid.children:
                if isinstance(child, PlayerCard):
                    child.size = (grid_card_width, grid_card_height)

        scroll.bind(size=adjust_grid_angel)

        for player in targets:
            card = PlayerCard()
            card.player_name = player
            card.role = self.players[player]['role']
            card.role_icon = 'assets/question_mark.png'
            card.alive = self.players[player]['alive']
            card.show_role = False
            card.size_hint = (None, None)
            card.bind(on_card_pressed=lambda instance, p=player: self.set_angel_choice(p))
            grid.add_widget(card)
        
        Clock.schedule_once(lambda dt: adjust_grid_angel(scroll, None), 0)
        
        status_box = self.create_status_box()
        
        self.add_widget(header)
        self.add_widget(scroll)
        self.add_widget(status_box)

    def update_alive_players(self):
        self.alive_players = [name for name, data in self.players.items() if data['alive']]
        self.eliminated_players = [name for name, data in self.players.items() if not data['alive']]  

    def set_angel_choice(self, target):
        self.angel_choice = target
        target_role = self.players[self.thieves_target]['role']
        image = None
        message = ""

        if self.angel_choice == self.thieves_target:
            if target_role == 'Angel':
                message = "Angel saved themselves!"
                image = 'assets/angel_saved.png'
            else:
                message = "Angel has saved the citizen!"
                image = 'assets/citizen_icon.png'
        else:
            self.players[self.thieves_target]['alive'] = False
            if target_role == 'Angel':
                message = "Angel failed to save themselves!"
                image = 'assets/angel_died.png'
            else:
                message = "Angel has failed to save the citizen!"
                image = 'assets/citizen_died.png'

        self.update_alive_players()
        self.show_popup("Angel's Decision", message, self.show_round_results, image)

    def create_status_box(self):
        status_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.14))
        
        alive_box = BoxLayout(orientation='vertical', size_hint=(0.5, 1))
        alive_box.add_widget(Label(
            text="Alive Players:",
            font_size=MOBILE_FONT_SM,
            bold=True,
            outline_color=(0,0,0,1),
            outline_width=1.5,
            color=(0.2, 0.8, 0.2, 1)
        ))
        alive_box.add_widget(Label(
            text=", ".join(self.alive_players),
            font_size=MOBILE_FONT_XS,
            bold=False,
            outline_color=(0,0,0,1),
            outline_width=1.0,
            color=(1, 1, 1, 1)
        ))
        
        eliminated_box = BoxLayout(orientation='vertical', size_hint=(0.5, 1))
        eliminated_box.add_widget(Label(
            text="Eliminated Players:",
            font_size=MOBILE_FONT_SM,
            bold=True,
            outline_color=(0,0,0,1),
            outline_width=1.5,
            color=(0.8, 0.2, 0.2, 1)
        ))
        eliminated_box.add_widget(Label(
            text=", ".join(self.eliminated_players) if self.eliminated_players else 'None',
            font_size=MOBILE_FONT_XS,
            bold=False,
            outline_color=(0,0,0,1),
            outline_width=1.0,
            color=(0.85, 0.85, 0.85, 1)
        ))
        
        status_box.add_widget(alive_box)
        status_box.add_widget(eliminated_box)
        return status_box

    def show_round_results(self):
        self.setup_background("results")
        self.clear_widgets()
        self.current_phase = "RESULTS"
        
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.14))
        phase_label = Label(
            text=f"Round {self.round_number} Results",
            font_size=MOBILE_FONT_LG,
            bold=True,
            color=(0.9, 0.9, 0.1, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1)
        )
        anim = Animation(color=(1, 1, 0.6, 1), duration=0.6) + \
               Animation(color=(0.9, 0.9, 0.1, 1), duration=0.6)
        anim.repeat = True
        anim.start(phase_label)
        header.add_widget(phase_label)
        
        results_box = BoxLayout(orientation='vertical', size_hint=(1, 0.58))
        
        if self.eliminated_in_voting:
            eliminated_card = PlayerCard()
            eliminated_card.player_name = self.eliminated_in_voting
            eliminated_card.role = self.players[self.eliminated_in_voting]['role']
            eliminated_card.role_icon = f'assets/{self.players[self.eliminated_in_voting]["role"].lower()}_icon.png'
            eliminated_card.alive = False
            eliminated_card.show_role = True
            eliminated_card.size_hint = (None, None)
            eliminated_card.size = (dp(140), dp(190))
            eliminated_card.pos_hint = {'center_x': 0.5}
            
            anim_fade = Animation(opacity=0, duration=0) + Animation(opacity=1, duration=1.2)
            anim_fade.start(eliminated_card)
            
            results_box.add_widget(eliminated_card)
        
        status_box = self.create_status_box()
        
        continue_btn = Button(
            text="CONTINUE TO NEXT ROUND",
            size_hint=(0.85, None),
            height=dp(50),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.15, 0.55, 0.15, 1),
            font_size=MOBILE_FONT_MD,
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
            self.show_final_results("CITIZENS WON!\nAll thieves have been eliminated")
        elif alive_thieves >= alive_citizens:
            self.show_final_results("THIEVES WON!\nThey outnumber the citizens")
        else:
            self.round_number += 1
            self.show_voting_phase()

    def show_final_results(self, message):
        self.setup_background("gameover")
        self.clear_widgets()
        self.current_phase = "GAME_OVER"
        
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(12))
        
        header = Label(
            text="GAME OVER",
            font_size=MOBILE_FONT_XL,
            color=(0.9, 0.2, 0.2, 1),
            outline_width=3,
            outline_color=(0, 0, 0, 1),
            size_hint=(1, 0.15)
        )
        
        result_msg = Label(
            text=message,
            font_size=MOBILE_FONT_LG,
            outline_color=(0,0,0,1),
            outline_width=2,
            color=(0.9, 0.9, 0.1, 1),
            size_hint=(1, 0.12),
            halign='center'
        )
        
        roles_box = GridLayout(
            cols=1,
            spacing=dp(6),
            padding=dp(8),
            size_hint_y=None
        )
        roles_box.bind(minimum_height=roles_box.setter('height'))
        
        for name, data in self.players.items():
            status = "ALIVE" if data['alive'] else "ELIMINATED"
            color = (0.2, 0.8, 0.2, 1) if data['alive'] else (0.8, 0.2, 0.2, 1)
            
            player_card = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(42), spacing=dp(8))
            
            player_label = Label(
                text=name,
                font_size=MOBILE_FONT_SM,
                color=(0.9, 0.9, 0.9, 1),
                size_hint_x=0.4,
                halign='left',
                outline_width=1.0,
                outline_color=(0,0,0,1)
            )
            
            role_box = BoxLayout(orientation='horizontal', size_hint_x=0.6, spacing=dp(5))
            
            role_icon = Image(
                source=f'assets/{data["role"].lower()}_icon.png',
                size_hint=(0.25, 1),
                allow_stretch=True,
                keep_ratio=True
            )
            
            role_label = Label(
                text=f"{data['role'].upper()} ({status})",
                font_size=MOBILE_FONT_SM,
                color=color,
                size_hint=(0.75, 1),
                halign='left',
                outline_width=1.0,
                outline_color=(0,0,0,1)
            )
            
            role_box.add_widget(role_icon)
            role_box.add_widget(role_label)
            
            player_card.add_widget(player_label)
            player_card.add_widget(role_box)
            roles_box.add_widget(player_card)
        
        scroll = ScrollView(size_hint=(1, 0.58))
        scroll.add_widget(roles_box)
        
        restart_btn = Button(
            text="PLAY AGAIN",
            size_hint=(0.8, None),
            height=dp(50),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.15, 0.35, 0.75, 1),
            font_size=MOBILE_FONT_MD,
            bold=True
        )
        restart_btn.bind(on_press=self.restart_game)
        
        main_layout.add_widget(header)
        main_layout.add_widget(result_msg)
        main_layout.add_widget(scroll)
        main_layout.add_widget(restart_btn)
        
        self.add_widget(main_layout)

    def restart_game(self, instance):
        self.clear_widgets()
        # Reset background overlay
        if hasattr(self, 'bg_overlay_color'):
            self.bg_overlay_color.rgba = (0, 0, 0, 0)
        self.__init__()

    def show_popup(self, title, message, callback, image=None):
        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(15))

        # Modern glassmorphism / dark slate dialog card
        with content.canvas.before:
            Color(0.08, 0.08, 0.15, 0.95)
            popup_bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[12,])
            Color(0.3, 0.3, 0.5, 0.8)
            popup_border = Line(rounded_rectangle=[content.x, content.y, content.width, content.height, 12], width=1.5)

        # Responsive canvas update handler
        def update_popup_bg(instance, value):
            popup_bg.pos = instance.pos
            popup_bg.size = instance.size
            popup_border.rounded_rectangle = [instance.x, instance.y, instance.width, instance.height, 12]

        content.bind(pos=update_popup_bg, size=update_popup_bg)

        # Custom title label inside layout (cleaner than default separator)
        clean_title = title.split(']')[-1] if ']' in title else title
        title_lbl = Label(
            text=clean_title.upper(),
            font_size=MOBILE_FONT_LG,
            bold=True,
            color=(0.9, 0.9, 0.1, 1),
            size_hint_y=None,
            height=dp(30),
            halign='center'
        )
        content.add_widget(title_lbl)

        if image:
            img = Image(
                source=image,
                size_hint=(1, 0.5),
                allow_stretch=True,
                keep_ratio=True
            )
            content.add_widget(img)

        message_label = Label(
            text=message,
            font_size=MOBILE_FONT_MD,
            markup=True,
            color=(0.95, 0.95, 0.95, 1),
            size_hint=(1, 0.3),
            bold=True,
            halign='center',
            valign='middle'
        )
        message_label.bind(width=lambda instance, val: setattr(instance, 'text_size', (val, None)))
        content.add_widget(message_label)
        
        btn = Button(
            text="OK",
            size_hint=(0.6, None),
            height=dp(42),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.15, 0.55, 0.15, 1),
            color=(1, 1, 1, 1),
            bold=True
        )

        popup = Popup(
            title="",
            title_size=0,
            separator_height=0,
            content=content,
            size_hint=(0.85, 0.55),
            background=''
        )

        btn.bind(on_press=popup.dismiss)
        btn.bind(on_press=lambda x: callback())
        content.add_widget(btn)
        popup.open()

    def show_error_popup(self, message):
        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(15))

        with content.canvas.before:
            Color(0.15, 0.05, 0.05, 0.95) # Dark red overlay
            popup_bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[10,])
            Color(0.8, 0.2, 0.2, 0.8)
            popup_border = Line(rounded_rectangle=[content.x, content.y, content.width, content.height, 10], width=1.5)

        def update_popup_bg(instance, value):
            popup_bg.pos = instance.pos
            popup_bg.size = instance.size
            popup_border.rounded_rectangle = [instance.x, instance.y, instance.width, instance.height, 10]

        content.bind(pos=update_popup_bg, size=update_popup_bg)

        title_lbl = Label(
            text="ERROR",
            font_size=MOBILE_FONT_LG,
            bold=True,
            color=(0.9, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(30),
            halign='center'
        )
        content.add_widget(title_lbl)

        msg_lbl = Label(
            text=message,
            font_size=MOBILE_FONT_SM,
            bold=True,
            color=(0.95, 0.95, 0.95, 1),
            size_hint=(1, 0.5),
            halign='center',
            valign='middle'
        )
        msg_lbl.bind(width=lambda instance, val: setattr(instance, 'text_size', (val, None)))
        content.add_widget(msg_lbl)

        btn = Button(
            text="OK",
            size_hint=(0.8, None),
            height=dp(40),
            pos_hint={'center_x': 0.5},
            background_normal='',
            background_color=(0.8, 0.2, 0.2, 1),
            bold=True
        )

        popup = Popup(
            title="",
            title_size=0,
            separator_height=0,
            content=content,
            size_hint=(0.8, 0.45),
            background=''
        )

        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

class DakatiApp(App):
    def build(self):
        self.title = 'Dakati Game'
        # Standard mobile size for testing on desktop
        Window.size = (480, 850)
        return DakatiGame()

if __name__ == '__main__':
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    DakatiApp().run()
