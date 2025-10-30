import pygame
import random
from hockey.constants import Colors

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y, width=40, height=200, thickness=10, rotate=0):
        super().__init__()
        self.width = width
        self.height = height
        self.thickness = thickness
        self.pos = (x, y)
        self.rotate = rotate

        self.original_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._draw_outer_shape(self.original_image)
        self.original_inner_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.original_inner_surf, (255, 255, 255),
                         (self.thickness, self.thickness,
                          self.width - self.thickness,
                          self.height - 2*self.thickness))

        self.image = pygame.transform.rotate(self.original_image, self.rotate)
        self.inner_surf = pygame.transform.rotate(self.original_inner_surf, self.rotate)
        self.rect = self.image.get_rect(center=(x, y))

        self.outer_mask = pygame.mask.from_surface(self.image)
        self.inner_mask = pygame.mask.from_surface(self.inner_surf)

    def _draw_outer_shape(self, surf):
        pygame.draw.rect(surf, Colors.BLACK.value, (0, 0, self.thickness, self.height))
        pygame.draw.rect(surf, Colors.BLACK.value, (0, 0, self.width, self.thickness))
        pygame.draw.rect(surf, Colors.BLACK.value, (0, self.height - self.thickness, self.width, self.thickness))

    def check_bounce(self, ball_mask, ball_pos):
        offset = (int(ball_pos[0] - self.rect.x), int(ball_pos[1] - self.rect.y))
        return self.outer_mask.overlap(ball_mask, offset) is not None

    def check_score(self, ball_mask, ball_pos):
        offset = (int(ball_pos[0] - self.rect.x), int(ball_pos[1] - self.rect.y))
        return self.inner_mask.overlap(ball_mask, offset) is not None

    def bounce_ball(self, ball_rect, ball_speed, ball_mask):
        """Bounce the ball off the outer goal mask accurately."""
        offset = (int(ball_rect.x - self.rect.x), int(ball_rect.y - self.rect.y))
        collision_point = self.outer_mask.overlap(ball_mask, offset)
        if collision_point:
            # Determine side of collision
            rel_x = collision_point[0]
            rel_y = collision_point[1]

            # If collision near vertical edges (left/right of goal frame)
            if rel_x < self.thickness or rel_x > self.width - self.thickness:
                ball_speed[0] *= -1  # bounce horizontally
            # If collision near top/bottom edges
            elif rel_y < self.thickness or rel_y > self.height - self.thickness:
                ball_speed[1] *= -1  # bounce vertically
            else:
                # fallback: invert horizontal by default
                ball_speed[0] *= -1
            # Optional: add small randomness
            ball_speed[0] += random.uniform(-0.5, 0.5)
            ball_speed[1] += random.uniform(-0.5, 0.5)
