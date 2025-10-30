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
        return f"{message}\n".encode()

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

    def update(self):
        action = self.capture_input()
        self.handle_input(action)
        self.check_collisions()
        self.ball.update()
        self.player1.update()
        self.player2.update()

    def serve(self, port: int):
        ...

    def run(self):
        if self.server:
            self.serve(self.port)
        while True:
            self.update()

    def quit(self):
        self.sock.close()
        
