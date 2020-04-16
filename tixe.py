import pynput
import os

import time


exit_keys = {
    pynput.keyboard.Key.esc
}

EMPTY = ' '
PLAYER = '\033[92m█\033[0m'


class Position:

    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __iter__(self):
        yield self.row
        yield self.col


class Game:

    def __init__(self):
        self.board = [[EMPTY for _ in range(10)] for _ in range(10)]
        self.character_pos = Position(5, 5)
        self.ready_to_exit = False
        self.update_board = True
        self.key_map = {
            pynput.keyboard.Key.up: self.move_up,
            pynput.keyboard.Key.left: self.move_left,
            pynput.keyboard.Key.down: self.move_down,
            pynput.keyboard.Key.right: self.move_right}

    def refresh_board(self):
        self.board = [[EMPTY for _ in range(80)] for _ in range(40)]
        self.board[self.character_pos.row][self.character_pos.col] = PLAYER

    def render_board(self):
        os.system('cls')  # TODO: Use alternate solution to reduce re-drawing time
        print('\n'.join(''.join(row) for row in self.board))

    def run(self):
        while not self.ready_to_exit:
            if self.update_board:
                self.refresh_board()
                self.render_board()
            time.sleep(0.05)

    def move_up(self):
        self.character_pos.row = max(self.character_pos.row - 1, 0)

    def move_down(self):
        self.character_pos.row = min(self.character_pos.row + 1, len(self.board) - 1)

    def move_left(self):
        self.character_pos.col = max(self.character_pos.col - 1, 0)

    def move_right(self):
        self.character_pos.col = min(self.character_pos.col + 1, len(self.board[self.character_pos.row]) - 1)

    def on_press(self, key):
        if key in exit_keys:
            self.ready_to_exit = True
        try:
            self.key_map[key]()
        except KeyError:
            pass

    def on_release(self, key):
        pass


if __name__ == '__main__':

    game = Game()

    kb_listener = pynput.keyboard.Listener(on_press=game.on_press, on_release=game.on_release)
    kb_listener.start()

    game.run()
