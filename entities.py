class Entity:

    def __init__(self, symbol):
        self.symbol = symbol

    def __repr__(self):
        return self.symbol


class Wall(Entity):

    def __init__(self):
        super().__init__(symbol='██')


class Empty(Entity):

    def __init__(self):
        super().__init__(symbol='  ')

    def __bool__(self):
        return False


class Player(Entity):

    def __init__(self):
        super().__init__(symbol='\033[92m██\033[0m')
