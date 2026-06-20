from entities.bullet import Bullet

class Tank:
    def __init__(self, x, y, direction, is_player=False):
        self.x = x
        self.y = y
        self.last_x = x
        self.last_y = y
        self.direction = direction
        self.is_alive = True
        self.is_player = is_player

    def get_dir_offsets(self, direction):
        offsets = {'w': (0, -1), 's': (0, 1), 'a': (-1, 0), 'd': (1, 0)}
        return offsets.get(direction, (0, 0))

    def save_history(self):
        self.last_x = self.x
        self.last_y = self.y

    def rotate(self, direction):
        self.direction = direction

    def move(self, direction, game_map, tanks):
        self.direction = direction
        dx, dy = self.get_dir_offsets(direction)
        nx, ny = self.x + dx, self.y + dy

        if game_map.is_out_of_bounds(nx, ny): return False
        if game_map.is_wall(nx, ny): return False
        for t in tanks:
            if t is not self and t.is_alive and t.x == nx and t.y == ny:
                return False
        
        self.x = nx
        self.y = ny
        return True

    def shoot(self):
        dx, dy = self.get_dir_offsets(self.direction)
        return Bullet(self.x, self.y, dx, dy, self.is_player)