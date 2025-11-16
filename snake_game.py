

import pygame
import random
import json
import os
from enum import Enum
from collections import deque

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
FPS = 8

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

class Direction(Enum):
    """Enum for movement directions"""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class PowerUpType(Enum):
    """Types of power-ups available"""
    SPEED_BOOST = "Speed Boost"
    SLOW_DOWN = "Slow Down"
    DOUBLE_POINTS = "Double Points"
    INVINCIBILITY = "Invincibility"

class PowerUp:
    """Power-up items that appear on the grid"""
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.duration = 5000  # milliseconds
        self.color = {
            PowerUpType.SPEED_BOOST: CYAN,
            PowerUpType.SLOW_DOWN: PURPLE,
            PowerUpType.DOUBLE_POINTS: YELLOW,
            PowerUpType.INVINCIBILITY: ORANGE
        }[power_type]

class Snake:
    """Snake entity with movement and collision logic"""
    def __init__(self, x, y, color, is_ai=False):
        self.body = deque([(x, y)])
        self.direction = Direction.RIGHT
        self.color = color
        self.score = 0
        self.is_ai = is_ai
        self.alive = True
        self.power_ups = {}
        self.speed_multiplier = 1.0
        
    def move(self, grow=False):
        """Move snake in current direction"""
        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        self.body.appendleft(new_head)
        if not grow:
            self.body.pop()
        
    def grow(self):
        """Increase snake length by adding to tail"""
        tail = self.body[-1]
        self.body.append(tail)
        
    def check_collision(self, obstacles=None):
        """Check if snake collided with walls or itself"""
        head_x, head_y = self.body[0]
        
        # Wall collision
        if head_x < 0 or head_x >= GRID_WIDTH or head_y < 0 or head_y >= GRID_HEIGHT:
            return True
            
        # Self collision
        if (head_x, head_y) in list(self.body)[1:]:
            return True
            
        # Obstacle collision
        if obstacles and (head_x, head_y) in obstacles:
            return True
            
        return False
    
    def ai_move(self, food_pos, obstacles=None):
        """Simple AI using BFS pathfinding"""
        if not self.is_ai:
            return
            
        head = self.body[0]
        path = self.bfs_path(head, food_pos, obstacles)
        
        if path and len(path) > 1:
            next_pos = path[1]
            dx = next_pos[0] - head[0]
            dy = next_pos[1] - head[1]
            
            if dx == 1:
                self.direction = Direction.RIGHT
            elif dx == -1:
                self.direction = Direction.LEFT
            elif dy == 1:
                self.direction = Direction.DOWN
            elif dy == -1:
                self.direction = Direction.UP
    
    def bfs_path(self, start, goal, obstacles=None):
        """Breadth-First Search pathfinding algorithm"""
        if obstacles is None:
            obstacles = set()
            
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            (x, y), path = queue.popleft()
            
            if (x, y) == goal:
                return path
                
            for direction in Direction:
                dx, dy = direction.value
                next_pos = (x + dx, y + dy)
                
                if (next_pos not in visited and 
                    0 <= next_pos[0] < GRID_WIDTH and 
                    0 <= next_pos[1] < GRID_HEIGHT and
                    next_pos not in obstacles and
                    next_pos not in self.body):
                    
                    visited.add(next_pos)
                    queue.append((next_pos, path + [next_pos]))
        
        return None

class Game:
    """Main game controller"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Advanced Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.player = None
        self.ai_snake = None
        self.food = None
        self.power_up = None
        self.obstacles = set()
        self.level = 1
        self.game_mode = None
        self.high_scores = self.load_high_scores()
        self.running = True
        
    def load_high_scores(self):
        """Load high scores from file"""
        try:
            if os.path.exists('snake_scores.json'):
                with open('snake_scores.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        return {'classic': 0, 'ai_battle': 0, 'obstacle': 0}
    
    def save_high_scores(self):
        """Save high scores to file"""
        try:
            with open('snake_scores.json', 'w') as f:
                json.dump(self.high_scores, f)
        except:
            pass
    
    def spawn_food(self):
        """Spawn food at random empty position"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            
            if ((x, y) not in self.player.body and 
                (not self.ai_snake or (x, y) not in self.ai_snake.body) and
                (x, y) not in self.obstacles):
                self.food = (x, y)
                break
    
    def spawn_power_up(self):
        """Spawn power-up at random position"""
        if random.random() < 0.3:  # 30% chance
            while True:
                x = random.randint(0, GRID_WIDTH - 1)
                y = random.randint(0, GRID_HEIGHT - 1)
                
                if ((x, y) not in self.player.body and 
                    (x, y) != self.food and
                    (x, y) not in self.obstacles):
                    power_type = random.choice(list(PowerUpType))
                    self.power_up = PowerUp(x, y, power_type)
                    break
    
    def spawn_obstacles(self):
        """Create obstacles for obstacle mode"""
        self.obstacles.clear()
        num_obstacles = 10 + (self.level * 2)
        
        for _ in range(num_obstacles):
            while True:
                x = random.randint(1, GRID_WIDTH - 2)
                y = random.randint(1, GRID_HEIGHT - 2)
                
                if ((x, y) not in self.player.body and
                    (x, y) != self.food and
                    (x, y) not in self.obstacles):
                    self.obstacles.add((x, y))
                    break
    
    def show_menu(self):
        """Display main menu"""
        menu_running = True
        selected = 0
        options = [
            "1. Classic Mode",
            "2. AI Battle Mode",
            "3. Obstacle Challenge",
            "4. How to Play",
            "5. View High Scores",
            "6. Quit"
        ]
        
        while menu_running:
            self.screen.fill(BLACK)
            
            # Title
            title = self.font.render("ADVANCED SNAKE GAME", True, GREEN)
            self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 50))
            
            # Menu options
            for i, option in enumerate(options):
                color = YELLOW if i == selected else WHITE
                text = self.small_font.render(option, True, color)
                self.screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, 150 + i * 50))
            
            # Instructions
            inst = self.small_font.render("Use Arrow Keys to Navigate, Enter to Select", True, GRAY)
            self.screen.blit(inst, (WINDOW_WIDTH//2 - inst.get_width()//2, 500))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if selected == 5:  # Quit
                            return None
                        elif selected == 4:  # High Scores
                            self.show_high_scores()
                        elif selected == 3:  # How to Play
                            self.show_instructions()
                        else:
                            return selected + 1
        
        return None
    
    def show_high_scores(self):
        """Display high scores screen"""
        showing = True
        while showing:
            self.screen.fill(BLACK)
            
            title = self.font.render("HIGH SCORES", True, YELLOW)
            self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
            
            y_pos = 200
            for mode, score in self.high_scores.items():
                text = self.small_font.render(f"{mode.replace('_', ' ').title()}: {score}", True, WHITE)
                self.screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, y_pos))
                y_pos += 50
            
            back = self.small_font.render("Press ESC to go back", True, GRAY)
            self.screen.blit(back, (WINDOW_WIDTH//2 - back.get_width()//2, 500))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    showing = False
    
    def show_instructions(self):
        """Display comprehensive instructions"""
        showing = True
        page = 0
        max_pages = 3
        
        while showing:
            self.screen.fill(BLACK)
            
            if page == 0:
                # Page 1: Basic Controls
                title = self.font.render("HOW TO PLAY - CONTROLS", True, GREEN)
                self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 30))
                
                instructions = [
                    "",
                    "BASIC CONTROLS:",
                    "  Arrow Keys (↑ ↓ ← →) - Move snake",
                    "  ESC - Pause / Return to menu",
                    "  Enter - Select menu options",
                    "",
                    "MOVEMENT RULES:",
                    "  • Snake moves continuously",
                    "  • Cannot reverse direction",
                    "  • Example: If moving RIGHT, can't go LEFT",
                    "",
                    "OBJECTIVE:",
                    "  • Eat red food squares to grow",
                    "  • Each food = 10 points",
                    "  • Avoid walls and your own body",
                    "  • Try to get the highest score!",
                ]
                
            elif page == 1:
                # Page 2: Game Modes
                title = self.font.render("GAME MODES", True, GREEN)
                self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 30))
                
                instructions = [
                    "",
                    "CLASSIC MODE:",
                    "  • Traditional snake gameplay",
                    "  • Eat food, grow, avoid obstacles",
                    "  • Perfect for beginners",
                    "",
                    "AI BATTLE MODE:",
                    "  • Race against AI opponent (blue snake)",
                    "  • Compete for the same food",
                    "  • Highest score wins!",
                    "",
                    "OBSTACLE CHALLENGE:",
                    "  • Navigate around gray obstacles",
                    "  • More obstacles as level increases",
                    "  • Most challenging mode",
                ]
                
            else:
                # Page 3: Power-ups
                title = self.font.render("POWER-UPS & TIPS", True, GREEN)
                self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 30))
                
                instructions = [
                    "",
                    "POWER-UPS (colored circles):",
                    "  Cyan - Speed Boost (move faster)",
                    "  Purple - Slow Down (easier control)",
                    "  Yellow - Double Points (2x score)",
                    "  Orange - Invincibility (can't die)",
                    "",
                    "STRATEGY TIPS:",
                    "  • Stay in center for more space",
                    "  • Plan 2-3 moves ahead",
                    "  • Don't trap yourself in corners",
                    "  • Use edges to create patterns",
                    "  • Grab yellow power-ups for high scores",
                ]
            
            y_pos = 100
            for line in instructions:
                if line.startswith("  •") or line.startswith("  Cyan") or line.startswith("  Purple") or line.startswith("  Yellow") or line.startswith("  Orange"):
                    text = self.small_font.render(line, True, CYAN)
                elif line.endswith(":"):
                    text = self.small_font.render(line, True, YELLOW)
                else:
                    text = self.small_font.render(line, True, WHITE)
                self.screen.blit(text, (50, y_pos))
                y_pos += 25
            
            # Page navigation
            nav_text = f"Page {page + 1} of {max_pages}"
            nav = self.small_font.render(nav_text, True, GRAY)
            self.screen.blit(nav, (WINDOW_WIDTH//2 - nav.get_width()//2, 520))
            
            controls = self.small_font.render("← Previous | Next → | ESC to go back", True, GRAY)
            self.screen.blit(controls, (WINDOW_WIDTH//2 - controls.get_width()//2, 550))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    showing = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        page = max(0, page - 1)
                    elif event.key == pygame.K_RIGHT:
                        page = min(max_pages - 1, page + 1)
    
    def init_game(self, mode):
        """Initialize game with selected mode"""
        self.game_mode = mode
        self.level = 1
        self.player = Snake(GRID_WIDTH // 2, GRID_HEIGHT // 2, GREEN)
        
        if mode == 2:  # AI Battle
            self.ai_snake = Snake(GRID_WIDTH // 4, GRID_HEIGHT // 4, BLUE, is_ai=True)
        else:
            self.ai_snake = None
        
        if mode == 3:  # Obstacle Challenge
            self.spawn_obstacles()
        else:
            self.obstacles.clear()
        
        self.spawn_food()
        self.power_up = None
    
    def handle_input(self):
        """Handle player input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.player.direction != Direction.DOWN:
                    self.player.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.player.direction != Direction.UP:
                    self.player.direction = Direction.DOWN
                elif event.key == pygame.K_LEFT and self.player.direction != Direction.RIGHT:
                    self.player.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.player.direction != Direction.LEFT:
                    self.player.direction = Direction.RIGHT
                elif event.key == pygame.K_ESCAPE:
                    return False
        
        return True
    
    def update(self):
        """Update game state"""
        # Check food collision BEFORE moving
        player_will_eat = self.player.body[0] == self.food
        ai_will_eat = self.ai_snake and self.ai_snake.alive and self.ai_snake.body[0] == self.food
        
        # Move snakes (grow if they're about to eat)
        self.player.move(grow=player_will_eat)
        if self.ai_snake and self.ai_snake.alive:
            self.ai_snake.ai_move(self.food, self.obstacles)
            self.ai_snake.move(grow=ai_will_eat)
        
        # Process food eating
        if player_will_eat:
            points = 10
            if PowerUpType.DOUBLE_POINTS in self.player.power_ups:
                points *= 2
            self.player.score += points
            self.spawn_food()
            
            if random.random() < 0.2:
                self.spawn_power_up()
        
        if ai_will_eat:
            self.ai_snake.score += 10
            if not player_will_eat:  # Only spawn new food if player didn't also eat it
                self.spawn_food()
        
        # Check power-up collision
        if self.power_up and self.player.body[0] == (self.power_up.x, self.power_up.y):
            self.player.power_ups[self.power_up.type] = pygame.time.get_ticks()
            self.power_up = None
        
        # Check collisions
        if self.player.check_collision(self.obstacles):
            self.player.alive = False
            return False
        
        if self.ai_snake and self.ai_snake.alive:
            if self.ai_snake.check_collision(self.obstacles):
                self.ai_snake.alive = False
        
        return True
    
    def draw(self):
        """Render game state"""
        self.screen.fill(BLACK)
        
        # Draw grid
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_WIDTH, y), 1)
        
        # Draw obstacles
        for obs_x, obs_y in self.obstacles:
            pygame.draw.rect(self.screen, GRAY, 
                           (obs_x * GRID_SIZE, obs_y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        
        # Draw food
        pygame.draw.rect(self.screen, RED, 
                        (self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        
        # Draw power-up
        if self.power_up:
            pygame.draw.circle(self.screen, self.power_up.color,
                             (self.power_up.x * GRID_SIZE + GRID_SIZE//2,
                              self.power_up.y * GRID_SIZE + GRID_SIZE//2),
                             GRID_SIZE // 2)
        
        # Draw player snake
        for i, (x, y) in enumerate(self.player.body):
            color = self.player.color if i > 0 else YELLOW
            pygame.draw.rect(self.screen, color,
                           (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        
        # Draw AI snake
        if self.ai_snake and self.ai_snake.alive:
            for i, (x, y) in enumerate(self.ai_snake.body):
                color = self.ai_snake.color if i > 0 else CYAN
                pygame.draw.rect(self.screen, color,
                               (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        
        # Draw UI
        score_text = self.small_font.render(f"Score: {self.player.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        if self.ai_snake:
            ai_score = self.small_font.render(f"AI: {self.ai_snake.score}", True, CYAN)
            self.screen.blit(ai_score, (10, 40))
        
        level_text = self.small_font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (WINDOW_WIDTH - 120, 10))
        
        pygame.display.flip()
    
    def game_over(self):
        """Display game over screen"""
        mode_key = {1: 'classic', 2: 'ai_battle', 3: 'obstacle'}[self.game_mode]
        
        if self.player.score > self.high_scores[mode_key]:
            self.high_scores[mode_key] = self.player.score
            self.save_high_scores()
        
        showing = True
        while showing:
            self.screen.fill(BLACK)
            
            title = self.font.render("GAME OVER", True, RED)
            self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 150))
            
            score = self.small_font.render(f"Your Score: {self.player.score}", True, WHITE)
            self.screen.blit(score, (WINDOW_WIDTH//2 - score.get_width()//2, 250))
            
            high = self.small_font.render(f"High Score: {self.high_scores[mode_key]}", True, YELLOW)
            self.screen.blit(high, (WINDOW_WIDTH//2 - high.get_width()//2, 300))
            
            if self.ai_snake:
                winner = "You Win!" if self.player.score > self.ai_snake.score else "AI Wins!"
                win_text = self.font.render(winner, True, GREEN if self.player.score > self.ai_snake.score else RED)
                self.screen.blit(win_text, (WINDOW_WIDTH//2 - win_text.get_width()//2, 350))
            
            options = self.small_font.render("Press ENTER to return to menu or ESC to quit", True, GRAY)
            self.screen.blit(options, (WINDOW_WIDTH//2 - options.get_width()//2, 500))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    return True
        
        return False
    
    def run(self):
        """Main game loop"""
        while self.running:
            mode = self.show_menu()
            
            if mode is None:
                break
            
            self.init_game(mode)
            playing = True
            
            while playing and self.running:
                self.clock.tick(FPS)
                
                if not self.handle_input():
                    playing = False
                    continue
                
                if not self.update():
                    playing = False
                
                self.draw()
            
            if self.running and not self.game_over():
                break
        
        pygame.quit()

# Main execution
if __name__ == "__main__":
    game = Game()
    game.run()