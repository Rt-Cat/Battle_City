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
        self.valid = True # Прапорець перевірки, чи не було скасовано створення карти
        self.running = True
        
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

        if self.valid:
            self.cursor_x = self.width // 2
            self.cursor_y = self.height // 2

    def _prompt_setup(self):
        # Вимикаємо сирий режим для безпечного введення тексту через стандартний input()
        stop_listening()
        
        # Повертаємо видимість системного курсора на час введення букв
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=== СТВОРЕННЯ НОВОЇ КАРТИ ===")
        print("(Введіть 'q' у будь-якому полі для скасування виходу в меню)\n")
        
        existing_levels = MapManager.get_all_levels()
        existing_names = [level['name'].lower() for level in existing_levels]
        
        # 1. Запит імені карти
        while True:
            name_input = input("Введіть назву карти: ").strip()
            if name_input.lower() == 'q':
                self.valid = False
                self.running = False
                return
                
            self.name = name_input if name_input else "Unnamed Map"
            if self.name.lower() in existing_names:
                print(f"Помилка: Карта з назвою '{self.name}' вже існує!")
            else:
                break
        
        # 2. Запит розмірів карти
        try:
            w_input = input("Ширина (макс 40): ").strip()
            if w_input.lower() == 'q':
                self.valid = False
                self.running = False
                return
            w = int(w_input)
            self.width = max(5, min(40, w))
            
            h_input = input("Висота (макс 40): ").strip()
            if h_input.lower() == 'q':
                self.valid = False
                self.running = False
                return
            h = int(h_input)
            self.height = max(5, min(40, h))
            
        except ValueError:
            # Якщо ввели не число і не 'q' — ставимо стандартний безпечний розмір
            self.width, self.height = 20, 15
            
        self.grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Повертаємо ігровий сирий режим назад
        start_listening()

    def run(self):
        # Якщо користувач скасував створення карти на етапі prompt_setup
        if not self.valid:
            return
            
        get_input()  # Очистка буфера клавіатури перед стартом
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
        """Нове інтерактивне меню закриття, яке реагує на поодинокі клавіші миттєво."""
        get_input() # Очищаємо хвіст натискань
        
        while True:
            # Збираємо кадр за допомогою системи захисту від мерехтіння
            frame = []
            frame.append("=== ВИХІД З РЕДАКТОРА ===")
            frame.append("")
            frame.append("Ви дійсно хочете вийти?")
            frame.append("")
            frame.append(f"  > [{c.GREEN}S{c.RESET}] Save (Зберегти карту та вийти)")
            frame.append(f"  > [{c.RED}D{c.RESET}] Destroy (Скасувати всі зміни)")
            frame.append("  > [Q] Повернутися назад до редагування")
            frame.append("")
            
            self.renderer._render_frame(frame)
            
            key = get_input()
            if key == 's':
                self._save_map()
                self.running = False
                break
            elif key == 'd':
                self.running = False
                break
            elif key == 'q':
                # Просто повертаємось у редактор до малювання сітки
                break
                
            time.sleep(0.05)
            
        # Якщо користувач обрав повернутися ('q'), моментально перемальовуємо редактор,
        # щоб не залишалося