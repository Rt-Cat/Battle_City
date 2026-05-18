from game.map_manager import MapManager

class Map:
    def __init__(self, level_index=0):
        self.walls = set()
        level = MapManager.get_level(level_index)
        
        self.name = level['name']
        self.width = level['width']
        self.height = level['height']
        self.player_start = level['player_start']
        self.enemy_spawns = level['enemy_spawns']
        
        layout = level['layout']
        for y, row in enumerate(layout):
            for x, char in enumerate(row):
                if char == '#':
                    self.walls.add((x, y))

    def is_wall(self, x, y):
        return (x, y) in self.walls

    def destroy_wall(self, x, y):
        if (x, y) in self.walls:
            self.walls.remove((x, y))
            return True
        return False
    
    def is_out_of_bounds(self, x, y):
        return not (0 <= x < self.width and 0 <= y < self.height)