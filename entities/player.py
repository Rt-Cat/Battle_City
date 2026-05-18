from entities.tank import Tank

class Player(Tank):
    def __init__(self, x, y):
        super().__init__(x, y, 'w', is_player=True)
        self.shoot_cooldown = 0
        
    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1