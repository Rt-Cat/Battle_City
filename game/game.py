import time
import constants as c
from game.map import Map
from game.input_handler import get_input
from entities.player import Player
from entities.enemy import Enemy
from utils.renderer import Renderer

class Game:
    def __init__(self, level_index=0):
        self.game_map = Map(level_index=level_index)
        self.renderer = Renderer()
        
        self.player = Player(self.game_map.player_start['x'], self.game_map.player_start['y'])
        self.enemies = [Enemy(s['x'], s['y']) for s in self.game_map.enemy_spawns]
            
        self.bullets = []
        self.explosions = []
        self.running = True
        self.message = ""

    def run(self):
        get_input() 
        while self.running:
            self.update()
            self.renderer.render_game(self.game_map, self.player, self.enemies, self.bullets, self.explosions, self.message)
            time.sleep(c.FPS)
            if self.message and not self.running:
                time.sleep(2) 

    def update(self):
        self._sync_history()
        self._update_explosions()
        self._process_input()
        self._update_enemies()
        self._update_bullets()
        self._check_win_condition()

    # ==========================================
    # Допоміжні методи циклу (Інкапсуляція ООП)
    # ==========================================
    
    def _sync_history(self):
        all_tanks = [self.player] + self.enemies
        for t in all_tanks:
            t.save_history()

    def _update_explosions(self):
        for exp in self.explosions[:]:
            exp['timer'] -= 1
            if exp['timer'] <= 0:
                self.explosions.remove(exp)

    def _process_input(self):
        key = get_input()
        all_tanks = [self.player] + self.enemies

        if key == 'q':
            self.running = False
            self.message = "Гру завершено."
        elif key in ['w', 'a', 's', 'd']:
            self.player.move(key, self.game_map, all_tanks)
        elif key in ['up', 'down', 'left', 'right']:
            dir_map = {'up': 'w', 'down': 's', 'left': 'a', 'right': 'd'}
            self.player.rotate(dir_map[key])
        elif key == ' ':
            if self.player.shoot_cooldown <= 0:
                self.bullets.append(self.player.shoot())
                self.player.shoot_cooldown = 3
        
        self.player.update()

    def _update_enemies(self):
        all_tanks = [self.player] + self.enemies
        for enemy in self.enemies:
            bullet = enemy.update(self.game_map, all_tanks)
            if bullet:
                self.bullets.append(bullet)

    def _update_bullets(self):
        for b in self.bullets[:]:
            if b not in self.bullets: continue  # Снаряд вже знищено в цьому тіку

            b.move()
            
            if self._check_out_of_bounds(b): continue
            if self._check_wall_collision(b): continue
            if self._check_bullet_collision(b): continue
            if self._check_tank_collision(b): continue

    def _check_win_condition(self):
        if not self.enemies and self.running:
            self.running = False
            self.message = "ПЕРЕМОГА! Всі вороги знищені."

    # ==========================================
    # Логіка колізій
    # ==========================================

    def _check_out_of_bounds(self, b):
        if self.game_map.is_out_of_bounds(b.x, b.y):
            self.bullets.remove(b)
            return True
        return False

    def _check_wall_collision(self, b):
        if self.game_map.is_wall(b.x, b.y):
            self.game_map.destroy_wall(b.x, b.y)
            self.explosions.append({'x': b.x, 'y': b.y, 'timer': 2})
            self.bullets.remove(b)
            return True
        return False

    def _check_bullet_collision(self, b):
        for ob in self.bullets[:]:
            if b != ob and b.is_player != ob.is_player and ob in self.bullets:
                if b.x == ob.x and b.y == ob.y:
                    self.bullets.remove(ob)
                    self.explosions.append({'x': b.x, 'y': b.y, 'timer': 1})
                    self.bullets.remove(b)
                    return True
        return False

    def _check_tank_collision(self, b):
        def is_hit(bullet, tank):
            if bullet.x == tank.x and bullet.y == tank.y:
                return True
            if bullet.x == tank.last_x and bullet.y == tank.last_y and \
               bullet.last_x == tank.x and bullet.last_y == tank.y:
                return True
            return False

        for e in self.enemies[:]:
            if is_hit(b, e):
                self.enemies.remove(e)
                self.explosions.append({'x': e.x, 'y': e.y, 'timer': 3})
                self.bullets.remove(b)
                return True

        if not b.is_player and is_hit(b, self.player):
            self.player.is_alive = False
            self.explosions.append({'x': self.player.x, 'y': self.player.y, 'timer': 5})
            self.running = False
            self.message = "ПОРАЗКА! Ваш танк знищено."
            self.bullets.remove(b)
            return True

        return False