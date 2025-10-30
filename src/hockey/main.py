from enum import Enum
import pygame
import sys
import random
from hockey.goal import Goal
from hockey.constants import (
    PADDLE_H,
    PADDLE_W,
    GOAL_H,
    GOAL_T,
    GOAL_W,
    WIDTH,
    HEIGHT,
    PADDLE_PADDING,
    GOAL_PADDING,
    Colors,
)

class Action(Enum):
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    QUIT = "quit"

class Game:
    def __init__(self, width: int, height: int):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.ball = None
        self.player1 = None
        self.player2 = None
        self.goal1 = None
        self.goal2 = None

    def check_collisions(self):
        ...

    def capture_input(self) -> Action:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            return Action.QUIT
        if keys[pygame.K_UP] and right_paddle.top > 0:
            return Action.MOVE_UP
        if keys[pygame.K_DOWN] and right_paddle.bottom < HEIGHT:
            return Action.MOVE_DOWN
        return None

    def handle_input(self) -> Action:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            return Action.QUIT
        if keys[pygame.K_UP] and right_paddle.top > 0:
            return Action.MOVE_UP
        if keys[pygame.K_DOWN] and right_paddle.bottom < HEIGHT:
            return Action.MOVE_DOWN
        return None

    def update(self):
        action = self.capture_input()
        self.handle_input(action)
        self.check_collisions()

    def serve(self, port: int):
        ...

    def run(self):
        while True:
            self.update()

    def quit(self):
        ...

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Goal Pong")
clock = pygame.time.Clock()

left_paddle = pygame.Rect(PADDLE_PADDING, HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
right_paddle = pygame.Rect(
    WIDTH - PADDLE_PADDING - PADDLE_W, HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H
)


left_goal = Goal(120, HEIGHT // 2, width=GOAL_W, height=GOAL_H, thickness=GOAL_T)
right_goal = Goal(
    WIDTH - GOAL_PADDING - PADDLE_W, HEIGHT // 2, width=GOAL_W, height=GOAL_H, thickness=GOAL_T, rotate=180
)

ball_size = 30
ball = pygame.Rect(
    WIDTH // 2 - ball_size // 2, HEIGHT // 2 - ball_size // 2, ball_size, ball_size
)
ball_speed = [random.choice([-5, 5]), random.choice([-3, 3])]

score_left, score_right = 0, 0
font = pygame.font.SysFont(None, 48)

ball_surf = pygame.Surface((ball_size, ball_size), pygame.SRCALPHA)
pygame.draw.ellipse(ball_surf, Colors.BLACK.value, (0, 0, ball_size, ball_size))
ball_mask = pygame.mask.from_surface(ball_surf)


def randomize_bounce(speed):
    speed[0] *= -1
    speed[0] += random.uniform(-1, 1)
    speed[1] += random.uniform(-1, 1)
    mag = (speed[0] ** 2 + speed[1] ** 2) ** 0.5
    scale = random.uniform(5, 7) / mag
    speed[0] *= scale
    speed[1] *= scale


# --- Main loop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    ball.x += ball_speed[0]
    ball.y += ball_speed[1]

    # --- Wall collision ---
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed[1] *= -1
        ball_speed[0] += random.uniform(-0.3, 0.3)

    # --- Paddle collision ---
    if ball.colliderect(left_paddle):
        randomize_bounce(ball_speed)
        if ball.centerx < left_paddle.centerx:
            ball.left = left_paddle.left - ball.width
        else:
            ball.right = left_paddle.right + ball.width
    if ball.colliderect(right_paddle):
        randomize_bounce(ball_speed)
        if ball.centerx > right_paddle.centerx:
            ball.right = right_paddle.right + ball.width
        else:
            ball.left = right_paddle.left - ball.width

    left_goal.bounce_ball(ball, ball_speed, ball_mask)
    right_goal.bounce_ball(ball, ball_speed, ball_mask)

    if left_goal.check_score(ball_mask, (ball.x, ball.y)):
        score_right += 1
        ball.x, ball.y = WIDTH // 2, HEIGHT // 2
        ball_speed = [random.choice([-5, 5]), random.choice([-3, 3])]
    if right_goal.check_score(ball_mask, (ball.x, ball.y)):
        score_left += 1
        ball.x, ball.y = WIDTH // 2, HEIGHT // 2
        ball_speed = [random.choice([-5, 5]), random.choice([-3, 3])]

    # --- Side wall bounce ---
    if ball.left <= 0 and not left_goal.check_score(ball_mask, (ball.x, ball.y)):
        ball_speed[0] *= -1
    if ball.right >= WIDTH and not right_goal.check_score(ball_mask, (ball.x, ball.y)):
        ball_speed[0] *= -1

    # --- Draw ---
    screen.fill(Colors.BLUE.value)
    screen.blit(left_goal.image, left_goal.rect)
    screen.blit(right_goal.image, right_goal.rect)
    pygame.draw.rect(screen, Colors.YELLOW.value, left_paddle)
    pygame.draw.rect(screen, Colors.YELLOW.value, right_paddle)
    screen.blit(ball_surf, (ball.x, ball.y))

    score_text = font.render(f"{score_left}   {score_right}", True, Colors.BLACK.value)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

    pygame.display.flip()
    clock.tick(60)
