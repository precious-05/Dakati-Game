import pygame
import random
import sys
from collections import defaultdict

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dakati Game - Social Deduction")

# Colors
DARK_BLUE = (20, 20, 38)
LIGHT_BLUE = (40, 40, 90)
GREEN = (50, 150, 50)
RED = (200, 50, 50)
YELLOW = (230, 230, 30)
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
CITIZEN_COLOR = (50, 200, 100)
THIEF_COLOR = (200, 50, 50)
ANGEL_COLOR = (100, 100, 230)

# Fonts
title_font = pygame.font.SysFont("Arial", 48, bold=True)
header_font = pygame.font.SysFont("Arial", 36)
button_font = pygame.font.SysFont("Arial", 24)
text_font = pygame.font.SysFont("Arial", 20)
small_font = pygame.font.SysFont("Arial", 16)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        text_surf = button_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class InputBox:
    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = LIGHT_BLUE
        self.text = text
        self.txt_surface = text_font.render(text, True, WHITE)
        self.active = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = DARK_GRAY if self.active else LIGHT_BLUE
        
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                
                self.txt_surface = text_font.render(self.text, True, WHITE)
        return False
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        surface.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + 10))
        
        # Draw label if needed
        if not self.text and not self.active:
            placeholder = text_font.render("Enter name...", True, GRAY)
            surface.blit(placeholder, (self.rect.x + 10, self.rect.y + 10))

class DakatiGame:
    def __init__(self):
        self.state = "WELCOME"
        self.players = {}
        self.player_names = []
        self.current_votes = defaultdict(int)
        self.thieves_target = None
        self.angel_choice = None
        self.current_player_index = 0
        self.current_voter_index = 0
        self.round_number = 1
        self.alive_players = []
        self.eliminated_players = []
        self.input_boxes = []
        self.buttons = []
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Initialize input boxes for player registration
        for i in range(8):
            y_pos = 150 + i * 60
            self.input_boxes.append(InputBox(250, y_pos, 400, 40))
            
        self.create_welcome_screen()
        
    def create_welcome_screen(self):
        self.buttons = [
            Button(SCREEN_WIDTH//2 - 125, SCREEN_HEIGHT//2 + 50, 250, 60, 
                  "START GAME", GREEN, (50, 200, 50))
        ]
        
    def create_registration_screen(self):
        self.buttons = [
            Button(SCREEN_WIDTH//2 - 125, SCREEN_HEIGHT - 80, 250, 60, 
                  "CONFIRM PLAYERS", LIGHT_BLUE, (100, 100, 200))
        ]
        
    def create_role_reveal_screen(self):
        self.buttons = [
            Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 50, 
                  "CONTINUE", LIGHT_BLUE, (100, 100, 200))
        ]
        
    def create_voting_screen(self):
        self.buttons = []  # Player buttons will be created dynamically
        
    def create_thieves_screen(self):
        self.buttons = []  # Player buttons will be created dynamically
        
    def create_angel_screen(self):
        self.buttons = []  # Player buttons will be created dynamically
        
    def create_results_screen(self):
        self.buttons = [
            Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT - 80, 300, 60, 
                  "CONTINUE TO NEXT ROUND", GREEN, (50, 200, 50))
        ]
        
    def create_final_results_screen(self):
        self.buttons = [
            Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 80, 200, 60, 
                  "PLAY AGAIN", LIGHT_BLUE, (100, 100, 200))
        ]
        
    def assign_roles(self):
        roles = ['Thief']*2 + ['Angel']*1 + ['Citizen']*5
        random.shuffle(roles)
        self.players = {
            name: {'role': role, 'alive': True}
            for name, role in zip(self.player_names, roles)
        }
        
        # Identify thieves partners
        thieves = [name for name, data in self.players.items() if data['role'] == 'Thief']
        for thief in thieves:
            self.players[thief]['partner'] = next(t for t in thieves if t != thief)
            
        self.state = "ROLE_REVEAL"
        self.current_player_index = 0
        self.create_role_reveal_screen()
        
    def update_alive_players(self):
        self.alive_players = [name for name, data in self.players.items() if data['alive']]
        self.eliminated_players = [name for name, data in self.players.items() if not data['alive']]
        
    def process_votes(self):
        if not self.current_votes:
            self.state = "THIEVES"
            self.create_thieves_screen()
            return
            
        max_votes = max(self.current_votes.values())
        candidates = [p for p, v in self.current_votes.items() if v == max_votes]
        eliminated = random.choice(candidates) if len(candidates) > 1 else candidates[0]
        
        self.players[eliminated]['alive'] = False
        self.eliminated_players.append(eliminated)
        
        # Show elimination result
        role = self.players[eliminated]['role']
        if role == 'Citizen':
            message = "Innocent citizen eliminated!"
        elif role == 'Thief':
            message = "A thief was eliminated!"
        else:
            message = "The angel was eliminated!"
            
        self.show_popup(
            "Voting Result",
            f"{eliminated} was eliminated!\n{message}",
            lambda: setattr(self, 'state', 'THIEVES') or self.create_thieves_screen()
        )
        
    def check_win_conditions(self):
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
            self.state = "VOTING"
            self.current_voter_index = 0
            self.current_votes = defaultdict(int)
            self.create_voting_screen()
            
    def show_final_results(self, message):
        self.state = "GAME_OVER"
        self.final_message = message
        self.create_final_results_screen()
        
    def show_popup(self, title, message, callback):
        self.popup = {
            'title': title,
            'message': message,
            'callback': callback,
            'active': True
        }
        
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if self.state == "REGISTRATION":
                for box in self.input_boxes:
                    if box.handle_event(event):
                        break
                        
            if hasattr(self, 'popup') and self.popup['active']:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.popup['active'] = False
                    self.popup['callback']()
                continue
                
            for button in self.buttons:
                button.check_hover(mouse_pos)
                if button.is_clicked(mouse_pos, event):
                    self.handle_button_click(button)
                    
            # Handle scroll events
            if event.type == pygame.MOUSEWHEEL and self.state in ["VOTING", "THIEVES", "ANGEL"]:
                self.scroll_offset = max(0, min(self.scroll_offset - event.y * 20, self.max_scroll))
                    
        return True
        
    def handle_button_click(self, button):
        if self.state == "WELCOME" and button.text == "START GAME":
            self.state = "REGISTRATION"
            self.create_registration_screen()
            
        elif self.state == "REGISTRATION" and button.text == "CONFIRM PLAYERS":
            self.player_names = [box.text.strip() for box in self.input_boxes]
            
            # Validate names
            if any(not name for name in self.player_names):
                self.show_popup("Error", "All player names must be non-empty!", lambda: None)
                return
                
            if len(set(self.player_names)) != 8:
                self.show_popup("Error", "All player names must be unique!", lambda: None)
                return
                
            self.assign_roles()
            
        elif self.state == "ROLE_REVEAL" and button.text == "CONTINUE":
            self.current_player_index += 1
            if self.current_player_index >= len(self.player_names):
                self.state = "GAME_LOOP"
                self.round_number = 1
                self.update_alive_players()
                self.state = "VOTING"
                self.create_voting_screen()
                
        elif self.state == "RESULTS" and button.text == "CONTINUE TO NEXT ROUND":
            self.check_win_conditions()
            
        elif self.state == "GAME_OVER" and button.text == "PLAY AGAIN":
            self.__init__()  # Reset the game
            
    def draw(self):
        screen.fill(DARK_BLUE)
        
        if hasattr(self, 'popup') and self.popup['active']:
            self.draw_popup()
            return
            
        if self.state == "WELCOME":
            self.draw_welcome_screen()
        elif self.state == "REGISTRATION":
            self.draw_registration_screen()
        elif self.state == "ROLE_REVEAL":
            self.draw_role_reveal_screen()
        elif self.state == "VOTING":
            self.draw_voting_screen()
        elif self.state == "THIEVES":
            self.draw_thieves_screen()
        elif self.state == "ANGEL":
            self.draw_angel_screen()
        elif self.state == "RESULTS":
            self.draw_results_screen()
        elif self.state == "GAME_OVER":
            self.draw_final_results_screen()
            
        for button in self.buttons:
            button.draw(screen)
            
        pygame.display.flip()
        
    def draw_welcome_screen(self):
        title = title_font.render("DAKATI GAME", True, YELLOW)
        subtitle = header_font.render("A Social Deduction Game for 8 Players", True, WHITE)
        
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 220))
        
    def draw_registration_screen(self):
        title = header_font.render("Player Registration", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        for i, box in enumerate(self.input_boxes):
            label = text_font.render(f"Player {i+1}:", True, WHITE)
            screen.blit(label, (150, box.rect.y + 10))
            box.draw(screen)
            
    def draw_role_reveal_screen(self):
        player = self.player_names[self.current_player_index]
        role_data = self.players[player]
        
        title = header_font.render(f"{player}'s Role", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        role_text = header_font.render(role_data['role'].upper(), True, 
                                     CITIZEN_COLOR if role_data['role'] == 'Citizen' else
                                     THIEF_COLOR if role_data['role'] == 'Thief' else
                                     ANGEL_COLOR)
        screen.blit(role_text, (SCREEN_WIDTH//2 - role_text.get_width()//2, 150))
        
        if role_data['role'] == 'Thief':
            partner_text = text_font.render(f"Your partner: {role_data['partner']}", True, YELLOW)
            screen.blit(partner_text, (SCREEN_WIDTH//2 - partner_text.get_width()//2, 220))
            
    def draw_voting_screen(self):
        voter = self.alive_players[self.current_voter_index]
        role_data = self.players[voter]
        
        title = header_font.render(f"Round {self.round_number}: Voting Phase", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
        
        instruction = text_font.render(f"{voter}, vote to eliminate:", True, WHITE)
        screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, 80))
        
        # Create player buttons for voting
        options = [p for p in self.alive_players if p != voter]
        if role_data['role'] == 'Thief':
            options = [p for p in options if p != role_data['partner']]
            
        self.buttons = []
        y_pos = 120 - self.scroll_offset
        button_width = 300
        button_height = 50
        
        for i, player in enumerate(options):
            btn = Button(
                SCREEN_WIDTH//2 - button_width//2, 
                y_pos + i * (button_height + 10), 
                button_width, 
                button_height, 
                player, 
                LIGHT_BLUE, 
                (100, 100, 200)
            )
            btn.player_name = player
            self.buttons.append(btn)
            
        self.max_scroll = max(0, y_pos + len(options) * (button_height + 10) - (SCREEN_HEIGHT - 150))
        
        # Current status
        status1 = text_font.render(f"Alive: {', '.join(self.alive_players)}", True, GREEN)
        status2 = text_font.render(f"Eliminated: {', '.join(self.eliminated_players) if self.eliminated_players else 'None'}", True, RED)
        
        screen.blit(status1, (50, SCREEN_HEIGHT - 80))
        screen.blit(status2, (50, SCREEN_HEIGHT - 50))
        
    def draw_thieves_screen(self):
        thieves = [name for name, data in self.players.items() 
                  if data['alive'] and data['role'] == 'Thief']
        
        title = header_font.render("Thieves' Phase", True, RED)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
        
        instruction = text_font.render(f"Thieves {' & '.join(thieves)}, choose a target:", True, WHITE)
        screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, 80))
        
        # Create target buttons
        targets = [name for name, data in self.players.items() if data['alive']]
        self.buttons = []
        y_pos = 120 - self.scroll_offset
        button_width = 300
        button_height = 50
        
        for i, player in enumerate(targets):
            btn = Button(
                SCREEN_WIDTH//2 - button_width//2, 
                y_pos + i * (button_height + 10), 
                button_width, 
                button_height, 
                player, 
                (100, 50, 50), 
                (150, 80, 80)
            )
            btn.player_name = player
            self.buttons.append(btn)
            
        self.max_scroll = max(0, y_pos + len(targets) * (button_height + 10) - (SCREEN_HEIGHT - 150))
        
    def draw_angel_screen(self):
        angel = next((name for name, data in self.players.items() 
                     if data['alive'] and data['role'] == 'Angel'), None)
        
        title = header_font.render("Angel's Phase", True, ANGEL_COLOR)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
        
        instruction = text_font.render(f"Angel {angel}, choose someone to save:", True, WHITE)
        screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, 80))
        
        # Create save buttons
        targets = [name for name, data in self.players.items() if data['alive']]
        self.buttons = []
        y_pos = 120 - self.scroll_offset
        button_width = 300
        button_height = 50
        
        for i, player in enumerate(targets):
            btn = Button(
                SCREEN_WIDTH//2 - button_width//2, 
                y_pos + i * (button_height + 10), 
                button_width, 
                button_height, 
                player, 
                (50, 50, 100), 
                (80, 80, 150)
            )
            btn.player_name = player
            self.buttons.append(btn)
            
        self.max_scroll = max(0, y_pos + len(targets) * (button_height + 10) - (SCREEN_HEIGHT - 150))
        
    def draw_results_screen(self):
        title = header_font.render(f"Round {self.round_number} Results", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
        
        alive_text = text_font.render(f"Alive Players: {', '.join(self.alive_players)}", True, GREEN)
        eliminated_text = text_font.render(f"Eliminated Players: {', '.join(self.eliminated_players) if self.eliminated_players else 'None'}", True, RED)
        
        screen.blit(alive_text, (50, 120))
        screen.blit(eliminated_text, (50, 160))
        
    def draw_final_results_screen(self):
        title = header_font.render("Game Over", True, RED)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
        
        result_text = header_font.render(self.final_message, True, YELLOW)
        screen.blit(result_text, (SCREEN_WIDTH//2 - result_text.get_width()//2, 100))
        
        # Player roles
        y_pos = 180
        for name, data in self.players.items():
            status = "ALIVE" if data['alive'] else "ELIMINATED"
            color = GREEN if data['alive'] else RED
            
            player_text = text_font.render(f"{name}:", True, WHITE)
            role_text = text_font.render(f"{data['role'].upper()} ({status})", True, color)
            
            screen.blit(player_text, (150, y_pos))
            screen.blit(role_text, (400, y_pos))
            y_pos += 30
            
    def draw_popup(self):
        # Darken background
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (0, 0))
        
        # Popup box
        popup_width = 600
        popup_height = 300
        popup_rect = pygame.Rect(
            (SCREEN_WIDTH - popup_width) // 2,
            (SCREEN_HEIGHT - popup_height) // 2,
            popup_width,
            popup_height
        )
        
        pygame.draw.rect(screen, WHITE, popup_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, popup_rect, 2, border_radius=10)
        
        # Title
        title = header_font.render(self.popup['title'], True, BLACK)
        screen.blit(title, (popup_rect.centerx - title.get_width()//2, popup_rect.y + 20))
        
        # Message (with line breaks)
        message_lines = self.popup['message'].split('\n')
        for i, line in enumerate(message_lines):
            msg = text_font.render(line, True, BLACK)
            screen.blit(msg, (popup_rect.centerx - msg.get_width()//2, popup_rect.y + 80 + i * 30))
            
        # OK button
        ok_btn = Button(
            popup_rect.centerx - 50,
            popup_rect.y + popup_height - 70,
            100, 50,
            "OK", GREEN, (50, 200, 50)
        )
        ok_btn.draw(screen)
        
        # Check if OK button is clicked (handled in handle_events)
        
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            self.draw()
            clock.tick(60)
            
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = DakatiGame()
    game.run()