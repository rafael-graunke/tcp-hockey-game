import pygame
from hockey.constants import (
    PADDLE_H,
    PADDLE_W,
    WIDTH,
    HEIGHT,
    PADDLE_PADDING,
    Colors,
)


class Player:
    def __init__(self, is_left: bool, speed: int = 7):
        x = PADDLE_PADDING if is_left else WIDTH - PADDLE_PADDING - PADDLE_W
        y = HEIGHT // 2 - PADDLE_H // 2
        self.rect = pygame.Rect(x, y, PADDLE_W, PADDLE_H)
        self.speed = speed
        self.is_left = is_left
        self.color = Colors.YELLOW.value

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

    def move_up(self):
        self.rect.y -= self.speed
        if self.rect.top < 0:
            self.rect.top = 0

    def move_down(self):
        self.rect.y += self.speed
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def render(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.color, self.rect)
