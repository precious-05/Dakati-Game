import socket
import threading
import json
import random
from collections import defaultdict
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import (StringProperty, ListProperty, 
                           NumericProperty, BooleanProperty,
                           ObjectProperty)
from kivy.graphics import Color, Rectangle

# Network Configuration
HOST = '0.0.0.0'
PORT = 55555
BUFFER_SIZE = 4096

class PlayerButton(Button):
    player_name = StringProperty("")

class DakatiServer:
    def __init__(self, game):
        self.game = game
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(8)
        self.clients = {}
        self.running = True
        threading.Thread(target=self.accept_connections, daemon=True).start()
    
    def accept_connections(self):
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except:
                break
    
    def handle_client(self, client_socket):
        while self.running:
            try:
                data = client_socket.recv(BUFFER_SIZE).decode('utf-8')
                if not data:
                    break
                message = json.loads(data)
                self.process_message(message, client_socket)
            except:
                break
        
        # Clean up disconnected client
        for name, info in list(self.clients.items()):
            if info['socket'] == client_socket:
                del self.clients[name]
                Clock.schedule_once(lambda dt: self.game.update_player_list())
                break
        client_socket.close()
    
    def process_message(self, message, client_socket):
        msg_type = message.get('type')
        
        if msg_type == 'register':
            self.handle_registration(message, client_socket)
        elif msg_type == 'ready':
            self.handle_ready(message)
        elif msg_type == 'vote':
            self.game.process_vote(message['voter'], message['target'])
        elif msg_type == 'thieves_choice':
            self.game.process_thieves_choice(message['target'])
        elif msg_type == 'angel_choice':
            self.game.process_angel_choice(message['target'])
    
    def handle_registration(self, message, client_socket):
        name = message['name']
        if name in self.clients:
            response = {'type': 'registration_failed', 'reason': 'Name already taken'}
            client_socket.send(json.dumps(response).encode('utf-8'))
        else:
            self.clients[name] = {'socket': client_socket, 'ready': False}
            response = {'type': 'registration_success', 'name': name}
            client_socket.send(json.dumps(response).encode('utf-8'))
            self.broadcast_player_list()
    
    def handle_ready(self, message):
        name = message['name']
        if name in self.clients:
            self.clients[name]['ready'] = True
            self.broadcast_player_list()
            if all(info['ready'] for info in self.clients.values()) and len(self.clients) == 8:
                self.start_game()
    
    def broadcast_player_list(self):
        players = [{
            'name': name,
            'ready': info['ready']
        } for name, info in self.clients.items()]
        
        self.broadcast({
            'type': 'player_list_update',
            'players': players
        })
    
    def start_game(self):
        names = list(self.clients.keys())
        roles = ['Thief']*2 + ['Angel']*1 + ['Citizen']*5
        random.shuffle(roles)
        roles_assignment = {name: role for name, role in zip(names, roles)}
        
        # Identify thieves partners
        thieves = [name for name, role in roles_assignment.items() if role == 'Thief']
        for thief in thieves:
            roles_assignment[thief + '_partner'] = next(t for t in thieves if t != thief)
        
        # Send role information
        for name, info in self.clients.items():
            role_info = {
                'type': 'role_assignment',
                'role': roles_assignment[name],
                'name': name
            }
            if roles_assignment[name] == 'Thief':
                role_info['partner'] = roles_assignment[name + '_partner']
            info['socket'].send(json.dumps(role_info).encode('utf-8'))
        
        # Initialize game state
        Clock.schedule_once(lambda dt: self.game.start_game(roles_assignment))
    
    def broadcast(self, message):
        for info in self.clients.values():
            try:
                info['socket'].send(json.dumps(message).encode('utf-8'))
            except:
                continue
    
    def send_to(self, player_name, message):
        if player_name in self.clients:
            try:
                self.clients[player_name]['socket'].send(json.dumps(message).encode('utf-8'))
            except:
                pass
    
    def stop(self):
        self.running = False
        try:
            self.server_socket.close()
        except:
            pass

class DakatiClient:
    def __init__(self, game, server_ip):
        self.game = game
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server_ip, PORT))
        self.running = True
        self.name = ""
        threading.Thread(target=self.receive_messages, daemon=True).start()
    
    def receive_messages(self):
        while self.running:
            try:
                data = self.socket.recv(BUFFER_SIZE).decode('utf-8')
                if not data:
                    break
                message = json.loads(data)
                Clock.schedule_once(lambda dt: self.process_message(message))
            except:
                break
        self.socket.close()
    
    def process_message(self, message):
        msg_type = message.get('type')
        handler = getattr(self.game, f'handle_{msg_type}', None)
        if handler:
            handler(message)
    
    def send(self, message):
        try:
            self.socket.send(json.dumps(message).encode('utf-8'))
        except:
            pass
    
    def stop(self):
        self.running = False
        try:
            self.socket.close()
        except:
            pass

class DakatiGame(BoxLayout):
    current_phase = StringProperty("lobby")
    round_number = NumericProperty(0)
    alive_players = ListProperty([])
    eliminated_players = ListProperty([])
    is_host = BooleanProperty(False)
    player_name = StringProperty("")
    connected_players = ListProperty([])
    current_voter = StringProperty("")
    
    server = ObjectProperty(None, allownone=True)
    client = ObjectProperty(None, allownone=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 15
        self.padding = 20
        self.players = {}
        self.my_role = ""
        self.my_partner = ""
        self.current_votes = defaultdict(int)
        self.thieves_target = None
        self.angel_choice = None
        self.show_welcome_screen()
    
    # Network Operations
    def host_game(self):
        self.is_host = True
        self.server = DakatiServer(self)
        self.show_host_waiting_screen()
    
    def join_game(self, ip_address):
        self.client = DakatiClient(self, ip_address)
        self.show_player_registration()
    
    def register_player(self, name):
        if self.client:
            self.player_name = name
            self.client.send({'type': 'register', 'name': name})
    
    def ready_player(self):
        if self.client:
            self.client.send({'type': 'ready', 'name': self.player_name})
    
    def on_stop(self):
        if self.server:
            self.server.stop()
        if self.client:
            self.client.stop()
    
    # Game Logic
    def start_game(self, roles_assignment):
        self.players = {name: {'role': role, 'alive': True} 
                       for name, role in roles_assignment.items() 
                       if not name.endswith('_partner')}
        
        thieves = [name for name, data in self.players.items() if data['role'] == 'Thief']
        for thief in thieves:
            self.players[thief]['partner'] = roles_assignment[thief + '_partner']
        
        self.alive_players = list(self.players.keys())
        self.eliminated_players = []
        self.round_number = 1
        
        if self.server:
            self.server.broadcast({
                'type': 'game_start',
                'roles': roles_assignment
            })
        
        self.start_voting_phase()
    
    def start_voting_phase(self):
        self.current_phase = "voting"
        self.current_votes = defaultdict(int)
        
        if self.is_host:
            self.current_voter = random.choice(self.alive_players)
            if self.server:
                self.server.broadcast({
                    'type': 'voting_start',
                    'alive_players': self.alive_players,
                    'voter': self.current_voter
                })
        
        if self.current_voter == self.player_name:
            self.show_voting_screen()
        else:
            self.show_waiting_screen(f"Waiting for {self.current_voter} to vote...")
    
    def process_vote(self, voter, target):
        self.current_votes[target] += 1
        
        if len([p for p in self.alive_players if p != voter]) == sum(self.current_votes.values()):
            max_votes = max(self.current_votes.values())
            candidates = [p for p, v in self.current_votes.items() if v == max_votes]
            eliminated = random.choice(candidates) if len(candidates) > 1 else candidates[0]
            
            self.players[eliminated]['alive'] = False
            self.alive_players.remove(eliminated)
            self.eliminated_players.append(eliminated)
            
            if self.server:
                self.server.broadcast({
                    'type': 'vote_result',
                    'eliminated': eliminated,
                    'role': self.players[eliminated]['role']
                })
            
            self.start_thieves_phase()
    
    def start_thieves_phase(self):
        self.current_phase = "thieves"
        thieves = [name for name, data in self.players.items() 
                  if data['alive'] and data['role'] == 'Thief']
        
        if not thieves:
            self.start_angel_phase()
            return
        
        if self.server:
            self.server.broadcast({
                'type': 'thieves_turn',
                'alive_players': self.alive_players
            })
        
        if self.my_role == 'Thief' and self.player_name in self.alive_players:
            self.show_thieves_screen()
        else:
            self.show_waiting_screen("Thieves are choosing a target...")
    
    def process_thieves_choice(self, target):
        self.thieves_target = target
        
        if self.server:
            self.server.broadcast({
                'type': 'angel_turn',
                'alive_players': self.alive_players
            })
        
        self.start_angel_phase()
    
    def start_angel_phase(self):
        self.current_phase = "angel"
        angel = next((name for name, data in self.players.items() 
                     if data['alive'] and data['role'] == 'Angel'), None)
        
        if not angel or not hasattr(self, 'thieves_target'):
            self.show_round_results()
            return
        
        if self.server:
            self.server.broadcast({
                'type': 'angel_turn',
                'alive_players': self.alive_players
            })
        
        if self.my_role == 'Angel' and self.player_name in self.alive_players:
            self.show_angel_screen()
        else:
            self.show_waiting_screen("Angel is choosing someone to save...")
    
    def process_angel_choice(self, target):
        self.angel_choice = target
        saved = (target == self.thieves_target)
        
        if not saved and self.players[self.thieves_target]['role'] in ['Citizen', 'Angel']:
            self.players[self.thieves_target]['alive'] = False
            self.alive_players.remove(self.thieves_target)
            self.eliminated_players.append(self.thieves_target)
        
        if self.server:
            self.server.broadcast({
                'type': 'night_result',
                'target': self.thieves_target,
                'saved': saved
            })
        
        self.show_round_results()
    
    def check_win_conditions(self):
        alive_thieves = sum(1 for data in self.players.values() 
                          if data['alive'] and data['role'] == 'Thief')
        alive_citizens = sum(1 for data in self.players.values() 
                           if data['alive'] and data['role'] in ['Citizen', 'Angel'])
        
        if alive_thieves == 0:
            winner = "CITIZENS WIN! All thieves have been eliminated!"
        elif alive_thieves >= alive_citizens:
            winner = "THIEVES WIN! They outnumber the citizens!"
        else:
            self.start_voting_phase()
            return
        
        if self.server:
            self.server.broadcast({
                'type': 'game_over',
                'winner': winner,
                'roles': {name: data['role'] for name, data in self.players.items()}
            })
        
        self.show_game_over(winner)
    
    # Message Handlers
    def handle_registration_success(self, message):
        self.player_name = message['name']
        self.show_waiting_room()
    
    def handle_registration_failed(self, message):
        self.show_error_popup("Registration Failed", message['reason'])
    
    def handle_player_list_update(self, message):
        self.connected_players = message['players']
    
    def handle_role_assignment(self, message):
        self.my_role = message['role']
        if self.my_role == 'Thief':
            self.my_partner = message['partner']
        self.show_role_screen()
    
    def handle_game_start(self, message):
        self.start_game(message['roles'])
    
    def handle_voting_start(self, message):
        self.alive_players = message['alive_players']
        self.current_voter = message['voter']
        
        if self.current_voter == self.player_name:
            self.show_voting_screen()
        else:
            self.show_waiting_screen(f"Waiting for {self.current_voter} to vote...")
    
    def handle_thieves_turn(self, message):
        self.alive_players = message['alive_players']
        
        if self.my_role == 'Thief' and self.player_name in self.alive_players:
            self.show_thieves_screen()
        else:
            self.show_waiting_screen("Thieves are choosing a target...")
    
    def handle_angel_turn(self, message):
        self.alive_players = message['alive_players']
        
        if self.my_role == 'Angel' and self.player_name in self.alive_players:
            self.show_angel_screen()
        else:
            self.show_waiting_screen("Angel is choosing someone to save...")
    
    def handle_vote_result(self, message):
        self.players[message['eliminated']]['alive'] = False
        self.alive_players.remove(message['eliminated'])
        self.eliminated_players.append(message['eliminated'])
        
        role = message['role']
        if role == 'Citizen':
            result = "Innocent citizen eliminated!"
        elif role == 'Thief':
            result = "A thief was eliminated!"
        else:
            result = "The angel was eliminated!"
        
        self.show_popup(
            "Voting Result",
            f"{message['eliminated']} was eliminated!\n{result}",
            self.start_thieves_phase
        )
    
    def handle_night_result(self, message):
        if not message['saved'] and message['target'] in self.alive_players:
            self.players[message['target']]['alive'] = False
            self.alive_players.remove(message['target'])
            self.eliminated_players.append(message['target'])
        
        result = "The angel saved the target!" if message['saved'] else \
                f"{message['target']} was eliminated during the night!"
        
        self.show_popup(
            "Night Phase Result",
            result,
            self.show_round_results
        )
    
    def handle_game_over(self, message):
        self.show_game_over(message['winner'])
    
    # UI Screens
    def show_welcome_screen(self):
        self.clear_widgets()
        
        title = Label(text="[b]DAKATI GAME[/b]", markup=True, font_size=36)
        subtitle = Label(text="A Social Deduction Game for 8 Players", font_size=20)
        
        host_btn = Button(text="Host Game", size_hint=(None, None), size=(250, 60))
        host_btn.bind(on_press=lambda x: self.host_game())
        
        join_btn = Button(text="Join Game", size_hint=(None, None), size=(250, 60))
        join_btn.bind(on_press=lambda x: self.show_join_screen())
        
        layout = BoxLayout(orientation='vertical', spacing=20)
        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(host_btn)
        layout.add_widget(join_btn)
        
        self.add_widget(layout)
    
    def show_join_screen(self):
        self.clear_widgets()
        
        ip_input = TextInput(hint_text="Enter Host IP Address", multiline=False, font_size=20,
                           size_hint=(0.8, None), height=50)
        
        join_btn = Button(text="Connect", size_hint=(None, None), size=(200, 60))
        join_btn.bind(on_press=lambda x: self.join_game(ip_input.text.strip()))
        
        back_btn = Button(text="Back", size_hint=(None, None), size=(200, 60))
        back_btn.bind(on_press=lambda x: self.show_welcome_screen())
        
        layout = BoxLayout(orientation='vertical', spacing=20)
        layout.add_widget(Label(text="Enter Host IP:", font_size=24))
        layout.add_widget(ip_input)
        layout.add_widget(join_btn)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def show_player_registration(self):
        self.clear_widgets()
        
        name_input = TextInput(hint_text="Enter Your Name", multiline=False, font_size=20,
                             size_hint=(0.8, None), height=50)
        
        register_btn = Button(text="Register", size_hint=(None, None), size=(200, 60))
        register_btn.bind(on_press=lambda x: self.register_player(name_input.text.strip()))
        
        back_btn = Button(text="Back", size_hint=(None, None), size=(200, 60))
        back_btn.bind(on_press=lambda x: self.show_welcome_screen())
        
        layout = BoxLayout(orientation='vertical', spacing=20)
        layout.add_widget(Label(text="Register Player:", font_size=24))
        layout.add_widget(name_input)
        layout.add_widget(register_btn)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def show_waiting_room(self):
        self.clear_widgets()
        
        title = Label(text="Waiting Room", font_size=24)
        self.player_list_label = Label(text="", font_size=18)
        
        ready_btn = Button(text="Ready", size_hint=(None, None), size=(200, 60),
                          disabled=len(self.connected_players) < 8)
        ready_btn.bind(on_press=lambda x: self.ready_player())
        
        layout = BoxLayout(orientation='vertical', spacing=20)
        layout.add_widget(title)
        layout.add_widget(self.player_list_label)
        layout.add_widget(ready_btn)
        
        self.add_widget(layout)
        self.update_player_list_display()
    
    def update_player_list_display(self):
        if hasattr(self, 'player_list_label'):
            players_text = "Connected Players:\n"
            for player in self.connected_players:
                status = " (Ready)" if player.get('ready', False) else ""
                players_text += f"{player['name']}{status}\n"
            self.player_list_label.text = players_text
    
    def show_host_waiting_screen(self):
        self.clear_widgets()
        
        title = Label(text="Host Waiting Room", font_size=24)
        self.player_list_label = Label(text="", font_size=18)
        
        layout = BoxLayout(orientation='vertical', spacing=20)
        layout.add_widget(title)
        layout.add_widget(self.player_list_label)
        
        self.add_widget(layout)
        self.update_player_list_display()
    
    def show_role_screen(self):
        self.clear_widgets()
        
        title = Label(text="Your Role", font_size=28)
        
        role_text = f"[b]{self.my_role.upper()}[/b]"
        role_color = (0.2, 0.8, 0.4, 1) if self.my_role == 'Citizen' else \
                    (0.8, 0.2, 0.2, 1) if self.my_role == 'Thief' else \
                    (0.4, 0.4, 0.9, 1)
        
        role_label = Label(text=role_text, markup=True, font_size=36)
        role_label.color = role_color
        
        info_label = Label(text="Keep this secret!", font_size=20)
        
        if self.my_role == 'Thief':
            partner_label = Label(text=f"Your partner: {self.my_partner}", font_size=24)
        else:
            partner_label = Label(text="", size_hint_y=None, height=0)
        
        continue_btn = Button(text="Continue", size_hint=(None, None), size=(200, 60))
        continue_btn.bind(on_press=lambda x: self.show_waiting_screen("Waiting for game to start..."))
        
        layout = BoxLayout(orientation='vertical', spacing=20)
        layout.add_widget(title)
        layout.add_widget(role_label)
        layout.add_widget(info_label)
        layout.add_widget(partner_label)
        layout.add_widget(continue_btn)
        
        self.add_widget(layout)
    
    def show_voting_screen(self):
        self.clear_widgets()
        
        title = Label(text=f"Round {self.round_number}: Voting Phase", font_size=24)
        instruction = Label(text="Choose a player to eliminate:", font_size=20)
        
        options = [p for p in self.alive_players if p != self.player_name]
        if self.my_role == 'Thief':
            options = [p for p in options if p != self.my_partner]
        
        grid = GridLayout(cols=2, spacing=15, padding=20, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for player in options:
            btn = PlayerButton(text=player, size_hint_y=None, height=60)
            btn.player_name = player
            btn.bind(on_press=lambda x: self.submit_vote(x.player_name))
            grid.add_widget(btn)
        
        scroll = ScrollView(size_hint=(1, 0.6))
        scroll.add_widget(grid)
        
        status = Label(
            text=f"Alive: {', '.join(self.alive_players)}\nEliminated: {', '.join(self.eliminated_players) if self.eliminated_players else 'None'}",
            font_size=16,
            halign='left',
            valign='top'
        )
        
        layout = BoxLayout(orientation='vertical', spacing=15)
        layout.add_widget(title)
        layout.add_widget(instruction)
        layout.add_widget(scroll)
        layout.add_widget(status)
        
        self.add_widget(layout)
    
    def submit_vote(self, target):
        if self.client:
            self.client.send({
                'type': 'vote',
                'voter': self.player_name,
                'target': target
            })
        elif self.server:
            self.process_vote(self.player_name, target)
        
        self.show_waiting_screen("Waiting for other players to vote...")
    
    def show_thieves_screen(self):
        self.clear_widgets()
        
        title = Label(text="Thieves' Phase", font_size=28)
        instruction = Label(text="Choose a target to eliminate:", font_size=20)
        
        targets = [p for p in self.alive_players if p != self.player_name and p != self.my_partner]
        
        grid = GridLayout(cols=2, spacing=15, padding=20, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for player in targets:
            btn = PlayerButton(text=player, size_hint_y=None, height=60)
            btn.player_name = player
            btn.bind(on_press=lambda x: self.submit_thieves_choice(x.player_name))
            grid.add_widget(btn)
        
        scroll = ScrollView(size_hint=(1, 0.6))
        scroll.add_widget(grid)
        
        layout = BoxLayout(orientation='vertical', spacing=15)
        layout.add_widget(title)
        layout.add_widget(instruction)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def submit_thieves_choice(self, target):
        if self.client:
            self.client.send({
                'type': 'thieves_choice',
                'target': target
            })
        elif self.server:
            self.process_thieves_choice(target)
        
        self.show_waiting_screen("Waiting for angel's decision...")
    
    def show_angel_screen(self):
        self.clear_widgets()
        
        title = Label(text="Angel's Phase", font_size=28)
        instruction = Label(text="Choose a player to save:", font_size=20)
        
        targets = self.alive_players
        
        grid = GridLayout(cols=2, spacing=15, padding=20, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        for player in targets:
            btn = PlayerButton(text=player, size_hint_y=None, height=60)
            btn.player_name = player
            btn.bind(on_press=lambda x: self.submit_angel_choice(x.player_name))
            grid.add_widget(btn)
        
        scroll = ScrollView(size_hint=(1, 0.6))
        scroll.add_widget(grid)
        
        layout = BoxLayout(orientation='vertical', spacing=15)
        layout.add_widget(title)
        layout.add_widget(instruction)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def submit_angel_choice(self, target):
        if self.client:
            self.client.send({
                'type': 'angel_choice',
                'target': target
            })
        elif self.server:
            self.process_angel_choice(target)
        
        self.show_waiting_screen("Waiting for night results...")
    
    def show_round_results(self):
        self.clear_widgets()
        
        title = Label(text=f"Round {self.round_number} Results", font_size=28)
        
        alive_label = Label(
            text=f"Alive Players: {', '.join(self.alive_players)}",
            font_size=20,
            color=(0.2, 0.8, 0.2, 1)
        )
        
        eliminated_label = Label(
            text=f"Eliminated Players: {', '.join(self.eliminated_players) if self.eliminated_players else 'None'}",
            font_size=20,
            color=(0.8, 0.2, 0.2, 1)
        )
        
        continue_btn = Button(text="Continue to Next Round", size_hint=(None, None), size=(300, 60))
        continue_btn.bind(on_press=lambda x: self.check_win_conditions())
        
        layout = BoxLayout(orientation='vertical', spacing=15)
        layout.add_widget(title)
        layout.add_widget(alive_label)
        layout.add_widget(eliminated_label)
        layout.add_widget(continue_btn)
        
        self.add_widget(layout)
    
    def show_game_over(self, winner):
        self.clear_widgets()
        
        title = Label(text="Game Over", font_size=36)
        result_label = Label(text=winner, font_size=24, color=(0.9, 0.9, 0.1, 1))
        
        roles_text = "Final Roles:\n"
        for name, data in self.players.items():
            status = "ALIVE" if data['alive'] else "ELIMINATED"
            role = data['role'].upper()
            roles_text += f"{name}: {role} ({status})\n"
        
        roles_label = Label(text=roles_text, font_size=18, halign='left')
        
        restart_btn = Button(text="Return to Main Menu", size_hint=(None, None), size=(250, 60))
        restart_btn.bind(on_press=lambda x: self.show_welcome_screen())
        
        scroll = ScrollView(size_hint=(1, 0.6))
        scroll.add_widget(roles_label)
        
        layout = BoxLayout(orientation='vertical', spacing=15)
        layout.add_widget(title)
        layout.add_widget(result_label)
        layout.add_widget(scroll)
        layout.add_widget(restart_btn)
        
        self.add_widget(layout)
    
    def show_waiting_screen(self, message):
        self.clear_widgets()
        
        label = Label(text=message, font_size=24)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(label)
        
        self.add_widget(layout)
    
    def show_popup(self, title, message, callback=None):
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        content.add_widget(Label(text=message, font_size=18))
        
        btn = Button(text="OK", size_hint=(1, None), height=50)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.5))
        
        if callback:
            btn.bind(on_press=lambda x: (popup.dismiss(), callback()))
        else:
            btn.bind(on_press=popup.dismiss)
        
        content.add_widget(btn)
        popup.open()
    
    def show_error_popup(self, title, message):
        self.show_popup(title, message)

class DakatiApp(App):
    def build(self):
        Window.size = (800, 600)
        self.game = DakatiGame()
        return self.game
    
    def on_stop(self):
        self.game.on_stop()

if __name__ == '__main__':
    DakatiApp().run()