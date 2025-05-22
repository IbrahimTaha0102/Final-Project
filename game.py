import pygame
import math
import random

# Base class for game objects
class GameObject:
    def __init__(self, x, y):
        self.x = x # Where it is left/right
        self.y = y # Where it is up/down
    
    def update(self, dt):
        pass
    
    def draw(self, screen):
        pass

# This is for stuff that gets in your way
class Obstacle(GameObject):
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y) # Initialize parent class attributes
        self.width = width #chunkyness
        self.height = height #length
        self.color = color #color (RGB tuple)
    
    def draw(self, screen):
        pygame.draw.rect(
            screen, self.color,
            (int(self.x), int(self.y), self.width, self.height) #derived from parent class attributes
        )
    
    def get_collision_rect(self):
        # This is used to check if we hit something
        return (self.x, self.y, self.width, self.height)

# Static wall obstacle
class Wall(Obstacle):
    def __init__(self, x, y, width, height): #traits of the wall
        super().__init__(x, y, width, height, (0, 0, 139))  # The dark blue walls

# Moving platform obstacle
class MovingPlatform(Obstacle):
    def __init__(self, x, y, w=None, h=None, width=None, height=None, move_type=None, **kwargs):
        # Handle both w/h and width/height naming conventions
        actual_width = width if width is not None else w
        actual_height = height if height is not None else h
        
        super().__init__(x, y, actual_width, actual_height, (148, 0, 211))  # PURPLE
        self.move_type = move_type
        
        if move_type == "vertical": #kwargs = kew word argumments 
            self.base_y = kwargs.get("base_y", y)  # Starting y position, defaults to initial y position
            self.amp = kwargs.get("amp", 50)
            self.speed = kwargs.get("speed", 1.0)
            self.dir = kwargs.get("dir", 1) # Direction: 1 for down, -1 for up initially
        elif move_type == "horizontal": # For platforms that move left and right
            self.base_x = kwargs.get("base_x", x) # Starting x position, defaults to initial x
            self.amp = kwargs.get("amp", 50)
            self.speed = kwargs.get("speed", 1.0)
            self.dir = kwargs.get("dir", 1) # Direction: 1 for right, -1 for left initially
        elif move_type == "random":
            self.dx = kwargs.get("dx", random.uniform(-2, 2))
            self.dy = kwargs.get("dy", random.uniform(-2, 2))
    
    def update(self, dt, border_thickness, window_width, window_height):
        # Parameters:
        '''- dt: Delta time (time since last frame)
        - border_thickness: Thickness of the game boundaries
        - window_width: Width of the game window
        - window_height: Height of the game window'''
        if self.move_type == "vertical":
            self.y += self.speed * self.dir
            if abs(self.y - self.base_y) >= self.amp:
                self.dir *= -1
                self.y += self.speed * self.dir
        elif self.move_type == "horizontal":
            self.x += self.speed * self.dir
            if abs(self.x - self.base_x) >= self.amp:
                self.dir *= -1
                self.x += self.speed * self.dir
        elif self.move_type == "random":
            self.x += self.dx
            self.y += self.dy
            if self.x < border_thickness or self.x + self.width > window_width - border_thickness:
                self.dx *= -1
            if self.y < border_thickness or self.y + self.height > window_height - border_thickness:
                self.dy *= -1

# Repulsor obstacle
class Repulsor(GameObject):
    # A circular obstacle that bounces around and repels the ball on contact
    # Initialized with position, radius, color, and velocity components (dx, dy)
    def __init__(self, x, y, radius=None, color=None, dx=0, dy=0, **kwargs):
        super().__init__(x, y)
        self.radius = radius
        self.color = color
        self.dx = dx
        self.dy = dy
    
    def update(self, dt, border_thickness, window_width, window_height):
        # Updates repulsor position based on velocity and handles boundary collisions
        # Reverses direction (dx, dy) when hitting any game boundary to create bouncing effect

        if hasattr(self, 'dx') and hasattr(self, 'dy'):
            self.x += self.dx
            self.y += self.dy
            if self.x - self.radius < border_thickness or self.x + self.radius > window_width - border_thickness:
                self.dx *= -1
            if self.y - self.radius < border_thickness or self.y + self.radius > window_height - border_thickness:
                self.dy *= -1
    
    def draw(self, screen):
        pygame.draw.circle(
            screen, self.color,
            (int(self.x), int(self.y)),
            self.radius
        )

# Ball class
class Ball(GameObject):
    # Ball class: Player-controlled golf ball with physics and collision handling
    # Attributes: position (x,y), radius, image, velocity components, movement flags, friction
    # launch(): Propels ball with angle and power
    # stop(): Halts ball movement by zeroing velocities and updating state
    # update(): Applies friction, updates position, and auto-stops when nearly stationary
    # draw(): Renders ball image at current position on screen
    # handle_border_collision(): Prevents ball from leaving playable area with 80% bounce
    # handle_obstacle_collision(): Detects collisions, determines impact side,

    def __init__(self, x, y, radius, image):
        super().__init__(x, y)
        self.radius = radius
        self.image = image
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_moving = False
        self.teleporting = False
        self.friction = 0.98
    
    def launch(self, angle_degrees, power, max_power):
        self.is_moving = True
        speed = (power / max_power) * 15
        self.velocity_x = speed * math.cos(math.radians(angle_degrees))
        self.velocity_y = -speed * math.sin(math.radians(angle_degrees))
    
    def stop(self):
        self.is_moving = False
        self.velocity_x = 0
        self.velocity_y = 0
    
    def update(self, dt):
        if self.is_moving and not self.teleporting:
            # Apply air friction
            self.velocity_x *= self.friction
            self.velocity_y *= self.friction
            
            # Update position
            self.x += self.velocity_x
            self.y += self.velocity_y
            
            # Check if ball is almost stopped
            if abs(self.velocity_x) < 0.1 and abs(self.velocity_y) < 0.1:
                self.stop()
    
    def draw(self, screen):
        screen.blit(
            self.image,
            (int(self.x - self.radius), int(self.y - self.radius))
        )
    
    def handle_border_collision(self, border_thickness, window_width, window_height):
        if self.x - self.radius < border_thickness:
            self.x = border_thickness + self.radius
            self.velocity_x *= -0.8
        if self.x + self.radius > window_width - border_thickness:
            self.x = window_width - border_thickness - self.radius
            self.velocity_x *= -0.8
        if self.y - self.radius < border_thickness:
            self.y = border_thickness + self.radius
            self.velocity_y *= -0.8
        if self.y + self.radius > window_height - border_thickness:
            self.y = window_height - border_thickness - self.radius
            self.velocity_y *= -0.8
    
    def handle_obstacle_collision(self, obstacle):
        ox, oy, ow, oh = obstacle
        if (self.x + self.radius > ox and
            self.x - self.radius < ox + ow and
            self.y + self.radius > oy and
            self.y - self.radius < oy + oh):
            
            penetration_left = abs(self.x + self.radius - ox)
            penetration_right = abs(self.x - self.radius - (ox + ow))
            penetration_top = abs(self.y + self.radius - oy)
            penetration_bottom = abs(self.y - self.radius - (oy + oh))
            
            min_pen = min(
                penetration_left,
                penetration_right,
                penetration_top,
                penetration_bottom
            )
            
            if min_pen == penetration_left:
                self.x = ox - self.radius
                self.velocity_x *= -0.8
                return "left"
            elif min_pen == penetration_right:
                self.x = ox + ow + self.radius
                self.velocity_x *= -0.8
                return "right"
            elif min_pen == penetration_top:
                self.y = oy - self.radius
                self.velocity_y *= -0.8
                return "top"
            else:
                self.y = oy + oh + self.radius
                self.velocity_y *= -0.8
                return "bottom"
        return None
    
    def handle_platform_collision(self, platform):
        collision_side = self.handle_obstacle_collision(
            (platform.x, platform.y, platform.width, platform.height)
        )
        
        if collision_side and platform.move_type in ["horizontal", "vertical"]:
            if collision_side in ["left", "right"] and platform.move_type == "horizontal":
                self.velocity_x += platform.speed * platform.dir * 0.5
            elif collision_side in ["top", "bottom"] and platform.move_type == "vertical":
                self.velocity_y += platform.speed * platform.dir * 0.5
    
    def handle_repulsor_collision(self, repulsor, current_level):
        dx = self.x - repulsor.x
        dy = self.y - repulsor.y
        dist = math.hypot(dx, dy)
        
        if dist < self.radius + repulsor.radius:
            # Push-out
            if dist > 0:
                overlap = (self.radius + repulsor.radius) - dist
                push_amount = overlap + 0.1
                norm_dx = dx / dist
                norm_dy = dy / dist
                self.x += norm_dx * push_amount
                self.y += norm_dy * push_amount
            else:
                push_amount = (self.radius + repulsor.radius) + 0.1
                self.x += push_amount
                norm_dx, norm_dy = 1.0, 0.0
            
            # Rebound logic
            if current_level == 4:
                incoming = math.hypot(self.velocity_x, self.velocity_y)
                ref_speed = max(incoming, 1.0)
                launch = 4 * ref_speed
                self.velocity_x = norm_dx * launch
                self.velocity_y = norm_dy * launch
            elif current_level == 5:
                incoming = math.hypot(self.velocity_x, self.velocity_y)
                if incoming > 0:
                    vx_norm = self.velocity_x / incoming
                    vy_norm = self.velocity_y / incoming
                    self.velocity_x = -4 * incoming * vx_norm
                    self.velocity_y = -4 * incoming * vy_norm
            else:
                self.velocity_x *= -1.1
                self.velocity_y *= -1.1
            
            return True
        return False
    
    def teleport_to_hole(self, hole_x, hole_y, hole_sound):
        dx = hole_x - self.x
        dy = hole_y - self.y
        distance = math.hypot(dx, dy)
        
        if distance < 2:
            self.x = hole_x
            self.y = hole_y
            self.velocity_x = 0
            self.velocity_y = 0
            self.is_moving = False
            hole_sound.play()
            return True
        
        move_factor = min(0.2, distance / 10)
        self.x += dx * move_factor
        self.y += dy * move_factor
        self.velocity_x *= 0.8
        self.velocity_y *= 0.8
        
        return False

# UI element base class
class UIElement(GameObject):
    def __init__(self, x, y, width, height):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
    
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

# Button class
class Button(UIElement):
    def __init__(self, x, y, width, height, text, color, text_color, font):
        super().__init__(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = font
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

# Slider class
class Slider(UIElement):
    def __init__(self, x, y, width, height, min_value, max_value, initial_value, color):
        super().__init__(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.color = color
        self.dragging = False
    
    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        slider_x = self.x + (self.value / self.max_value) * self.width
        pygame.draw.circle(screen, (0, 0, 0), (int(slider_x), int(self.y + self.height // 2)), 9)
    
    def handle_mouse_down(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.dragging = True
            return True
        return False
    
    def handle_mouse_up(self):
        self.dragging = False
    
    def handle_mouse_motion(self, mouse_x):
        if self.dragging:
            rel_x = max(0, min(mouse_x - self.x, self.width))
            self.value = (rel_x / self.width) * self.max_value
            return True
        return False

# Level class
class Level:
    def __init__(self, level_number, hole_position, walls_data, window_width, window_height, border_thickness):
        self.level_number = level_number
        self.hole_x, self.hole_y = hole_position
        self.walls = []
        self.moving_platforms = []
        self.repulsors = []
        self.window_width = window_width
        self.window_height = window_height
        self.border_thickness = border_thickness
        
        # Create walls
        for wall_data in walls_data:
            x, y, w, h = wall_data
            self.walls.append(Wall(x, y, w, h))
    
    def add_moving_platforms(self, platforms_data):
        for platform_data in platforms_data:
            self.moving_platforms.append(MovingPlatform(**platform_data))
    
    def add_repulsors(self, repulsors_data):
        for repulsor_data in repulsors_data:
            self.repulsors.append(Repulsor(**repulsor_data))
    
    def update(self, dt):
        for platform in self.moving_platforms:
            platform.update(dt, self.border_thickness, self.window_width, self.window_height)
        
        for repulsor in self.repulsors:
            repulsor.update(dt, self.border_thickness, self.window_width, self.window_height)
    
    def draw(self, screen):
        # Draw walls
        for wall in self.walls:
            wall.draw(screen)
        
        # Draw moving platforms
        for platform in self.moving_platforms:
            platform.draw(screen)
        
        # Draw repulsors
        for repulsor in self.repulsors:
            repulsor.draw(screen)
        
        # Draw hole
        pygame.draw.circle(screen, (0, 0, 0), (int(self.hole_x), int(self.hole_y)), 12)
    
    def get_all_obstacles(self):
        obstacles = []
        for wall in self.walls:
            obstacles.append(wall.get_collision_rect())
        
        for platform in self.moving_platforms:
            obstacles.append(platform.get_collision_rect())
        
        return obstacles

# Game class
class MiniGolfGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Constants
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = 800, 600
        self.BORDER_THICKNESS = 30
        self.BALL_RADIUS = 10
        self.HOLE_RADIUS = 12
        self.HOLE_CAPTURE_FACTOR = 0.75
        self.MAX_POWER = 300
        self.AIR_FRICTION_FACTOR = 0.98
        self.TOTAL_LEVELS = 5
        
        # Colors
        self.GREEN = (0, 150, 0)
        self.BLUE = (0, 0, 139)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BROWN = (139, 69, 0)
        self.ORANGE = (255, 165, 0)
        self.PURPLE = (148, 0, 211)
        self.YELLOW = (255, 255, 0)
        self.RED = (255, 0, 0)
        self.OVERLAY = (0, 0, 0, 180)
        
        # Setup display
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Mini Golf")
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)
        self.clock = pygame.time.Clock()
        
        # Load sounds
        self.hole_sound = pygame.mixer.Sound("sound.wav")
        
        # Load ball image
        ball_img_orig = pygame.image.load("ball.png").convert_alpha()
        self.ball_image = pygame.transform.smoothscale(
            ball_img_orig,
            (self.BALL_RADIUS*2, self.BALL_RADIUS*2)
        )
        
        # Game state
        self.current_level = 1
        self.timer_seconds = 135  # 2 minutes and 15 seconds
        self.game_over = False
        self.game_won = False
        self.game_paused = False
        self.timer_counter = 0
        
        # UI setup
        self.setup_ui()
        
        # Level setup
        self.setup_levels()
        
        # Create ball
        self.ball = Ball(
            self.BORDER_THICKNESS + self.BALL_RADIUS + 20,
            self.WINDOW_HEIGHT // 2,
            self.BALL_RADIUS,
            self.ball_image
        )
        
        # Initialize level
        self.reset_level()
    
    def setup_ui(self):
        # Controls
        controls_y = self.WINDOW_HEIGHT - self.BORDER_THICKNESS + (self.BORDER_THICKNESS - 20)//2
        
        # Angle slider
        self.angle_slider = Slider(
            50, controls_y, 300, 20, 0, 360, 0, self.WHITE
        )
        
        # Power slider
        launch_button_x = 650
        power_slider_x = 400
        self.power_slider = Slider(
            power_slider_x, controls_y, launch_button_x - power_slider_x - 10, 20, 0, self.MAX_POWER, 0, self.WHITE
        )
        
        # Launch button
        self.launch_button = Button(
            launch_button_x, controls_y, 100, 30, "Launch", self.BLUE, self.WHITE, self.font
        )
        
        # Resume button (for pause screen)
        self.resume_button = Button(
            (self.WINDOW_WIDTH - 160)//2,
            (self.WINDOW_HEIGHT - 50)//2,
            160, 50, "Resume", self.GREEN, self.WHITE, self.font
        )
        
        # Play again button (for win/lose screens)
        self.play_again_button = Button(
            (self.WINDOW_WIDTH - 200)//2,
            (self.WINDOW_HEIGHT - 60)//2 + 100,
            200, 60, "Play Again", self.GREEN, self.WHITE, self.font
        )
    
    def setup_levels(self):
        # Define hole positions
        self.hole_positions = [
            (600, 400),  # Level 1
            (400, 100),  # Level 2
            (400, 300),  # Level 3
            (200, 200),  # Level 4
            (700, 500)   # Level 5
        ]
        
        # Define course walls
        self.course_walls = [
            # Level 1 – simple dog‐leg right
            [
                (150, 100, 500, 15),
                (150, 100, 15, 350),
                (150, 450, 400, 15),
                (550, 250, 15, 215),
            ],
            # Level 2 – "Z" fairway
            [],
            # Level 3 – intricate central structure
            [
                (100, 100, 600, 15),
                (100, 485, 600, 15),
                (100, 100, 15, 150),
                (100, 335, 15, 150),
                (685, 100, 15, 150),
                (685, 335, 15, 150),
                (200, 200, 15, 200),
                (585, 200, 15, 200),
                (200, 200, 100, 15),
                (500, 200, 100, 15),
                (200, 385, 100, 15),
                (500, 385, 100, 15),
                (350, 150, 100, 15),
                (350, 435, 100, 15),
                (250, 292, 15, 30),
                (535, 292, 15, 30),
            ],
            # Level 4 – new layout
            [
                (200, 150, 400, 15),
                (200, 450, 400, 15),
                (150, 200, 15, 200),
                (635, 200, 15, 200),
                (300, 300, 200, 15),
            ],
            # Level 5 – no static walls
            []
        ]
        
        # Create levels
        self.levels = []
        for i in range(self.TOTAL_LEVELS):
            level = Level(
                i + 1,
                self.hole_positions[i],
                self.course_walls[i],
                self.WINDOW_WIDTH,
                self.WINDOW_HEIGHT,
                self.BORDER_THICKNESS
            )
            self.levels.append(level)
        
        # Add moving platforms to levels
        self.setup_moving_platforms()
        
        # Add repulsors to levels
        self.setup_repulsors()
    
    def setup_moving_platforms(self):
        # Level 2 platforms
        level2_platforms = [
            {"x":150, "base_y":200, "y":200, "w":80, "h":15,
             "amp":70, "speed":1.0, "dir":1, "move_type":"vertical"},
            {"x":350, "base_y":300, "y":300, "w":80, "h":15,
             "amp":60, "speed":1.2, "dir":-1,"move_type":"vertical"},
            {"x":550, "base_y":200, "y":200, "w":80, "h":15,
             "amp":80, "speed":0.8, "dir":1, "move_type":"vertical"},
            {"x":200, "base_x":200, "y":180, "w":80, "h":15,
             "amp":100,"speed":1.5, "dir":1, "move_type":"horizontal"},
            {"x":450, "base_x":450, "y":280, "w":80, "h":15,
             "amp":120,"speed":1.0, "dir":-1,"move_type":"horizontal"},
        ]
        self.levels[1].add_moving_platforms(level2_platforms)
        
        # Level 3 platforms
        level3_platforms = [
            {"x":150, "base_x":150, "y":250, "w":100, "h":15,
             "amp":70, "speed":1.5, "dir":1, "move_type":"horizontal"},
            {"x":600, "base_y":300, "y":300, "w":80, "h":15,
             "amp":100,"speed":1.8, "dir":-1,"move_type":"vertical"},
            {"x":300, "base_x":300, "y":150, "w":150, "h":15,
             "amp":150,"speed":2.5, "dir":1, "move_type":"horizontal"},
        ]
        self.levels[2].add_moving_platforms(level3_platforms)
        
        # Level 4 platforms
        level4_platforms = [
            {"x":250, "base_x":250, "y":200, "w":100, "h":15,
             "amp":50, "speed":1.0, "dir":1, "move_type":"horizontal"},
            {"x":450, "base_y":350, "y":350, "w":100, "h":15,
             "amp":50, "speed":1.2, "dir":-1,"move_type":"vertical"},
        ]
        self.levels[3].add_moving_platforms(level4_platforms)
        
        # Level 5 platforms (random)
        level5_platforms = []
        for i in range(12):
            x = random.uniform(self.BORDER_THICKNESS+50,
                               self.WINDOW_WIDTH - self.BORDER_THICKNESS - 60)
            y = random.uniform(self.BORDER_THICKNESS+50,
                               self.WINDOW_HEIGHT - self.BORDER_THICKNESS - 10)
            level5_platforms.append({
                "x": x,
                "y": y,
                "w": 60,
                "h": 10,
                "dx": random.uniform(-2, 2),
                "dy": random.uniform(-2, 2),
                "move_type": "random"
            })
        self.levels[4].add_moving_platforms(level5_platforms)
    
    def setup_repulsors(self):
        # Level 4 repulsors
        level4_repulsors = [
            {"x":300, "y":200, "radius":20, "color":self.ORANGE},
            {"x":500, "y":200, "radius":20, "color":self.ORANGE},
            {"x":150, "y":350, "radius":15, "color":self.ORANGE},
            {"x":650, "y":350, "radius":15, "color":self.ORANGE},
        ]
        self.levels[3].add_repulsors(level4_repulsors)
        
        # Level 5 repulsors (random)
        level5_repulsors = []
        for i in range(10):
            x = random.uniform(
                self.BORDER_THICKNESS + 30,
                self.WINDOW_WIDTH - self.BORDER_THICKNESS - 30
            )
            y = random.uniform(
                self.BORDER_THICKNESS + 30,
                self.WINDOW_HEIGHT - self.BORDER_THICKNESS - 30
            )
            level5_repulsors.append({
                "x": x,
                "y": y,
                "radius": 15,
                "color": self.YELLOW,
                "dx": random.uniform(-2, 2),
                "dy": random.uniform(-2, 2)
            })
        self.levels[4].add_repulsors(level5_repulsors)
    
    def reset_level(self):
        # Reset ball position
        self.ball.x = self.BORDER_THICKNESS + self.BALL_RADIUS + 20
        self.ball.y = self.WINDOW_HEIGHT // 2
        self.ball.stop()
        self.ball.teleporting = False
        
        # Set current level
        self.current_level_obj = self.levels[self.current_level - 1]
    
    def reset_game(self):
        self.current_level = 1
        self.timer_seconds = 135  # 2 minutes and 15 seconds
        self.game_over = False
        self.game_won = False
        self.reset_level()
    
    def update_timer(self):
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
        else:
            self.game_over = True
    
    def predict_trajectory(self):
        sim_x = self.ball.x
        sim_y = self.ball.y
        speed = (self.power_slider.value / self.MAX_POWER) * 15
        vel_x = speed * math.cos(math.radians(self.angle_slider.value))
        vel_y = -speed * math.sin(math.radians(self.angle_slider.value))
        points = [(sim_x, sim_y)]
        
        for _ in range(200):
            sim_x += vel_x
            sim_y += vel_y
            vel_x *= self.AIR_FRICTION_FACTOR
            vel_y *= self.AIR_FRICTION_FACTOR
            
            # Border collisions
            if sim_x - self.BALL_RADIUS < self.BORDER_THICKNESS:
                sim_x = self.BORDER_THICKNESS + self.BALL_RADIUS
                vel_x *= -0.8
            if sim_x + self.BALL_RADIUS > self.WINDOW_WIDTH - self.BORDER_THICKNESS:
                sim_x = self.WINDOW_WIDTH - self.BORDER_THICKNESS - self.BALL_RADIUS
                vel_x *= -0.8
            if sim_y - self.BALL_RADIUS < self.BORDER_THICKNESS:
                sim_y = self.BORDER_THICKNESS + self.BALL_RADIUS
                vel_y *= -0.8
            if sim_y + self.BALL_RADIUS > self.WINDOW_HEIGHT - self.BORDER_THICKNESS:
                sim_y = self.WINDOW_HEIGHT - self.BORDER_THICKNESS - self.BALL_RADIUS
                vel_y *= -0.8
            
            # Obstacle collisions
            for ox, oy, ow, oh in self.current_level_obj.get_all_obstacles():
                if (sim_x + self.BALL_RADIUS > ox and
                    sim_x - self.BALL_RADIUS < ox + ow and
                    sim_y + self.BALL_RADIUS > oy and
                    sim_y - self.BALL_RADIUS < oy + oh):
                    penetration_left = abs(sim_x + self.BALL_RADIUS - ox)
                    penetration_right = abs(sim_x - self.BALL_RADIUS - (ox + ow))
                    penetration_top = abs(sim_y + self.BALL_RADIUS - oy)
                    penetration_bottom = abs(sim_y - self.BALL_RADIUS - (oy + oh))
                    min_pen = min(
                        penetration_left,
                        penetration_right,
                        penetration_top,
                        penetration_bottom
                    )
                    if min_pen == penetration_left:
                        sim_x = ox - self.BALL_RADIUS
                        vel_x *= -0.8
                    elif min_pen == penetration_right:
                        sim_x = ox + ow + self.BALL_RADIUS
                        vel_x *= -0.8
                    elif min_pen == penetration_top:
                        sim_y = oy - self.BALL_RADIUS
                        vel_y *= -0.8
                    else:
                        sim_y = oy + oh + self.BALL_RADIUS
                        vel_y *= -0.8
            
            points.append((sim_x, sim_y))
            
            if abs(vel_x) < 0.1 and abs(vel_y) < 0.1:
                break
        
        return points
    
    def draw_aim_preview(self):
        points = self.predict_trajectory()
        total_len = 0
        for i in range(1, len(points)):
            x0, y0 = points[i-1]
            x1, y1 = points[i]
            total_len += math.hypot(x1 - x0, y1 - y0)
        
        if total_len == 0:
            return
        
        spacing = total_len / 15
        acc = 0
        next_d = spacing
        
        for i in range(1, len(points)):
            x0, y0 = points[i-1]
            x1, y1 = points[i]
            seg = math.hypot(x1 - x0, y1 - y0)
            while acc + seg >= next_d:
                ratio = (next_d - acc) / seg
                dx = x0 + ratio * (x1 - x0)
                dy = y0 + ratio * (y1 - y0)
                pygame.draw.circle(self.screen, self.ORANGE, (int(dx), int(dy)), 3)
                next_d += spacing
            acc += seg
    
    def draw_level_label(self):
        self.screen.blit(
            self.font.render(f"Level {self.current_level}", True, self.WHITE),
            (10, 5)
        )
    
    def draw_timer(self):
        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60
        
        # Make timer red when less than 30 seconds left
        color = self.RED if self.timer_seconds < 30 else self.WHITE
        
        timer_text = f"Timer: {minutes} min {seconds} sec"
        self.screen.blit(
            self.font.render(timer_text, True, color),
            (10, 30)
        )
    
    def draw_win_screen(self):
        # Draw dark overlay
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw win message
        win_text = "YOU WIN! CONGRATS!"
        text_surface = self.big_font.render(win_text, True, self.YELLOW)
        text_rect = text_surface.get_rect(center=(self.WINDOW_WIDTH//2, self.WINDOW_HEIGHT//2 - 50))
        self.screen.blit(text_surface, text_rect)
        
        # Draw play again button
        self.play_again_button.draw(self.screen)
    
    def draw_lose_screen(self):
        # Draw dark overlay
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw lose message
        lose_text = "TIME'S UP! YOU LOSE!"
        text_surface = self.big_font.render(lose_text, True, self.RED)
        text_rect = text_surface.get_rect(center=(self.WINDOW_WIDTH//2, self.WINDOW_HEIGHT//2 - 50))
        self.screen.blit(text_surface, text_rect)
        
        # Draw play again button
        self.play_again_button.draw(self.screen)
    
    def draw_pause_screen(self):
        # Draw dark overlay
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw pause text
        self.screen.blit(
            self.big_font.render("PAUSED", True, self.WHITE),
            (self.WINDOW_WIDTH//2 - 80, self.WINDOW_HEIGHT//2 - 80)
        )
        
        # Draw resume button
        self.resume_button.draw(self.screen)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_paused = not self.game_paused
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.game_over or self.game_won:
                    # Check if play again button was clicked
                    if self.play_again_button.is_clicked(mouse_pos):
                        self.reset_game()
                elif self.game_paused:
                    if self.resume_button.is_clicked(mouse_pos):
                        self.game_paused = False
                else:
                    # Angle slider
                    if self.angle_slider.handle_mouse_down(mouse_pos):
                        pass
                    # Power slider
                    elif self.power_slider.handle_mouse_down(mouse_pos):
                        pass
                    # Launch button
                    elif self.launch_button.is_clicked(mouse_pos):
                        if not self.ball.is_moving:
                            self.ball.launch(self.angle_slider.value, self.power_slider.value, self.MAX_POWER)
                        else:
                            self.ball.stop()
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.angle_slider.handle_mouse_up()
                self.power_slider.handle_mouse_up()
            
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                self.angle_slider.handle_mouse_motion(mouse_x)
                self.power_slider.handle_mouse_motion(mouse_x)
        
        return True
    
    def update(self, dt):
        if self.game_paused or self.game_over or self.game_won:
            return
        
        # Update timer (once per second)
        self.timer_counter += dt
        if self.timer_counter >= 1.0:
            self.update_timer()
            self.timer_counter = 0
        
        # Update current level
        self.current_level_obj.update(dt)
        
        # Update ball physics
        self.ball.update(dt)
        
        if self.ball.is_moving and not self.ball.teleporting:
            # Handle border collisions
            self.ball.handle_border_collision(
                self.BORDER_THICKNESS,
                self.WINDOW_WIDTH,
                self.WINDOW_HEIGHT
            )
            
            # Handle wall collisions
            for wall in self.current_level_obj.walls:
                self.ball.handle_obstacle_collision(wall.get_collision_rect())
            
            # Handle platform collisions
            for platform in self.current_level_obj.moving_platforms:
                self.ball.handle_platform_collision(platform)
            
            # Handle repulsor collisions
            for repulsor in self.current_level_obj.repulsors:
                self.ball.handle_repulsor_collision(repulsor, self.current_level)
            
            # Hole detection
            dx = self.current_level_obj.hole_x - self.ball.x
            dy = self.current_level_obj.hole_y - self.ball.y
            dist_to_hole = math.hypot(dx, dy)
            
            if dist_to_hole < self.HOLE_RADIUS * self.HOLE_CAPTURE_FACTOR:
                self.ball.teleporting = True
        
        # Handle teleporting to hole
        if self.ball.teleporting:
            if self.ball.teleport_to_hole(
                self.current_level_obj.hole_x,
                self.current_level_obj.hole_y,
                self.hole_sound
            ):
                self.ball.teleporting = False
                
                if self.current_level == self.TOTAL_LEVELS:
                    self.game_won = True
                else:
                    self.current_level += 1
                    self.reset_level()
    
    def draw(self):
        # Draw the course
        self.screen.fill(self.GREEN)
        
        # Draw borders
        pygame.draw.rect(
            self.screen, self.BROWN,
            (0, 0, self.WINDOW_WIDTH, self.BORDER_THICKNESS)
        )
        pygame.draw.rect(
            self.screen, self.BROWN,
            (0, self.WINDOW_HEIGHT - self.BORDER_THICKNESS, self.WINDOW_WIDTH, self.BORDER_THICKNESS)
        )
        pygame.draw.rect(
            self.screen, self.BROWN,
            (0, 0, self.BORDER_THICKNESS, self.WINDOW_HEIGHT)
        )
        pygame.draw.rect(
            self.screen, self.BROWN,
            (self.WINDOW_WIDTH - self.BORDER_THICKNESS, 0, self.BORDER_THICKNESS, self.WINDOW_HEIGHT)
        )
        
        # Draw level elements
        self.current_level_obj.draw(self.screen)
        
        # Draw aim preview
        if not self.ball.is_moving and not self.ball.teleporting:
            self.draw_aim_preview()
        
        # Draw ball
        self.ball.draw(self.screen)
        
        # Draw UI elements
        self.draw_level_label()
        self.draw_timer()
        
        if not self.ball.is_moving and not self.ball.teleporting:
            self.angle_slider.draw(self.screen)
            self.power_slider.draw(self.screen)
            
            # Update launch button text based on ball state
            self.launch_button.text = "GO!" if self.ball.is_moving else "Launch"
            self.launch_button.color = self.BROWN if self.ball.is_moving else self.BLUE
            self.launch_button.draw(self.screen)
        
        # Draw overlay screens
        if self.game_paused:
            self.draw_pause_screen()
        elif self.game_over:
            self.draw_lose_screen()
        elif self.game_won:
            self.draw_win_screen()
    
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            # Handle events
            running = self.handle_events()
            
            # Update game state
            self.update(dt)
            
            # Draw everything
            self.draw()
            
            # Update display
            pygame.display.flip()
        
        pygame.quit()

# Main entry point
if __name__ == "__main__":
    game = MiniGolfGame()
    game.run()
