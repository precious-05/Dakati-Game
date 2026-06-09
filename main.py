from kivy.app import App
import math
from kivy.graphics import PushMatrix, PopMatrix, Rotate, Scale
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
from kivy.core.audio import SoundLoader
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.text import Label as CoreLabel
from kivy.utils import platform

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
<GameButton>:
    background_normal: ''
    background_color: (0, 0, 0, 0)
    canvas.before:
        PushMatrix:
        Scale:
            origin: self.center
            x: self.scale_value
            y: self.scale_value
        Color:
            rgba: self.custom_bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14),]
    canvas.after:
        PopMatrix:

<GameTextInput>:
    background_normal: ''
    background_active: ''
    background_color: (0, 0, 0, 0)
    cursor_color: (1, 1, 1, 1)
    foreground_color: (1, 1, 1, 1)
    canvas.before:
        Color:
            rgba: (0.08, 0.08, 0.15, 0.8)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10),]
        Color:
            rgba: (0.88, 0.65, 0.12, 1) if self.focus else (0.3, 0.3, 0.5, 0.6)
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, 10]
            width: 1.5 if self.focus else 1.0

<PlayerCard>:
    orientation: 'vertical'
    size_hint: (None, None)
    size: (dp(65), dp(95))
    canvas.before:
        PushMatrix:
        Scale:
            origin: self.center
            x: self.scale_value
            y: self.scale_value
        Color:
            rgba: (0.1, 0.1, 0.2, 0.85) if not root.selected else (0.35, 0.2, 0.5, 0.9)
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [12,]
        Color:
            rgba: (0.8, 0.2, 0.2, 1) if not root.alive else ((0.88, 0.65, 0.12, 1) if root.selected else (0.3, 0.3, 0.5, 0.8))
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, 12]
            width: 2.0 if root.selected else 1.2
    canvas.after:
        PopMatrix:

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
    background: 'assets/role_reveal_bg.jpg'
    background_color: (1, 1, 1, 1)
    canvas.before:
        Color:
            rgba: (1, 1, 1, 1)
        Rectangle:
            source: root.background
            pos: self.pos
            size: self.size
        Color:
            rgba: (0, 0, 0, 0.55)
        Rectangle:
            pos: self.pos
            size: self.size
            
    BoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(15)
        size_hint: (1, 1)
        
        Widget:
            size_hint_y: 0.08
            
        Label:
            text: root.player_name.upper()
            font_size: '26sp'
            bold: True
            color: (1, 0.85, 0.3, 1)
            outline_width: 2.0
            outline_color: (0, 0, 0, 1)
            size_hint_y: None
            height: dp(35)
            halign: 'center'
            
        BoxLayout:
            orientation: 'vertical'
            size_hint: (None, None)
            size: (dp(160), dp(160))
            pos_hint: {'center_x': 0.5}
            padding: dp(6)
            canvas.before:
                Color:
                    rgba: (0.88, 0.65, 0.12, 1)
                Line:
                    rounded_rectangle: [self.x, self.y, self.width, self.height, 20]
                    width: 2.5
                Color:
                    rgba: (0.08, 0.08, 0.15, 0.75)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [20,]
            Image:
                source: root.role_icon
                allow_stretch: True
                keep_ratio: True
                
        Label:
            text: root.role_text
            font_size: '20sp'
            bold: True
            color: (1, 1, 1, 1)
            outline_width: 2.0
            outline_color: (0, 0, 0, 1)
            size_hint_y: None
            height: dp(30)
            halign: 'center'
            
        Label:
            text: root.role_description
            font_size: '14sp'
            color: (0.9, 0.9, 0.95, 1)
            outline_width: 1.5
            outline_color: (0, 0, 0, 1)
            size_hint_y: None
            height: dp(50)
            text_size: self.width - dp(20), None
            halign: 'center'
            valign: 'middle'
            
        Widget:
            size_hint_y: 0.05
            
        GameButton:
            text: 'CONTINUE'
            size_hint: (0.85, None)
            height: dp(50)
            pos_hint: {'center_x': 0.5}
            custom_bg_color: (0.12, 0.64, 0.38, 1)
            font_size: '16sp'
            bold: True
            on_press: root.dismiss()
''')

class FitImage(Image):
    """Cover-fill image: fills its box, cropping to maintain aspect ratio.
    Uses Kivy's native Image pipeline so textures are always right-side up."""

    def __init__(self, **kwargs):
        kwargs.setdefault('allow_stretch', True)
        kwargs.setdefault('keep_ratio', False)
        super().__init__(**kwargs)

class DarkOverlay(Widget):
    alpha = NumericProperty(0.0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        with self.canvas:
            self.color = Color(0, 0, 0, self.alpha)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update, pos=self._update)
        
    def _update(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
        
    def on_alpha(self, instance, value):
        self.color.rgba = (0, 0, 0, value)

class GameButton(Button):
    scale_value = NumericProperty(1.0)
    custom_bg_color = ListProperty([0.35, 0.25, 0.7, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.markup = True
        
    def on_press(self):
        Animation(scale_value=0.92, duration=0.08, t='out_quad').start(self)
        
    def on_release(self):
        Animation(scale_value=1.0, duration=0.15, t='out_bounce').start(self)

class GameTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color = (0, 0, 0, 0)
        self.cursor_color = (1, 1, 1, 1)
        self.foreground_color = (1, 1, 1, 1)

# Custom Widgets
class PlayerCard(ButtonBehavior, BoxLayout):
    player_name = StringProperty('')
    role = StringProperty('')
    role_icon = StringProperty('')
    alive = BooleanProperty(True)
    show_role = BooleanProperty(False)
    selected = BooleanProperty(False)
    scale_value = NumericProperty(1.0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_card_pressed')
        
    def on_press(self):
        Animation(scale_value=0.92, duration=0.08, t='out_quad').start(self)
        self.dispatch('on_card_pressed')
        
    def on_release(self):
        Animation(scale_value=1.0, duration=0.15, t='out_bounce').start(self)
    
    def on_card_pressed(self, *args):
        if hasattr(self, 'callback'):
            self.callback(self.player_name)

class RoleRevealScreen(ModalView):
    role_text = StringProperty('')
    player_name = StringProperty('')
    role_icon = StringProperty('')
    role_description = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background = 'assets/role_reveal_bg.jpg'
        self.background_color = (1, 1, 1, 1)
        self.size_hint = (1, 1)

class GameMenuModal(ModalView):
    def __init__(self, game_instance, **kwargs):
        super().__init__(**kwargs)
        self.game = game_instance
        self.size_hint = (0.85, 0.65)
        self.auto_dismiss = True
        self.background = ''
        self.background_color = (0, 0, 0, 0)
        self.build_ui()
        
    def build_ui(self):
        with self.canvas.before:
            Color(0.05, 0.05, 0.1, 0.95)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20,])
            Color(0.3, 0.3, 0.5, 0.8)
            self.border_line = Line(rounded_rectangle=[self.x, self.y, self.width, self.height, 20], width=2.0)
        self.bind(pos=self._update, size=self._update)
        
        layout = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(20))
        
        title = Label(
            text="GAME MENU",
            font_size=MOBILE_FONT_LG,
            bold=True,
            color=(0.9, 0.9, 0.1, 1),
            size_hint_y=None,
            height=dp(35),
            halign='center'
        )
        layout.add_widget(title)
        
        resume_btn = GameButton(
            text="RESUME GAME",
            size_hint_y=None,
            height=dp(45),
            custom_bg_color=(0.12, 0.64, 0.38, 1),
            bold=True
        )
        resume_btn.bind(on_press=self.dismiss)
        layout.add_widget(resume_btn)
        
        principles_btn = GameButton(
            text="VIEW PRINCIPLES",
            size_hint_y=None,
            height=dp(45),
            custom_bg_color=(0.35, 0.25, 0.7, 1),
            bold=True
        )
        principles_btn.bind(on_press=self.view_principles)
        layout.add_widget(principles_btn)
        
        roles_btn = GameButton(
            text="VIEW ROLES INFO",
            size_hint_y=None,
            height=dp(45),
            custom_bg_color=(0.35, 0.25, 0.7, 1),
            bold=True
        )
        roles_btn.bind(on_press=self.view_roles)
        layout.add_widget(roles_btn)
        
        history_btn = GameButton(
            text="ELIMINATION HISTORY",
            size_hint_y=None,
            height=dp(45),
            custom_bg_color=(0.88, 0.65, 0.12, 1),
            bold=True
        )
        history_btn.bind(on_press=self.view_history)
        layout.add_widget(history_btn)
        
        restart_btn = GameButton(
            text="RESTART GAME",
            size_hint_y=None,
            height=dp(45),
            custom_bg_color=(0.85, 0.2, 0.25, 1),
            bold=True
        )
        restart_btn.bind(on_press=self.confirm_restart)
        layout.add_widget(restart_btn)
        
        exit_btn = GameButton(
            text="EXIT TO WELCOME SCREEN",
            size_hint_y=None,
            height=dp(45),
            custom_bg_color=(0.85, 0.2, 0.25, 1),
            bold=True
        )
        exit_btn.bind(on_press=self.confirm_exit)
        layout.add_widget(exit_btn)
        
        self.add_widget(layout)
        
    def _update(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rounded_rectangle = [self.x, self.y, self.width, self.height, 20]
        
    def view_principles(self, *args):
        self.dismiss()
        principles_screen = PrinciplesScreen(on_dismiss_callback=None)
        principles_screen.open()
        
    def view_roles(self, *args):
        self.dismiss()
        roles_screen = RoleShowcaseScreen(on_dismiss_callback=None)
        roles_screen.open()
        
    def view_history(self, *args):
        self.dismiss()
        history_modal = HistoryModal(self.game)
        history_modal.open()
        
    def confirm_restart(self, *args):
        self.dismiss()
        self.game.show_confirmation_popup("Restart Game?", "Are you sure you want to restart? All progress will be lost.", self.game.restart_game)
        
    def confirm_exit(self, *args):
        self.dismiss()
        self.game.show_confirmation_popup("Exit Game?", "Are you sure you want to exit to the welcome screen?", self.game.exit_to_welcome)

class HistoryModal(ModalView):
    def __init__(self, game_instance, **kwargs):
        super().__init__(**kwargs)
        self.game = game_instance
        self.size_hint = (0.9, 0.7)
        self.auto_dismiss = True
        self.background = ''
        self.background_color = (0, 0, 0, 0)
        self.build_ui()
        
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(15))
        
        with self.canvas.before:
            Color(0.05, 0.05, 0.1, 0.95)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20,])
            Color(0.3, 0.3, 0.5, 0.8)
            self.border_line = Line(rounded_rectangle=[self.x, self.y, self.width, self.height, 20], width=2.0)
        self.bind(pos=self._update, size=self._update)
        
        title = Label(
            text="ELIMINATION HISTORY",
            font_size=MOBILE_FONT_LG,
            bold=True,
            color=(0.9, 0.9, 0.1, 1),
            size_hint_y=None,
            height=dp(35),
            halign='center'
        )
        layout.add_widget(title)
        
        scroll = ScrollView(size_hint=(1, 0.75))
        history_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        history_layout.bind(minimum_height=history_layout.setter('height'))
        
        if not self.game.game_history:
            no_hist = Label(
                text="No events recorded yet. The game has just started!",
                font_size=MOBILE_FONT_SM,
                color=(0.8, 0.8, 0.8, 1),
                size_hint_y=None,
                height=dp(50),
                halign='center'
            )
            history_layout.add_widget(no_hist)
        else:
            for item in self.game.game_history:
                item_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(65), spacing=dp(2))
                
                with item_box.canvas.before:
                    Color(0.1, 0.1, 0.18, 0.7)
                    item_bg = RoundedRectangle(pos=item_box.pos, size=item_box.size, radius=[8,])
                def update_item_bg(instance, value, bg=item_bg):
                    bg.pos = instance.pos
                    bg.size = instance.size
                item_box.bind(pos=update_item_bg, size=update_item_bg)
                
                header_lbl = Label(
                    text=f"ROUND {item['round']} - {item['phase'].upper()}",
                    font_size=MOBILE_FONT_XS,
                    bold=True,
                    color=(0.88, 0.65, 0.12, 1),
                    size_hint_y=0.35,
                    halign='left',
                    padding=[dp(8), 0]
                )
                header_lbl.bind(width=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                
                event_lbl = Label(
                    text=item['event'],
                    font_size=MOBILE_FONT_SM,
                    color=(0.95, 0.95, 0.95, 1),
                    size_hint_y=0.65,
                    halign='left',
                    valign='middle',
                    padding=[dp(8), dp(4)]
                )
                event_lbl.bind(width=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                
                item_box.add_widget(header_lbl)
                item_box.add_widget(event_lbl)
                history_layout.add_widget(item_box)
                
        scroll.add_widget(history_layout)
        layout.add_widget(scroll)
        
        close_btn = GameButton(
            text="CLOSE",
            size_hint_y=None,
            height=dp(45),
            custom_bg_color=(0.35, 0.25, 0.7, 1),
            bold=True
        )
        close_btn.bind(on_press=self.dismiss)
        layout.add_widget(close_btn)
        
        self.add_widget(layout)
        
    def _update(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rounded_rectangle = [self.x, self.y, self.width, self.height, 20]
        
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
        self.background = ''
        self.background_color = (0, 0, 0, 0)
        self.on_dismiss_callback = on_dismiss_callback
        self.build_ui()

    def build_ui(self):
        root = FloatLayout()

        # Full-screen background image
        bg = FitImage(
            source='assets/principles_bg.jpg',
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        root.add_widget(bg)

        # Light overlay — just enough to keep text readable without hiding the bg
        with root.canvas.after:
            Color(0, 0, 0, 0.30)
            self._overlay_rect = Rectangle(size=root.size, pos=root.pos)
        root.bind(size=self._upd_overlay, pos=self._upd_overlay)
        self._root_ref = root

        # Main vertical content card (lighter glassmorphism)
        outer = BoxLayout(
            orientation='vertical',
            size_hint=(0.92, 0.92),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=dp(10),
            padding=[dp(14), dp(14), dp(14), dp(10)]
        )
        with outer.canvas.before:
            Color(0.06, 0.06, 0.14, 0.55)
            self._outer_bg = RoundedRectangle(pos=outer.pos, size=outer.size, radius=[dp(18)])
            Color(0.88, 0.65, 0.12, 0.7)
            self._outer_border = Line(
                rounded_rectangle=[outer.x, outer.y, outer.width, outer.height, dp(18)],
                width=1.8
            )
        outer.bind(pos=self._upd_outer, size=self._upd_outer)

        # Title row
        title_lbl = Label(
            text='GAME PRINCIPLES',
            font_size='20sp',
            bold=True,
            color=(0.88, 0.65, 0.12, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(40),
            halign='center'
        )
        outer.add_widget(title_lbl)

        # Scrollable list of principle cards
        scroll = ScrollView(size_hint=(1, 1))
        cards_col = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, padding=[0, dp(4)])
        cards_col.bind(minimum_height=cards_col.setter('height'))

        principles = [
            ("1", "The game has 8 players: 2 Thieves, 1 Angel and 5 Citizens. Everyone is introduced as a Citizen at first."),
            ("2", "Only the two Thieves know each other's roles — but they do NOT know who the Angel is."),
            ("3", "The Angel doesn't know anyone's identity."),
            ("4", "In the Voting Phase, all players discuss and vote to eliminate one suspicious player."),
            ("5", "The player with the most votes is eliminated from the game."),
            ("6", "In the Thieves' Phase, the two Thieves secretly choose one alive player to attack."),
            ("7", "In the Angel's Phase, the Angel guesses who was targeted by the Thieves to save them."),
            ("8", "If the Angel guesses correctly, the target is saved. If wrong, the target is eliminated."),
            ("9", "The game continues until all Thieves are eliminated (Citizens win) or Thieves outnumber Citizens (Thieves win)."),
        ]

        for num, text in principles:
            card = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                spacing=dp(10),
                padding=[dp(10), dp(8), dp(10), dp(8)]
            )
            # Dynamic height: tall enough for wrapped text
            card.height = dp(68)
            with card.canvas.before:
                Color(0.1, 0.1, 0.22, 0.78)
                c_bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
                Color(0.88, 0.65, 0.12, 0.35)
                c_border = Line(
                    rounded_rectangle=[card.x, card.y, card.width, card.height, dp(12)],
                    width=1.2
                )
            def _upd_card(inst, val, b=c_bg, l=c_border):
                b.pos = inst.pos; b.size = inst.size
                l.rounded_rectangle = [inst.x, inst.y, inst.width, inst.height, dp(12)]
            card.bind(pos=_upd_card, size=_upd_card)

            # Gold number badge
            num_lbl = Label(
                text=num,
                font_size='18sp',
                bold=True,
                color=(0.88, 0.65, 0.12, 1),
                size_hint=(None, 1),
                width=dp(28),
                halign='center',
                valign='middle'
            )
            # Principle text
            txt_lbl = Label(
                text=text,
                font_size='12sp',
                color=(0.95, 0.95, 0.95, 1),
                halign='left',
                valign='middle',
                size_hint=(1, 1)
            )
            txt_lbl.bind(
                width=lambda inst, val: setattr(inst, 'text_size', (val, None)),
                texture_size=lambda inst, val: setattr(inst.parent, 'height',
                    max(dp(68), val[1] + dp(18))) if inst.parent else None
            )
            card.add_widget(num_lbl)
            card.add_widget(txt_lbl)
            cards_col.add_widget(card)

        scroll.add_widget(cards_col)
        outer.add_widget(scroll)

        # Back button
        back_btn = GameButton(
            text='BACK',
            size_hint=(1, None),
            height=dp(48),
            custom_bg_color=(0.12, 0.64, 0.38, 1),
            font_size=MOBILE_FONT_MD,
            bold=True
        )
        back_btn.bind(on_press=self.dismiss)
        outer.add_widget(back_btn)

        root.add_widget(outer)
        self.add_widget(root)

    def _upd_overlay(self, inst, val):
        self._overlay_rect.size = inst.size
        self._overlay_rect.pos = inst.pos

    def _upd_outer(self, inst, val):
        self._outer_bg.pos = inst.pos
        self._outer_bg.size = inst.size
        self._outer_border.rounded_rectangle = [inst.x, inst.y, inst.width, inst.height, dp(18)]

    def on_dismiss(self):
        if self.on_dismiss_callback:
            self.on_dismiss_callback()
        return super().on_dismiss()

    
class RoleShowcaseScreen(ModalView):
    def __init__(self, on_dismiss_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.auto_dismiss = False
        self.background = ''
        self.background_color = (0, 0, 0, 0)
        self.on_dismiss_callback = on_dismiss_callback
        self.current_role_index = 0
        self.roles = [
            {
                'name': 'Thief',
                'description': 'Works secretly with a partner to eliminate Citizens one by one. Wins when Thieves outnumber the remaining players.',
                'image': 'assets/thief_icon.png',
                'accent': (0.85, 0.2, 0.2, 1),
                'glow': (0.9, 0.1, 0.1, 0.4),
            },
            {
                'name': 'Angel',
                'description': 'Protects players from the Thieves\' attack each round. Works alongside Citizens to expose and eliminate Thieves.',
                'image': 'assets/angel_icon.png',
                'accent': (0.3, 0.7, 1.0, 1),
                'glow': (0.1, 0.5, 0.9, 0.4),
            },
            {
                'name': 'Citizen',
                'description': 'Uses reason and debate to identify Thieves in the Voting Phase. Wins when all Thieves have been eliminated.',
                'image': 'assets/citizen_icon.png',
                'accent': (0.88, 0.65, 0.12, 1),
                'glow': (0.8, 0.5, 0.0, 0.4),
            },
        ]
        self.build_ui()
        self.show_role(0)

    def wrap_text_by_words(self, text, words_per_line=4):
        words = text.split()
        lines = []
        for i in range(0, len(words), words_per_line):
            lines.append(" ".join(words[i:i+words_per_line]))
        return "\n".join(lines)

    def build_ui(self):
        self.root_layout = FloatLayout()

        # Full-screen background — the image IS the frame, no overlay or card needed
        self.bg_img = FitImage(
            source='assets/roles_bg.jpg',
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.root_layout.add_widget(self.bg_img)

        # Content sits directly inside the frame area of roles_bg.jpg
        # Frame inner area is approx: x=13%, y=12%, w=74%, h=76% of screen
        # We increase top padding to push the title down from the top edge of the frame
        self.content_box = BoxLayout(
            orientation='vertical',
            spacing=dp(12),
            padding=[dp(12), dp(35), dp(12), dp(10)],  # Top padding 30 (increase)
            size_hint=(0.63, 0.70),  # WIDTH 60% (pehle 74% tha), HEIGHT 70%
            pos_hint={'center_x': 0.5, 'center_y': 0.48}  # POSITION Y = 48% (neeche)
            )
        self.root_layout.add_widget(self.content_box)

        # "Next / Done" button at bottom of screen, outside frame
        self.next_btn = GameButton(
            text='NEXT >>',
            size_hint=(0.55, None),
            height=dp(46),
            pos_hint={'center_x': 0.5, 'center_y': 0.07},
            custom_bg_color=(0.12, 0.64, 0.38, 1),
            font_size=MOBILE_FONT_MD,
            bold=True,
            opacity=0
        )
        self.next_btn.bind(on_press=self.next_role)
        self.root_layout.add_widget(self.next_btn)
        self.add_widget(self.root_layout)

    # --- role display ----------------------------------------------------
    def show_role(self, index):
        self.content_box.clear_widgets()
        role = self.roles[index]
        accent = role['accent']

        print(f"[ROLES INFO] Showing role: {role['name']}")

        # --- Role name title (large, bold, accent color) ---
        title = Label(
            text=role['name'].upper(),
            font_size='26sp',
            bold=True,
            color=accent,
            outline_width=2,
            outline_color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(46),
            halign='center',
            opacity=0
        )
        Animation(opacity=1, duration=0.5, t='out_quad').start(title)

        # --- Role icon — framed container matching role's accent color ---
        img_container = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(dp(120), dp(120)),
            pos_hint={'center_x': 0.5},
            padding=dp(6),
            opacity=0
        )
        with img_container.canvas.before:
            Color(0.08, 0.08, 0.15, 0.6)
            img_bg = RoundedRectangle(pos=img_container.pos, size=img_container.size, radius=[dp(15)])
            Color(*accent[:3], 0.8)
            img_border = Line(rounded_rectangle=[img_container.x, img_container.y, img_container.width, img_container.height, dp(15)], width=2.0)
            
        def _upd_img_frame(inst, val, bg=img_bg, border=img_border):
            bg.pos = inst.pos
            bg.size = inst.size
            border.rounded_rectangle = [inst.x, inst.y, inst.width, inst.height, dp(15)]
            
        img_container.bind(pos=_upd_img_frame, size=_upd_img_frame)
        
        icon_img = Image(
            source=role['image'],
            allow_stretch=True,
            keep_ratio=True
        )
        img_container.add_widget(icon_img)
        Animation(opacity=1, duration=0.8, t='out_quad').start(img_container)

        # --- Description Glass Card ---
        desc_card = BoxLayout(
            orientation='vertical',
            size_hint=(0.8, None),
            height=dp(115),
            pos_hint={'center_x': 0.5},
            padding=[dp(12), dp(10), dp(12), dp(10)],
            opacity=0
        )
        with desc_card.canvas.before:
            Color(0.05, 0.05, 0.12, 0.75)
            desc_bg = RoundedRectangle(pos=desc_card.pos, size=desc_card.size, radius=[dp(12)])
            Color(*accent[:3], 0.6)
            desc_border = Line(rounded_rectangle=[desc_card.x, desc_card.y, desc_card.width, desc_card.height, dp(12)], width=1.5)
            
        def _upd_desc_card(inst, val, bg=desc_bg, border=desc_border):
            bg.pos = inst.pos
            bg.size = inst.size
            border.rounded_rectangle = [inst.x, inst.y, inst.width, inst.height, dp(12)]
            
        desc_card.bind(pos=_upd_desc_card, size=_upd_desc_card)
        
        wrapped_desc = self.wrap_text_by_words(role['description'], 4)
        desc_lbl = Label(
            text=wrapped_desc,
            font_size='12sp',
            color=(0.95, 0.95, 0.95, 1),
            halign='center',
            valign='middle',
            size_hint=(1, 1)
        )
        desc_lbl.bind(width=lambda inst, val: setattr(inst, 'text_size', (val, None)))
        desc_card.add_widget(desc_lbl)
        Animation(opacity=1, duration=1.0, t='out_quad').start(desc_card)

        # --- Page indicator dots ---
        dots_row = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size=(dp(72), dp(18)),
            pos_hint={'center_x': 0.5},
            spacing=dp(10)
        )
        for i, _ in enumerate(self.roles):
            dot = Label(
                text='O' if i == index else 'o',
                font_size='12sp',
                color=accent if i == index else (0.5, 0.5, 0.5, 1),
                size_hint=(None, None),
                size=(dp(18), dp(18))
            )
            dots_row.add_widget(dot)

        self.content_box.add_widget(title)
        self.content_box.add_widget(img_container)
        self.content_box.add_widget(desc_card)
        self.content_box.add_widget(dots_row)
        self.content_box.add_widget(Widget(size_hint_y=1))

        # Show next button after brief delay
        self.next_btn.opacity = 0
        is_last = (index >= len(self.roles) - 1)
        self.next_btn.text = 'START GAME >>' if is_last else 'NEXT >>'
        self.next_btn.custom_bg_color = (0.35, 0.25, 0.7, 1) if is_last else (0.12, 0.64, 0.38, 1)
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=0.5).start(self.next_btn), 1.0)

    def next_role(self, instance):
        self.current_role_index += 1
        if self.current_role_index >= len(self.roles):
            self.dismiss()
        else:
            self.show_role(self.current_role_index)

    def on_dismiss(self):
        if self.on_dismiss_callback:
            self.on_dismiss_callback()
        return super().on_dismiss()

    
class DakatiGame(FloatLayout):
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
    game_history = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.players = {}
        self.player_names = []
        self.current_votes = defaultdict(int)
        self.thieves_target = None
        self.angel_choice = None
        self.current_player_viewing = None
        self.eliminated_in_voting = None
        self.eliminated_at_night = None
        self.game_history = []
        self.music_muted = False
        self.current_sound = None
        self.current_track_name = None
        
        # 1. Background image layer
        self.bg_image = FitImage(source='assets/default_bg.jpg', size_hint=(1, 1))
        super().add_widget(self.bg_image)
        
        # 2. Dark Overlay layer
        self.bg_overlay = DarkOverlay()
        super().add_widget(self.bg_overlay)
        
        # 3. Main content layer
        self.main_content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(12),
            size_hint=(1, 1)
        )
        super().add_widget(self.main_content)
        
        self.setup_background()
        self.show_welcome_screen()

    def add_widget(self, widget, *args, **kwargs):
        if widget in (self.bg_image, self.bg_overlay, self.main_content):
            super().add_widget(widget, *args, **kwargs)
        else:
            self.main_content.add_widget(widget, *args, **kwargs)
            
    def clear_widgets(self, children=None):
        if children is None:
            self.main_content.clear_widgets()
        else:
            for child in children:
                if child in self.main_content.children:
                    self.main_content.remove_widget(child)

    def change_screen(self, build_layout_callback, phase_name):
        anim_out = Animation(opacity=0, duration=0.3, t='out_quad')
        
        def on_fade_out(*args):
            self.clear_widgets()
            self.setup_background(phase_name)
            build_layout_callback()
            self.main_content.opacity = 0
            anim_in = Animation(opacity=1, duration=0.4, t='out_quad')
            anim_in.start(self.main_content)
            
        anim_out.bind(on_complete=on_fade_out)
        anim_out.start(self.main_content)

    def setup_background(self, phase=None):
        if phase is None:
            bg_source = 'assets/default_bg.jpg'
        else:
            bg_source = getattr(self, f'background_{phase.lower()}', 'assets/default_bg.jpg')
            
        self.bg_image.source = bg_source
        
        if phase in ["GAMEOVER", "GAME_OVER"]:
            self.bg_overlay.alpha = 0.7
        else:
            self.bg_overlay.alpha = 0.15
            
        self.update_music(phase)

    def update_music(self, phase=None):
        if self.music_muted:
            self.stop_music()
            return

        # Determine track based on phase/state
        p = (phase or self.current_phase or "").upper()
        if p == "VOTING":
            track = "suspense.mp3"
        elif p == "THIEVES":
            track = "thieves.mp3"
        elif p == "ANGEL":
            track = "angel.mp3"
        else:
            track = "detect.mp3"

        if self.current_track_name == track:
            if self.current_sound and self.current_sound.state == 'stop':
                self.current_sound.play()
            return

        if self.current_sound:
            self.current_sound.stop()

        self.current_track_name = track
        if os.path.exists(track):
            self.current_sound = SoundLoader.load(track)
            if self.current_sound:
                self.current_sound.loop = True
                self.current_sound.play()
        else:
            print(f"[AUDIO WARN] Audio file {track} not found in root directory.")

    def stop_music(self):
        if self.current_sound:
            self.current_sound.stop()

    def toggle_mute(self, instance=None):
        self.music_muted = not self.music_muted
        if self.music_muted:
            self.stop_music()
        else:
            self.current_track_name = None # force reloading the music
            self.update_music()
        self.update_mute_buttons_ui()

    def update_mute_buttons_ui(self):
        def walk_and_update(widget):
            if isinstance(widget, GameButton) and widget.text in ["🔊", "🔇", "SOUND ON", "SOUND OFF"]:
                widget.text = "SOUND OFF" if self.music_muted else "SOUND ON"
            if hasattr(widget, 'children'):
                for child in widget.children:
                    walk_and_update(child)
        walk_and_update(self)

    def create_game_header(self, phase_title, instruction_text=None):
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.16), spacing=dp(4))
        
        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.6), spacing=dp(8))
        
        title_lbl = Label(
            text=phase_title,
            font_size=MOBILE_FONT_LG,
            bold=True,
            color=(0.9, 0.9, 0.1, 1),
            outline_width=2.0,
            outline_color=(0, 0, 0, 1),
            size_hint=(0.5, 1),
            halign='left',
            valign='middle'
        )
        title_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
        
        mute_btn = GameButton(
            text="SOUND OFF" if self.music_muted else "SOUND ON",
            size_hint=(0.28, 0.8),
            pos_hint={'center_y': 0.5},
            custom_bg_color=(0.15, 0.15, 0.22, 0.9),
            font_size=MOBILE_FONT_XS,
            bold=True
        )
        mute_btn.bind(on_press=self.toggle_mute)
        
        menu_btn = GameButton(
            text="= MENU",
            size_hint=(0.22, 0.8),
            pos_hint={'center_y': 0.5},
            custom_bg_color=(0.15, 0.15, 0.22, 0.9),
            font_size=MOBILE_FONT_XS,
            bold=True
        )
        menu_btn.bind(on_press=lambda x: self.open_game_menu())
        
        top_bar.add_widget(title_lbl)
        top_bar.add_widget(mute_btn)
        top_bar.add_widget(menu_btn)
        header.add_widget(top_bar)
        
        if instruction_text:
            instr_lbl = Label(
                text=instruction_text,
                font_size=MOBILE_FONT_SM,
                bold=True,
                color=(0.95, 0.95, 0.95, 1),
                outline_width=1.5,
                outline_color=(0, 0, 0, 1),
                size_hint=(1, 0.4),
                halign='center',
                valign='middle'
            )
            header.add_widget(instr_lbl)
            
        return header

    def open_game_menu(self):
        menu = GameMenuModal(self)
        menu.open()

    def show_confirmation_popup(self, title, message, on_confirm_callback):
        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(15))
        
        with content.canvas.before:
            Color(0.08, 0.08, 0.15, 0.95)
            popup_bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[12,])
            Color(0.3, 0.3, 0.5, 0.8)
            popup_border = Line(rounded_rectangle=[content.x, content.y, content.width, content.height, 12], width=1.5)
            
        def update_popup_bg(instance, value):
            popup_bg.pos = instance.pos
            popup_bg.size = instance.size
            popup_border.rounded_rectangle = [instance.x, instance.y, instance.width, instance.height, 12]
        content.bind(pos=update_popup_bg, size=update_popup_bg)
        
        title_lbl = Label(
            text=title.upper(),
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
            color=(0.95, 0.95, 0.95, 1),
            size_hint=(1, 0.4),
            halign='center',
            valign='middle'
        )
        msg_lbl.bind(width=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
        content.add_widget(msg_lbl)
        
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(42))
        
        cancel_btn = GameButton(
            text="CANCEL",
            custom_bg_color=(0.35, 0.25, 0.7, 1),
            bold=True
        )
        
        confirm_btn = GameButton(
            text="CONFIRM",
            custom_bg_color=(0.85, 0.2, 0.25, 1),
            bold=True
        )
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(confirm_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title="",
            title_size=0,
            separator_height=0,
            content=content,
            size_hint=(0.85, 0.4),
            background=''
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        
        def on_confirm(*args):
            popup.dismiss()
            on_confirm_callback()
            
        confirm_btn.bind(on_press=on_confirm)
        popup.open()

    def exit_to_welcome(self):
        self.stop_slideshow()
        self.clear_widgets()
        self.players = {}
        self.player_names = []
        self.game_history = []
        self.round_number = 1
        self.setup_background()
        self.show_welcome_screen()

    def stop_slideshow(self):
        if hasattr(self, 'slideshow_event'):
            self.slideshow_event.cancel()
            delattr(self, 'slideshow_event')

    def show_welcome_screen(self):
        self.clear_widgets()
        self.stop_slideshow()
        
        self.main_content.padding = 0
        self.current_phase = "WELCOME"
        self.update_music("WELCOME")

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
        self.slideshow = FitImage(
            source=self.slideshow_images[0],
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
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

        # Create mute button in top right of the welcome screen
        self.welcome_mute_btn = GameButton(
            text="SOUND OFF" if self.music_muted else "SOUND ON",
            size_hint=(None, None),
            size=(dp(110), dp(40)),
            pos_hint={'right': 0.96, 'top': 0.96},
            custom_bg_color=(0.15, 0.15, 0.22, 0.9),
            font_size=MOBILE_FONT_XS,
            bold=True
        )
        self.welcome_mute_btn.bind(on_press=self.toggle_mute)
        self.main_layout.add_widget(self.welcome_mute_btn)

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
        self.principles_btn = GameButton(
            text="Read Principles",
            size_hint=(1, 0.45),
            custom_bg_color=(0.35, 0.25, 0.7, 1),
            font_size=MOBILE_FONT_MD,
            bold=True
        )

        # Start Game Button
        self.start_btn = GameButton(
            text="START GAME",
            size_hint=(1, 0.45),
            custom_bg_color=(0.85, 0.2, 0.25, 1),
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
        
    def autofill_player_names(self, instance):
        names = ["Sikandar1", "Shera2", "Mani3", "Billo4", "Raja5", "Chor6", "Angel7", "Kaka8"]
        for input_widget, name in zip(self.player_inputs, names):
            input_widget.text = name

    def start_registration(self, instance=None):
        self.main_content.padding = dp(12)
        self.setup_background("registration")
        self.clear_widgets()
        self.current_phase = "REGISTRATION"

        header = BoxLayout(orientation='vertical', size_hint=(1, 0.15), spacing=dp(5))

        title_box = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(40))
        title = Label(
            text="PLAYER REGISTRATION",
            font_size=MOBILE_FONT_XL,
            bold=True,
            color=(0.9, 0.9, 0.1, 1),
            outline_width=2,
            outline_color=(0, 0, 0, 1),
            size_hint_x=0.7,
            halign='left',
            valign='middle'
        )
        title.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
        
        reg_mute_btn = GameButton(
            text="SOUND OFF" if self.music_muted else "SOUND ON",
            size_hint=(0.3, 0.9),
            pos_hint={'center_y': 0.5},
            custom_bg_color=(0.15, 0.15, 0.22, 0.9),
            font_size=MOBILE_FONT_XS,
            bold=True
        )
        reg_mute_btn.bind(on_press=self.toggle_mute)
        title_box.add_widget(title)
        title_box.add_widget(reg_mute_btn)
        header.add_widget(title_box)

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

            player_input = GameTextInput(
                multiline=False,
                size_hint=(0.7, 1),
                hint_text_color=(0.6, 0.6, 0.7, 1),
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

        actions_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(0.95, None),
            height=dp(50),
            spacing=dp(10),
            pos_hint={'center_x': 0.5}
        )

        back_btn = GameButton(
            text="BACK",
            size_hint=(0.25, 1),
            custom_bg_color=(0.35, 0.25, 0.7, 1),
            font_size=MOBILE_FONT_SM,
            bold=True
        )
        back_btn.bind(on_press=lambda x: self.show_welcome_screen())

        autofill_btn = GameButton(
            text="AUTO-FILL",
            size_hint=(0.35, 1),
            custom_bg_color=(0.88, 0.65, 0.12, 1),
            font_size=MOBILE_FONT_SM,
            bold=True
        )
        autofill_btn.bind(on_press=self.autofill_player_names)

        submit_btn = GameButton(
            text="CONFIRM",
            size_hint=(0.4, 1),
            custom_bg_color=(0.12, 0.64, 0.38, 1),
            font_size=MOBILE_FONT_SM,
            bold=True
        )
        submit_btn.bind(on_press=self.validate_registration)

        actions_layout.add_widget(back_btn)
        actions_layout.add_widget(autofill_btn)
        actions_layout.add_widget(submit_btn)

        self.add_widget(header)
        self.add_widget(scroll)
        self.add_widget(actions_layout)

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
        role_screen.player_name = ""
        role_screen.role_text = f"{player}, your role is: {role_data['role'].upper()}"
        role_screen.role_icon = role_data['role_icon']
        
        descriptions = {
            'Thief': "Work with your partner to target players at night. Stay hidden and deceive the citizens!",
            'Angel': "Select a player to protect every night. You can save targeted players from the thieves!",
            'Citizen': "Discuss with others and vote to catch the thieves during the day. Protect your village!"
        }
        role_screen.role_description = descriptions.get(role_data['role'], "")

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
        print(f"\n{'='*40}")
        print(f"[ROUND {self.round_number}] VOTING PHASE STARTED")
        print(f"  Alive players: {', '.join(self.alive_players)}")
        print(f"{'='*40}")
        self.update_voting_screen()
        
    def update_voting_screen(self):
        if self.current_voter_index >= len(self.alive_players):
            self.process_votes()
            return

        voter = self.alive_players[self.current_voter_index]
        role_data = self.players[voter]

        self.clear_widgets()

        # Header with phase information
        header = self.create_game_header(
            f"ROUND {self.round_number}: VOTING PHASE",
            f"{voter}, vote to eliminate:"
        )

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
        print(f"  [VOTE] {voter}  ->  {target}")
        self.current_voter_index += 1
        self.update_voting_screen()

    def process_votes(self):
        if not self.current_votes:
            print("  [VOTES] No votes cast.")
            self.show_thieves_phase()
            return

        print(f"  [VOTE TALLY] {dict(self.current_votes)}")
        max_votes = max(self.current_votes.values())
        candidates = [p for p, v in self.current_votes.items() if v == max_votes]
        eliminated = random.choice(candidates) if len(candidates) > 1 else candidates[0]

        self.players[eliminated]['alive'] = False
        self.update_alive_players()
        self.eliminated_in_voting = eliminated

        role = self.players[eliminated]['role']
        print(f"  [ELIMINATED BY VOTE] {eliminated} was a {role}")

        # Record voting event in game history
        self.game_history.append({
            'round': self.round_number,
            'phase': 'Voting Phase',
            'event': f"{eliminated} ({role}) was voted out."
        })

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

        print(f"\n[ROUND {self.round_number}] THIEVES' PHASE")
        print(f"  Alive thieves: {', '.join(thieves) if thieves else 'None'}")

        if not thieves:
            self.show_angel_phase()
            return

        self.thieves_target = None
        self.clear_widgets()

        header = self.create_game_header(
            f"ROUND {self.round_number}: THIEVES' PHASE",
            f"Thieves {' & '.join(thieves)}, choose a target to kill!"
        )

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
        self.thieves_target = target
        target_role = self.players[target]['role']
        print(f"  [THIEVES CHOSE] {target} (a {target_role})")
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
        print(f"\n[ROUND {self.round_number}] ANGEL'S PHASE")
        print(f"  Angel is: {angel if angel else 'None (dead)'}")
        print(f"  Thieves' target: {self.thieves_target if self.thieves_target else 'None'}")
        
        if not angel or not self.thieves_target:
            self.show_round_results()
            return
            
        self.angel_choice = None
        self.clear_widgets()
        
        header = self.create_game_header(
            f"ROUND {self.round_number}: ANGEL'S PHASE",
            f"Angel {angel}, choose someone to save:"
        )
        
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
        print(f"  [ANGEL CHOSE] {target} to save  |  Thieves targeted: {self.thieves_target}")
        saved = (target == self.thieves_target)
        print(f"  [RESULT] {'SAVED!' if saved else 'FAILED TO SAVE'}")
        target_role = self.players[self.thieves_target]['role']
        image = None
        message = ""

        if self.angel_choice == self.thieves_target:
            self.eliminated_at_night = None
            if target_role == 'Angel':
                message = "Angel saved themselves!"
                image = 'assets/angel_saved.png'
            else:
                message = "Angel has saved the citizen!"
                image = 'assets/angel_saved.png'
                
            event_text = f"Thieves targeted {self.thieves_target} ({target_role}), but the Angel SAVED them!"
        else:
            self.players[self.thieves_target]['alive'] = False
            self.eliminated_at_night = self.thieves_target
            if target_role == 'Angel':
                message = "Angel failed to save themselves!"
                image = 'assets/angel_died.png'
            else:
                message = "Angel has failed to save the citizen!"
                image = 'assets/citizen_died.png'
                
            event_text = f"Thieves targeted {self.thieves_target} ({target_role}), and the Angel failed to protect them. {self.thieves_target} died."

        # Record event in game history
        self.game_history.append({
            'round': self.round_number,
            'phase': "Thieves' & Angel's Phase",
            'event': event_text
        })

        self.update_alive_players()
        self.show_popup("Angel's Decision", message, self.show_round_results, image)

    def create_status_box(self):
        """Returns a horizontal split showing Alive / Eliminated players as modern glassmorphic name cards."""
        container = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(130), spacing=dp(6))

        def _make_panel(title_text, names, accent, card_bg, card_border_alpha):
            panel = BoxLayout(orientation='vertical', size_hint=(0.5, 1), spacing=dp(4),
                              padding=[dp(5), dp(5), dp(5), dp(5)])
            with panel.canvas.before:
                Color(0.04, 0.05, 0.13, 0.88)
                pbg = RoundedRectangle(pos=panel.pos, size=panel.size, radius=[dp(14)])
                Color(*accent[:3], 0.5)
                pborder = Line(rounded_rectangle=[panel.x, panel.y, panel.width, panel.height, dp(14)], width=1.4)
            def _upd_panel(inst, val, b=pbg, l=pborder):
                b.pos = inst.pos; b.size = inst.size
                l.rounded_rectangle = [inst.x, inst.y, inst.width, inst.height, dp(14)]
            panel.bind(pos=_upd_panel, size=_upd_panel)

            # Section header with count badge
            hdr_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(22), spacing=dp(4))
            hdr_lbl = Label(
                text=title_text,
                font_size='10sp',
                bold=True,
                color=accent,
                size_hint=(1, 1),
                halign='left',
                valign='middle',
                outline_color=(0, 0, 0, 1),
                outline_width=1.0
            )
            hdr_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            count_lbl = Label(
                text=str(len(names)),
                font_size='10sp',
                bold=True,
                color=(0, 0, 0, 1),
                size_hint=(None, None),
                size=(dp(20), dp(20))
            )
            with count_lbl.canvas.before:
                Color(*accent[:3], 1)
                count_bg = RoundedRectangle(pos=count_lbl.pos, size=count_lbl.size, radius=[dp(10)])
            def _upd_count_bg(inst, val, r=count_bg):
                r.pos = inst.pos; r.size = inst.size
            count_lbl.bind(pos=_upd_count_bg, size=_upd_count_bg)

            hdr_row.add_widget(hdr_lbl)
            hdr_row.add_widget(count_lbl)
            panel.add_widget(hdr_row)

            # Scrollable card list
            sv = ScrollView(size_hint=(1, 1), do_scroll_x=False)
            card_col = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(3))
            card_col.bind(minimum_height=card_col.setter('height'))

            display_names = names if names else ['—']
            for name in display_names:
                card = BoxLayout(
                    orientation='horizontal',
                    size_hint=(1, None),
                    height=dp(24),
                    padding=[dp(6), dp(2), dp(6), dp(2)]
                )
                with card.canvas.before:
                    Color(*card_bg)
                    card_r = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(8)])
                    Color(*accent[:3], card_border_alpha)
                    card_l = Line(rounded_rectangle=[card.x, card.y, card.width, card.height, dp(8)], width=1.0)
                def _upd_card(inst, val, r=card_r, l=card_l):
                    r.pos = inst.pos; r.size = inst.size
                    l.rounded_rectangle = [inst.x, inst.y, inst.width, inst.height, dp(8)]
                card.bind(pos=_upd_card, size=_upd_card)

                name_lbl = Label(
                    text=name,
                    font_size='10sp',
                    bold=True,
                    color=(0.95, 0.95, 0.95, 1),
                    size_hint=(1, 1),
                    halign='center',
                    valign='middle'
                )
                name_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
                card.add_widget(name_lbl)
                card_col.add_widget(card)

            sv.add_widget(card_col)
            panel.add_widget(sv)
            return panel

        alive_panel = _make_panel(
            "Alive", list(self.alive_players),
            accent=(0.25, 0.95, 0.45, 1),
            card_bg=(0.04, 0.22, 0.10, 0.9),
            card_border_alpha=0.35
        )
        elim_panel = _make_panel(
            "Eliminated", list(self.eliminated_players) if self.eliminated_players else [],
            accent=(0.95, 0.25, 0.25, 1),
            card_bg=(0.22, 0.04, 0.04, 0.9),
            card_border_alpha=0.35
        )

        container.add_widget(alive_panel)
        container.add_widget(elim_panel)
        return container

    def show_round_results(self):
        self.setup_background("results")
        self.clear_widgets()
        self.current_phase = "RESULTS"
        
        header = self.create_game_header(f"ROUND {self.round_number} RESULTS")
        
        results_box = BoxLayout(orientation='vertical', size_hint=(1, 0.56))
        
        active_elims = []
        if self.eliminated_in_voting:
            active_elims.append(('Voted Out', self.eliminated_in_voting))
        if self.eliminated_at_night:
            active_elims.append(('Killed By Thieves', self.eliminated_at_night))
            
        if len(active_elims) == 2:
            card_size_hint = (0.45, 1)
        else:
            card_size_hint = (0.6, 1)
            
        cards_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(0.95, 0.9),
            spacing=dp(15),
            pos_hint={'center_x': 0.5}
        )
        
        if len(active_elims) == 1:
            cards_layout.add_widget(Widget(size_hint_x=0.2))
            
        for label_text, player_name in active_elims:
            card_box = BoxLayout(orientation='vertical', spacing=dp(5), size_hint=card_size_hint)
            
            label = Label(
                text=label_text.upper(),
                font_size=MOBILE_FONT_SM,
                bold=True,
                color=(0.85, 0.2, 0.25, 1),
                outline_width=1.5,
                outline_color=(0, 0, 0, 1),
                size_hint_y=None,
                height=dp(25)
            )
            
            eliminated_card = PlayerCard()
            eliminated_card.player_name = player_name
            eliminated_card.role = self.players[player_name]['role']
            eliminated_card.role_icon = f'assets/{self.players[player_name]["role"].lower()}_icon.png'
            eliminated_card.alive = False
            eliminated_card.show_role = True
            eliminated_card.size_hint = (1, 0.8)
            
            card_box.add_widget(label)
            card_box.add_widget(eliminated_card)
            cards_layout.add_widget(card_box)
            
        if len(active_elims) == 1:
            cards_layout.add_widget(Widget(size_hint_x=0.2))
            
        if not active_elims:
            no_deaths = Label(
                text="PEACEFUL NIGHT!\nNo one was eliminated this round.",
                font_size=MOBILE_FONT_MD,
                bold=True,
                color=(0.12, 0.64, 0.38, 1),
                outline_width=1.5,
                outline_color=(0, 0, 0, 1),
                halign='center',
                valign='middle'
            )
            no_deaths.bind(width=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            cards_layout.add_widget(no_deaths)
            
        results_box.add_widget(cards_layout)
        
        status_box = self.create_status_box()
        
        continue_btn = GameButton(
            text="CONTINUE TO NEXT ROUND",
            size_hint=(0.85, None),
            height=dp(50),
            pos_hint={'center_x': 0.5},
            custom_bg_color=(0.12, 0.64, 0.38, 1),
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
        
        header_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=dp(10))
        header = Label(
            text="GAME OVER",
            font_size=MOBILE_FONT_XL,
            color=(0.9, 0.2, 0.2, 1),
            outline_width=3,
            outline_color=(0, 0, 0, 1),
            size_hint_x=0.8,
            halign='left',
            valign='middle'
        )
        header.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
        
        go_mute_btn = GameButton(
            text="🔇" if self.music_muted else "🔊",
            size_hint=(0.2, 0.8),
            pos_hint={'center_y': 0.5},
            custom_bg_color=(0.15, 0.15, 0.22, 0.9),
            font_size=MOBILE_FONT_SM,
            bold=True
        )
        go_mute_btn.bind(on_press=self.toggle_mute)
        
        header_box.add_widget(header)
        header_box.add_widget(go_mute_btn)
        main_layout.add_widget(header_box)
        
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
        
        restart_btn = GameButton(
            text="PLAY AGAIN",
            size_hint=(0.8, None),
            height=dp(52),
            pos_hint={'center_x': 0.5},
            custom_bg_color=(0.15, 0.35, 0.75, 1),
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
            
        muted = getattr(self, 'music_muted', False)
        self.__init__()
        self.music_muted = muted
        if self.music_muted:
            self.stop_music()

    def show_popup(self, title, message, callback, image=None):
        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(15))

        with content.canvas.before:
            Color(0.06, 0.06, 0.14, 0.97)
            popup_bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[16,])
            Color(0.88, 0.65, 0.12, 0.6)
            popup_border = Line(rounded_rectangle=[content.x, content.y, content.width, content.height, 16], width=1.8)

        def update_popup_bg(instance, value):
            popup_bg.pos = instance.pos
            popup_bg.size = instance.size
            popup_border.rounded_rectangle = [instance.x, instance.y, instance.width, instance.height, 16]

        content.bind(pos=update_popup_bg, size=update_popup_bg)

        clean_title = title.split(']')[-1] if ']' in title else title
        title_lbl = Label(
            text=clean_title.upper(),
            font_size=MOBILE_FONT_LG,
            bold=True,
            color=(0.9, 0.9, 0.1, 1),
            outline_width=1.5,
            outline_color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(32),
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

        btn = GameButton(
            text="OK",
            size_hint=(0.55, None),
            height=dp(44),
            pos_hint={'center_x': 0.5},
            custom_bg_color=(0.12, 0.64, 0.38, 1),
            font_size=MOBILE_FONT_MD,
            bold=True
        )

        popup = Popup(
            title="",
            title_size=0,
            separator_height=0,
            content=content,
            size_hint=(0.85, 0.55),
            background='',
            background_color=(0, 0, 0, 0)
        )

        btn.bind(on_press=popup.dismiss)
        btn.bind(on_press=lambda x: callback())
        content.add_widget(btn)
        popup.open()

    def show_error_popup(self, message):
        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(15))

        with content.canvas.before:
            Color(0.10, 0.04, 0.04, 0.97)
            popup_bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[16,])
            Color(0.9, 0.2, 0.2, 0.7)
            popup_border = Line(rounded_rectangle=[content.x, content.y, content.width, content.height, 16], width=1.8)

        def update_popup_bg(instance, value):
            popup_bg.pos = instance.pos
            popup_bg.size = instance.size
            popup_border.rounded_rectangle = [instance.x, instance.y, instance.width, instance.height, 16]

        content.bind(pos=update_popup_bg, size=update_popup_bg)

        title_lbl = Label(
            text="ERROR",
            font_size=MOBILE_FONT_LG,
            bold=True,
            color=(0.95, 0.3, 0.3, 1),
            outline_width=1.5,
            outline_color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(32),
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

        btn = GameButton(
            text="OK",
            size_hint=(0.65, None),
            height=dp(44),
            pos_hint={'center_x': 0.5},
            custom_bg_color=(0.75, 0.15, 0.15, 1),
            font_size=MOBILE_FONT_MD,
            bold=True
        )

        popup = Popup(
            title="",
            title_size=0,
            separator_height=0,
            content=content,
            size_hint=(0.8, 0.45),
            background='',
            background_color=(0, 0, 0, 0)
        )

        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

class DakatiApp(App):
    def build(self):
        self.title = 'Dakati Game'
        # Standard mobile size for testing on desktop
        if platform not in ('android', 'ios'):
            Window.size = (490, 860)
        return DakatiGame()

if __name__ == '__main__':
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    DakatiApp().run()
