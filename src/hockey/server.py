from hockey.game import Game

game = Game(800, 600, server=True, port=8080)
game.run()
