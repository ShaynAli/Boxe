import pynput

import entities

import collections
import contextlib
import itertools
import os
import threading
import time


class TixeException(Exception):
    pass


class InvalidMove(TixeException):
    pass


class Controller:

    def __init__(self, on_exit, on_error, move_up, move_down, move_left, move_right):
        self.kb_listener = pynput.keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        keys = pynput.keyboard.Key
        self.key_press_map = {
            keys.esc: on_exit,
            keys.up: move_up,
            keys.down: move_down,
            keys.left: move_left,
            keys.right: move_right}
        self.on_error = on_error

    def run(self):
        with self.kb_listener:
            try:
                self.kb_listener.join()
            except Exception:
                self.on_error()
                print('Encountered exception in input thread')
                raise

    def stop(self):
        self.kb_listener.stop()

    def on_press(self, key):
        with contextlib.suppress(KeyError):
            self.key_press_map[key]()

    def on_release(self, key):
        pass


class Level:
    static_map = {
        'w': entities.Wall,
        ' ': entities.Empty}

    spawn_map = {
        'p': entities.Player,
        '.': entities.Empty}

    _can_enter = {
        entities.Player: {
            entities.Wall: False,  # The player cannot enter walls
            entities.Empty: True  # The player can enter empty spaces
        }}

    def __init__(self, path):

        # Load layers
        level_spawns_file = os.path.join(path, 'spawns')
        level_static_file = os.path.join(path, 'static')
        level_spawns = Level.load_layer(level_spawns_file, layer_type='spawns')
        level_static = Level.load_layer(level_static_file, layer_type='static')

        if len(level_spawns) != len(level_static):
            raise TixeException('Layer size mismatch')

        # Initialize entities
        self.actor_layer = [[e() for e in row] for row in level_spawns]
        self.terrain_layer = [[e() for e in row] for row in level_static]

        # Record actor locations
        self.actor_location = {e: (row_i, col_i)
                               for row_i, row in enumerate(self.actor_layer)
                               for col_i, e in enumerate(row)}
        self.actors = collections.defaultdict(list, {type(e): e for e in itertools.chain.from_iterable(self.actor_layer)})

        self.player = next(actor for actor in itertools.chain.from_iterable(self.actor_layer)
                           if isinstance(actor, entities.Player))

        self.level = self.merge_layers()

    @staticmethod
    def load_layer(file, layer_type):

        if layer_type == 'static':
            layer_map = Level.static_map
        elif layer_type == 'spawns':
            layer_map = Level.spawn_map
        else:
            raise TixeException(f'Invalid layer type {layer_type}')

        with open(file, 'r') as layer_file:
            return [[layer_map[e] for e in row] for row in layer_file.read().split('\n')]

    def merge_layers(self):
        return [[actor_e or level_e for actor_e, level_e in zip(actor_row, level_row)]
                for actor_row, level_row in zip(self.actor_layer, self.terrain_layer)]

    def update(self):
        self.level = self.merge_layers()

    # region Entity movement

    @staticmethod
    def can_enter(actor, entity):
        return Level._can_enter[type(actor)][type(entity)]

    def _move(self, actor, row_offset=0, col_offset=0):

        row, col = self.actor_location[actor]
        other_row = (row + row_offset) % len(self.actor_layer)
        other_col = (col + col_offset) % len(self.actor_layer[other_row])

        other_actor = self.actor_layer[other_row][other_col]
        terrain = self.terrain_layer[other_row][other_col]

        if other_actor or not Level.can_enter(actor, terrain):
            raise InvalidMove(f'Cannot move {actor} into {other_actor or terrain} at {(other_row, other_col)}')

        self.actor_location[actor] = (other_row, other_col)
        self.actor_layer[other_row][other_col] = actor
        self.actor_layer[row][col] = entities.Empty()

    def move_up(self, actor):
        self._move(actor, row_offset=-1)

    def move_down(self, actor):
        self._move(actor, row_offset=1)

    def move_left(self, actor):
        self._move(actor, col_offset=-1)

    def move_right(self, actor):
        self._move(actor, col_offset=1)

    # endregion


class Game:

    def __init__(self):
        self.controller = Controller(
            on_exit=self.exit,
            on_error=self.on_error,
            move_up=self.move_up,
            move_down=self.move_down,
            move_left=self.move_left,
            move_right=self.move_right)
        self.level = Level(path=os.path.join('levels', '001'))
        self.running = True
        self.rendering = True

    def run(self):
        input_thread = threading.Thread(target=self.controller.run, daemon=True)
        input_thread.start()
        os.system('cls')
        while self.running:
            self.level.update()
            if self.rendering:
                print('\033[0;0H'  # Reset cursor position to (0, 0)
                      + '\n'.join(''.join(repr(e) for e in row) for row in self.level.level), end='')
            time.sleep(0.01)
        os.system('cls')

    def exit(self):
        self.running = False

    def on_error(self):
        self.rendering = False

    # region Player movement

    def move_up(self):
        with contextlib.suppress(InvalidMove):
            self.level.move_up(self.level.player)

    def move_down(self):
        with contextlib.suppress(InvalidMove):
            self.level.move_down(self.level.player)

    def move_left(self):
        with contextlib.suppress(InvalidMove):
            self.level.move_left(self.level.player)

    def move_right(self):
        with contextlib.suppress(InvalidMove):
            self.level.move_right(self.level.player)

    # endregion


if __name__ == '__main__':
    game = Game()
    game.run()
