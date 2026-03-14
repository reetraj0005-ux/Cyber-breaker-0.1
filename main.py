import pygame
import random
import math
import os

# --- Setup ---
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
clock = pygame.time.Clock()

# Colors
BLACK = (10, 10, 25)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
COLORS = [(0, 255, 255), (255, 20, 147), (50, 255, 50), (255, 255, 0)]

# --- Game States ---
MENU = 0
PLAYING = 1

class Ball:
    def __init__(self, x, y):
        self.radius = 12
        self.x, self.y = x, y
        self.vx, self.vy = 0, 0
        self.active = False
        self.rect = pygame.Rect(x-12, y-12, 24, 24)

    def launch(self, angle, speed=15):
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.active = True

    def update(self):
        if self.active:
            self.x += self.vx
            self.y += self.vy
            self.rect.center = (self.x, self.y)
            if self.x <= self.radius or self.x >= WIDTH - self.radius:
                self.vx *= -1
            if self.y <= self.radius:
                self.vy *= -1

class Brick:
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)
        self.alive = True
        self.color = random.choice(COLORS)

    def draw(self, surf):
        if self.alive:
            pygame.draw.rect(surf, self.color, self.rect, border_radius=4)

class CyberBreakerAI:
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 30, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 60, bold=True)
        self.score = 0
        self.level = 1
        self.state = MENU
        
        # --- IMAGE LOADING ---
        # Replace 'start_button.png' with your actual filename
        try:
            self.start_img = pygame.image.load("start_button.png").convert_alpha()
            # Scale image to a reasonable size (e.g., 300x100)
            self.start_img = pygame.transform.scale(self.start_img, (300, 100))
            self.start_rect = self.start_img.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
        except:
            print("Image not found! Using a placeholder rectangle.")
            self.start_img = None
            self.start_rect = pygame.Rect(WIDTH//2-150, HEIGHT//2+50, 300, 100)

        self.ball = Ball(WIDTH // 2, HEIGHT - 150)
        self.bricks = []
        self.is_dragging = False
        self.aim_angle = 0
        self.brick_size = 22
        self.generate_ai_map()

    def generate_ai_map(self):
        self.bricks = []
        cx, cy = WIDTH // 2, 300
        shape_type = random.choice(["heart", "diamond", "circle"])
        for y in range(120, 500, self.brick_size + 4):
            for x in range(50, WIDTH - 50, self.brick_size + 4):
                nx, ny = (x - cx) / 150, (y - cy) / 150
                is_inside = False
                if shape_type == "heart":
                    is_inside = (nx**2 + (ny - math.sqrt(abs(nx)))**2) < 1.0
                elif shape_type == "diamond":
                    is_inside = (abs(nx) + abs(ny)) < 1.0
                elif shape_type == "circle":
                    is_inside = (nx**2 + ny**2) < 0.8
                if is_inside:
                    self.bricks.append(Brick(x, y, self.brick_size))

    def draw_menu(self):
        screen.fill(BLACK)
        title_txt = self.title_font.render("CYBER BREAKER", True, CYAN)
        screen.blit(title_txt, (WIDTH//2 - title_txt.get_width()//2, HEIGHT//2 - 100))
        
        # --- DRAW IMAGE BUTTON ---
        if self.start_img:
            # Pulsing effect for the image
            alpha = 150 + abs(math.sin(pygame.time.get_ticks() * 0.005)) * 105
            self.start_img.set_alpha(alpha)
            screen.blit(self.start_img, self.start_rect)
        else:
            # Fallback if image fails to load
            pygame.draw.rect(screen, CYAN, self.start_rect, 2)
            msg = self.font.render("START GAME", True, WHITE)
            screen.blit(msg, (self.start_rect.centerx - msg.get_width()//2, self.start_rect.centery - msg.get_height()//2))

    def run(self):
        running = True
        while running:
            m_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == MENU:
                        # Only start if clicking on the image area
                        if self.start_rect.collidepoint(m_pos):
                            self.state = PLAYING
                    elif not self.ball.active:
                        self.is_dragging = True
                
                if event.type == pygame.MOUSEBUTTONUP and self.is_dragging:
                    self.is_dragging = False
                    self.ball.launch(self.aim_angle)

            if self.state == MENU:
                self.draw_menu()
            else:
                self.update_game(m_pos)
                self.draw_game()

            pygame.display.flip()
            clock.tick(FPS)

    def update_game(self, m_pos):
        if self.is_dragging:
            dx, dy = m_pos[0] - self.ball.x, m_pos[1] - self.ball.y
            self.aim_angle = math.atan2(dy, dx)
        if self.ball.active:
            self.ball.update()
            for brk in self.bricks:
                if brk.alive and self.ball.rect.colliderect(brk.rect):
                    if abs(self.ball.rect.centerx - brk.rect.centerx) > abs(self.ball.rect.centery - brk.rect.centery):
                        self.ball.vx *= -1
                    else:
                        self.ball.vy *= -1
                    brk.alive = False
                    self.score += 10
                    break
            if self.ball.y > HEIGHT:
                self.ball.active = False
                self.ball.x, self.ball.y = WIDTH // 2, HEIGHT - 150
            if not any(brk.alive for brk in self.bricks):
                self.level += 1
                self.ball.active = False
                self.ball.x, self.ball.y = WIDTH // 2, HEIGHT - 150
                self.generate_ai_map()

    def draw_game(self):
        screen.fill(BLACK)
        for brk in self.bricks: brk.draw(screen)
        pygame.draw.circle(screen, WHITE, (int(self.ball.x), int(self.ball.y)), self.ball.radius)
        if self.is_dragging:
            for i in range(1, 8):
                px = self.ball.x + math.cos(self.aim_angle) * (i * 30)
                py = self.ball.y + math.sin(self.aim_angle) * (i * 30)
                pygame.draw.circle(screen, (100, 100, 100), (int(px), int(py)), 2)
        score_txt = self.font.render(f"SCORE: {self.score}", True, (255, 255, 0))
        level_txt = self.font.render(f"LVL: {self.level}", True, WHITE)
        screen.blit(score_txt, (40, 20))
        screen.blit(level_txt, (WIDTH - 140, 20))

if __name__ == "__main__":
    CyberBreakerAI().run()
