import socket
from uuid import uuid4 as uuid

from enum import Enum
import pygame
import sys
from hockey.goal import Goal
from hockey.ball import Ball
from hockey.player import Player
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
    def __init__(self, width: int, height: int, server=False, address=None, port=None):
        pygame.init()
        self.server = server
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Goal Pong")
        self.clock = pygame.time.Clock()

        # entities
        self.player1 = Player(is_left=True)
        self.player2 = Player(is_left=False)
        self.ball = Ball()
        self.goal1 = Goal(PADDLE_PADDING - GOAL_PADDING + GOAL_W // 2, HEIGHT // 2, width=GOAL_W, height=GOAL_H, thickness=GOAL_T)
        # place right goal at symmetrical position
        right_goal_x = WIDTH - GOAL_PADDING - PADDLE_W
        self.goal2 = Goal(right_goal_x, HEIGHT // 2, width=GOAL_W, height=GOAL_H, thickness=GOAL_T, rotate=180)

        self.active_player = None

        self.address = address
        self.port = port

        self.sock = None
        self.score = (0, 0)
        self.font = pygame.font.SysFont(None, 48)

        if server:
            assert port, "Cannot instantiate server without port."
            self.active_player = self.player1
        else:
            assert address, "Cannot connect to game without address."
            assert port, "Cannot connect to game without port."
            self.active_player = self.player2

    def __encode_message(self, message: str) -> bytes:
        return f"{message}".encode()

    def connect(self, address: str, port: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (address, port)
        self.sock.connect(server_address)
        # initial handshake
        self.sock.sendall(self.__encode_message("start"))

    def capture_input(self) -> Action:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            return Action.QUIT
        if keys[pygame.K_UP]:
            return Action.MOVE_UP
        if keys[pygame.K_DOWN]:
            return Action.MOVE_DOWN
        return None

    def handle_input(self, action: Action):
        if action == Action.QUIT:
            self.quit()
            pygame.quit()
            sys.exit()

        if action == Action.MOVE_UP:
            self.active_player.move_up()
        elif action == Action.MOVE_DOWN:
            self.active_player.move_down()

        return None

    def parse_game_state(self, message: str):
        try:
            (player1_pos, ball_pos, score) = message.split("\n")
            (x, y) = player1_pos.split(" ")
            self.player1.x = float(x)
            self.player1.y = float(y)

            (x, y) = ball_pos.split(" ")
            self.ball.x = float(x)
            self.ball.y = float(y)

            (p1_score, p2_score) = score.split(" ")
            self.score = (int(p1_score), int(p2_score))
        except Exception:
            pass

    def create_game_state(self) -> str:
        message = f"{int(self.player1.x)} {int(self.player1.y)}\n"
        message += f"{int(self.ball.x)} {int(self.ball.y)}\n"
        message += f"{self.score[0]} {self.score[1]}"
        return message

    def update_game_state(self):
        pos_msg = f"pos {int(self.player2.x)} {int(self.player2.y)}"
        try:
            self.sock.sendall(self.__encode_message(pos_msg))
            data = self.sock.recv(1024).decode()
            if not data:
                self.quit()
                return
            self.parse_game_state(data)
        except (ConnectionResetError, ConnectionAbortedError):
            self.quit()

    def check_collisions(self):
        try:
            data = self.sock.recv(1024).decode()
        except Exception:
            self.quit()

        if not data:
            self.quit()

        if data.startswith("pos"):
            try:
                _, xs, ys = data.split()
                self.player2.x = float(xs)
                self.player2.y = float(ys)
            except Exception:
                pass

        self.ball.update()
        self.ball.check_wall_collision()

        self.ball.handle_paddle_collision(self.player1)
        self.ball.handle_paddle_collision(self.player2)

        def score_callback(scored_for_left_index):
            if scored_for_left_index == 1:
                self.score = (self.score[0], self.score[1] + 1)
            else:
                self.score = (self.score[0] + 1, self.score[1])

        self.ball.handle_goal_collision_and_score(self.goal1, self.goal2, score_callback)

    def render(self):
        self.screen.fill(Colors.BLUE.value)
        self.screen.blit(self.goal1.image, self.goal1.rect)
        self.screen.blit(self.goal2.image, self.goal2.rect)
        self.player1.render(self.screen)
        self.player2.render(self.screen)
        self.ball.render(self.screen)

        score_text = self.font.render(f"{self.score[0]}   {self.score[1]}", True, Colors.BLACK.value)
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

        pygame.display.flip()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

        action = self.capture_input()
        self.handle_input(action)

        if self.server:
            self.check_collisions()
            state_msg = self.create_game_state()
            try:
                self.sock.sendall(self.__encode_message(state_msg))
            except Exception:
                self.quit()
        else:
            self.update_game_state()

        self.render()
        self.clock.tick(60)

    def serve(self, port: int):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(("", port))
        server_sock.listen(1)
        print(f"[server] listening on port {port}...")
        conn, addr = server_sock.accept()
        print(f"[server] client connected: {addr}")
        self.sock = conn
        server_sock.close()

    def run(self):
        if self.server:
            self.serve(self.port)
        else:
            self.connect(self.address, self.port)

        while True:
            self.update()

    def quit(self):
        try:
            if self.sock:
                self.sock.close()
            pygame.quit()
            sys.exit()
        except Exception:
            pass
