import random
from entities.tank import Tank

class Enemy(Tank):
    def __init__(self, x, y):
        super().__init__(x, y, 's', is_player=False)
        self.action_timer = 0
        self.shoot_timer = random.randint(10, 20)
        self.prev_step_x = x
        self.prev_step_y = y

    def can_see_player(self, player, game_map, all_tanks):
        if self.x != player.x and self.y != player.y:
            return False
            
        walls_between = 0
        enemies_between = 0
        
        if self.x == player.x:
            ymin, ymax = min(self.y, player.y), max(self.y, player.y)
            for y in range(ymin + 1, ymax):
                if game_map.is_wall(self.x, y): 
                    walls_between += 1
                if any(t.x == self.x and t.y == y and not t.is_player for t in all_tanks):
                    enemies_between += 1
        else:
            xmin, xmax = min(self.x, player.x), max(self.x, player.x)
            for x in range(xmin + 1, xmax):
                if game_map.is_wall(x, self.y): 
                    walls_between += 1
                if any(t.y == self.y and t.x == x and not t.is_player for t in all_tanks):
                    enemies_between += 1
                    
        return walls_between <= 1 and enemies_between == 0

    def get_dir_towards(self, target):
        if self.x == target.x:
            return 'w' if self.y > target.y else 's'
        return 'a' if self.x > target.x else 'd'

    def update(self, game_map, all_tanks):
        player = next((t for t in all_tanks if t.is_player), None)
        
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
            
        if player and player.is_alive and self.can_see_player(player, game_map, all_tanks):
            self.direction = self.get_dir_towards(player)
            if self.shoot_timer <= 0:
                self.shoot_timer = 15  
                return self.shoot()
            return None 

        self.action_timer -= 1
        if self.action_timer <= 0:
            self.action_timer = random.randint(5, 15)
            dirs = ['w', 'a', 's', 'd']
            random.shuffle(dirs)
            
            moved = False
            for d in dirs:
                dx, dy = self.get_dir_offsets(d)
                nx, ny = self.x + dx, self.y + dy
                
                if not game_map.is_out_of_bounds(nx, ny) and not game_map.is_wall(nx, ny):
                    if not any(t.x == nx and t.y == ny for t in all_tanks):
                        if (nx, ny) != (self.prev_step_x, self.prev_step_y) or random.random() < 0.2:
                            self.prev_step_x, self.prev_step_y = self.x, self.y
                            self.move(d, game_map, all_tanks)
                            moved = True
                            break
                            
            if not moved:
                for d in dirs:
                    dx, dy = self.get_dir_offsets(d)
                    nx, ny = self.x + dx, self.y + dy
                    if not game_map.is_out_of_bounds(nx, ny) and game_map.is_wall(nx, ny):
                        self.direction = d
                        if self.shoot_timer <= 0:
                            self.shoot_timer = 20  
                            return self.shoot()
                        break 
        return None