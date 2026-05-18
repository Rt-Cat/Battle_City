class Bullet:
    def __init__(self, x, y, dx, dy, is_player):
        self.x = x
        self.y = y
        self.last_x = x
        self.last_y = y
        self.dx = dx
        self.dy = dy
        self.is_player = is_player

    def move(self):
        self.last_x = self.x
        self.last_y = self.y
        self.x += self.dx
        self.y += self.dy