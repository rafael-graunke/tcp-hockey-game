import socket
from uuid import uuid4 as uuid

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
    def __init__(self, width: int, height: int, server=False, address=None, port=None):
        pygame.init()
        self.server = server
        self.screen = pygame.display.set_mode((width, height))

        self.ball = None
        self.player1 = None
        self.player2 = None
        self.goal1 = None
        self.goal2 = None
        self.active_player = None

        self.address = address
        self.port = port
        
        if server:
            assert port, "Cannot instantiate server without port."
            self.active_player = self.player1
        else:
            assert port, "Cannot connect to game without address."
            assert port, "Cannot connect to game without port."
            self.active_player = self.player2             

    def __encode_message(self, message: str) -> bytes:
        return f"{message}".encode()

    def connect(self, address: str, port: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (address, port)
        self.sock.connect(server_address)
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
        if action == Action.MOVE_UP:
            return Action.MOVE_UP
        if action == Action.MOVE_DOWN:
            return Action.MOVE_DOWN
        return None

    def parse_game_state(self, message: str):
        ...

    def create_game_state(self):
        message = f"{self.active_player.x} {self.active_player.x}\n"
        message += f"{self.ball.x} {self.ball.y}\n"
        message += f"{self.score[0]} {self.score[1]}"

    def get_game_state(self):
        self.__encode_message("update")
        message = self.sock.recv(1024).decode()
        (player1_pos, ball_pos, score) = message.split("\n")

        (x, y) = player1_pos.split(" ")
        self.player1.x = float(x)
        self.player1.y = float(y)

        (x, y) = ball_pos.split(" ")
        self.ball.x = float(x)
        self.ball.y = float(y)

        (p1_score, p2_score) = score.split(" ")
        self.score = (int(p1_score), int(p2_score))

    def check_collisions(self):
        ...

    def render(self):
        ...

    def update(self):
        action = self.capture_input()
        self.handle_input(action)

        if self.server:
            self.check_collisions()

        else:
            self.update_game_state()

        self.ball.render()
        self.player1.render()
        self.player2.render()
        self.render()

    def serve(self, port: int):
        ...

    def run(self):
        if self.server:
            self.serve(self.port)
        else:
            self.connect(self.port)

        while True:
            self.update()

    def quit(self):
        self.sock.close()
