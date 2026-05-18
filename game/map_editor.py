import time
import os
import sys
import constants as c
from game.input_handler import get_input, start_listening, stop_listening
from game.map_manager import MapManager
from utils.renderer import Renderer

class MapEditor:
    def __init__(self, existing_level_idx=None):
        self.renderer = Renderer()
        self.existing_level_idx = existing_level_idx
        
        if existing_level_idx is not None:
            level = MapManager.get_level(existing_level_idx)
            self.name = level['name']
            self.width = level['width']
            self.height = level['height']
            self.grid = [list(row) for row in level['layout']]
            
            if level.get('player_start'):
                self.grid[level['player_start']['y']][level['player_start']['x']] = 'R'
            for e in level.get('enemy_spawns', []):
                self.grid[e['y']][e['x']] = 'E'
        else:
            self._prompt_setup()

        self.cursor_x = self.width // 2
        self.cursor_y = self.height // 2
        self.running = True

    def _prompt_setup(self):
        # Тимчасово вимикаємо сирий режим, щоб працювали стандартні print() та input()
        stop_listening()
        
        # Повертаємо текстовий курсор для зручності введення
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=== СТВОРЕННЯ НОВОЇ КАРТИ ===")
        
        existing_levels = MapManager.get_all_levels()
        existing_names = [level['name'].lower() for level in existing_levels]
        
        while True:
            name_input = input("Введіть назву карти: ").strip()
            self.name = name_input if name_input else "Unnamed Map"
            
            if self.name.lower() in existing_names:
                print(f"Помилка: Карта з назвою '{self.name}' вже існує!")
            else:
                break
        
        try:
            w = int(input("Ширина (макс 40): "))
            self.width = max(5, min(40, w))
            h = int(input("Висота (макс 40): "))
            self.height = max(5, min(40, h))
        except ValueError:
            self.width, self.height = 20, 15
            
        self.grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Вмикаємо сирий режим та фоновий потік назад перед стартом редактора
        start_listening()

    def run(self):
        get_input()  # Очистка буфера
        while self.running:
            self.renderer.render_editor(self.grid, self.cursor_x, self.cursor_y, self.name)
            key = get_input()
            
            if key == 'up' and self.cursor_y > 0: self.cursor_y -= 1
            elif key == 'down' and self.cursor_y < self.height - 1: self.cursor_y += 1
            elif key == 'left' and self.cursor_x > 0: self.cursor_x -= 1
            elif key == 'right' and self.cursor_x < self.width - 1: self.cursor_x += 1
            
            elif key == 'w': self.grid[self.cursor_y][self.cursor_x] = '#'
            elif key == 'e': self.grid[self.cursor_y][self.cursor_x] = 'E'
            elif key == 'r': 
                for y in range(self.height):
                    for x in range(self.width):
                        if self.grid[y][x] == 'R': self.grid[y][x] = ' '
                self.grid[self.cursor_y][self.cursor_x] = 'R'
            elif key == ' ': self.grid[self.cursor_y][self.cursor_x] = ' ' 
            
            elif key == 'enter':
                self._save_map()
                self.running = False
                
            elif key == 'q':
                self._handle_quit_prompt()
                
            time.sleep(0.05)

    def _handle_quit_prompt(self):
        # На час текстового вікна підтвердження знову вимикаємо сирий режим
        stop_listening()
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()
        
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Ви дійсно хочете вийти?")
            print("[S] Save (Зберегти)")
            print("[D] Destroy (Скасувати)")
            k = input("Ваш вибір: ").strip().lower()
            if k == 's':
                self._save_map()
                self.running = False
                break
            elif k == 'd':
                self.running = False
                break
        
        start_listening()

    def _save_map(self):
        player_start = None 
        enemy_spawns = []
        layout = []
        
        for y in range(self.height):
            row_str = ""
            for x in range(self.width):
                char = self.grid[y][x]
                if char == 'R':
                    player_start = {"x": x, "y": y}
                    row_str += " "
                elif char == 'E':
                    enemy_spawns.append({"x": x, "y": y})
                    row_str += " "
                else:
                    row_str += char
            layout.append(row_str)

        level_data = {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "layout": layout,
            "player_start": player_start,
            "enemy_spawns": enemy_spawns
        }
        MapManager.save_level(level_data, self.existing_level_idx)