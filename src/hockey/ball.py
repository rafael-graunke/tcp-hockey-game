import pygame
import random
from hockey.goal import Goal
from hockey.player import Player

from hockey.constants import (
    WIDTH,
    HEIGHT,
    Colors,
)

class Ball:
    def __init__(self, size: int = 30):
        self.size = size
        self.rect = pygame.Rect(WIDTH // 2 - size // 2, HEIGHT // 2 - size // 2, size, size)
        self.speed = [random.choice([-5, 5]), random.choice([-3, 3])]
        self.surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(self.surf, Colors.BLACK.value, (0, 0, size, size))
        self.mask = pygame.mask.from_surface(self.surf)

    @property
    def x(self):
        return float(self.rect.x)

    @x.setter
    def x(self, value):
        self.rect.x = int(value)

    @property
    def y(self):
        return float(self.rect.y)

    @y.setter
    def y(self, value):
        self.rect.y = int(value)

    def update(self):
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]

    def check_wall_collision(self):
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed[1] *= -1
            self.speed[0] += random.uniform(-0.3, 0.3)

    def _randomize_bounce(self):
        self.speed[0] *= -1
        self.speed[0] += random.uniform(-1, 1)
        self.speed[1] += random.uniform(-1, 1)
        mag = (self.speed[0] ** 2 + self.speed[1] ** 2) ** 0.5
        if mag == 0:
            mag = 1
        scale = random.uniform(5, 7) / mag
        self.speed[0] *= scale
        self.speed[1] *= scale

    def handle_paddle_collision(self, player: Player):
        if self.rect.colliderect(player.rect):
            self._randomize_bounce()
            if self.rect.centerx < player.rect.centerx:
                self.rect.left = player.rect.left - self.rect.width
            else:
                self.rect.right = player.rect.right + self.rect.width

    def handle_goal_collision_and_score(self, goal_left: Goal, goal_right: Goal, score_callback):
        goal_left.bounce_ball(self.rect, self.speed, self.mask)
        goal_right.bounce_ball(self.rect, self.speed, self.mask)

        if goal_left.check_score(self.mask, (self.rect.x, self.rect.y)):
            score_callback(1)
            self.reset()
            return

        if goal_right.check_score(self.mask, (self.rect.x, self.rect.y)):
            score_callback(0)
            self.reset()
            return

        if self.rect.left <= 0 and not goal_left.check_score(self.mask, (self.rect.x, self.rect.y)):
            self.speed[0] *= -1
        if self.rect.right >= WIDTH and not goal_right.check_score(self.mask, (self.rect.x, self.rect.y)):
            self.speed[0] *= -1

    def reset(self):
        self.rect.x = WIDTH // 2 - self.size // 2
        self.rect.y = HEIGHT // 2 - self.size // 2
        self.speed = [random.choice([-5, 5]), random.choice([-3, 3])]

    def render(self, screen: pygame.Surface):
        screen.blit(self.surf, (self.rect.x, self.rect.y))

