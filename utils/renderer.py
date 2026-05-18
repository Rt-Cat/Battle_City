import os
import sys
import constants as c

class Renderer:
    def __init__(self):
        if os.name == 'nt':
            os.system('')
        self.first_render = True

    def clear(self):
        # Повертаємо курсор і повністю чистимо термінал
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()
        os.system('cls' if os.name == 'nt' else 'clear')
        self.first_render = True

    def _render_frame(self, frame_lines):
        import time
        
        if self.first_render:
            self.clear()
            self.first_render = False
        
        sys.stdout.write('\033[?25l\033[H')
        output = "\r\n".join([line + "\033[K" for line in frame_lines])
        
        # Залізобетонний вивід: якщо ОС каже, що буфер повний,
        # ми робимо мікропаузу і повторюємо спробу замість крашу програми
        while True:
            try:
                sys.stdout.write(output + "\033[J")
                sys.stdout.flush()
                break
            except BlockingIOError:
                time.sleep(0.005) # Чекаємо 5мс, поки термінал звільнить буфер

    # ===============================
    # ВІДМАЛЬОВКА ГРИ
    # ===============================
    def render_game(self, game_map, player, enemies, bullets, explosions, message=""):
        frame = []
        frame.append(f"=== BATTLE CITY | {game_map.name} ===")
        
        grid = [[c.EMPTY for _ in range(game_map.width)] for _ in range(game_map.height)]
        
        for (wx, wy) in game_map.walls: grid[wy][wx] = c.WALL
        for exp in explosions: grid[exp['y']][exp['x']] = c.EXPLOSION
        for b in bullets:
            if 0 <= b.x < game_map.width and 0 <= b.y < game_map.height:
                grid[b.y][b.x] = c.PLAYER_BULLET if b.is_player else c.ENEMY_BULLET
                
        for e in enemies:
            arrow = c.ARROWS.get(e.direction, 'v')
            grid[e.y][e.x] = f"{c.RED}{arrow}{c.RESET}"
            
        if player.is_alive:
            arrow = c.ARROWS.get(player.direction, '^')
            grid[player.y][player.x] = f"{c.GREEN}{arrow}{c.RESET}"

        self._draw_box(grid, game_map.width, frame)
        
        frame.append("")
        frame.append("Управління: [WASD] Рух | [Стрілочки] Поворот | [ПРОБІЛ] Постріл | [Q] Меню")
        if message: 
            frame.append("")
            frame.append(f"{c.RED}>>> {message} <<<{c.RESET}")
            
        self._render_frame(frame)

    # ===============================
    # ВІДМАЛЬОВКА МЕНЮ
    # ===============================
    def render_main_menu(self, options, selected_idx):
        frame = []
        frame.append("="*30)
        frame.append("        BATTLE CITY         ")
        frame.append("="*30)
        frame.append("")
        
        for i, opt in enumerate(options):
            if i == selected_idx:
                frame.append(f"  > {c.CYAN}{opt}{c.RESET}")
            else:
                frame.append(f"    {opt}")
                
        frame.append("")
        frame.append("")
        frame.append("[Стрілочки Вгору/Вниз] Вибір | [Enter] Підтвердити")
        self._render_frame(frame)

    def render_maps_menu(self, options, selected_idx):
        frame = []
        frame.append("="*30)
        frame.append("        МЕНЮ КАРТ           ")
        frame.append("="*30)
        frame.append("")
        
        for i, opt in enumerate(options):
            if i == selected_idx:
                if "Select Map:" in opt:
                    frame.append(f"  > {c.CYAN}{opt}{c.RESET}")
                else:
                    frame.append(f"  > {c.GREEN}{opt}{c.RESET}")
            else:
                frame.append(f"    {opt}")
        
        frame.append("")
        frame.append("")
        frame.append("[Вгору/Вниз] Навігація по меню")
        frame.append("[Вліво/Вправо] Змінити карту (на пункті Select Map)")
        frame.append("[Enter] Підтвердити дію | [Q] Назад")
        self._render_frame(frame)

    def render_play_select(self, levels, selected_idx):
        frame = []
        frame.append("="*30)
        frame.append("        ВИБІР КАРТИ         ")
        frame.append("="*30)
        frame.append("")
        
        map_data = levels[selected_idx]
        map_name = map_data['name']
        
        is_valid = map_data.get('player_start') is not None and len(map_data.get('enemy_spawns', [])) > 0
        color = c.CYAN if is_valid else c.YELLOW
        
        frame.append(f"  <  {color}{map_name}{c.RESET}  >")
        
        if not is_valid:
            frame.append("")
            frame.append(f"  {c.YELLOW}* Карта недобудована{c.RESET}")
            
        frame.append("")
        frame.append("")
        frame.append("[<- ->] Гортати | [Enter] Грати | [Q] Назад")
        self._render_frame(frame)

    def render_invalid_map_prompt(self, map_name, reason):
        frame = []
        frame.append("="*30)
        frame.append("      ПОМИЛКА ЗАПУСКУ       ")
        frame.append("="*30)
        frame.append("")
        frame.append(f"Карта: {c.YELLOW}{map_name}{c.RESET}")
        frame.append(f"Причина: {c.RED}{reason}{c.RESET}")
        frame.append("")
        frame.append("Гру на цій карті неможливо розпочати!")
        frame.append("")
        frame.append("[E] Редагувати карту")
        frame.append("[Q] Обрати іншу")
        self._render_frame(frame)

    # ===============================
    # ВІДМАЛЬОВКА РЕДАКТОРА
    # ===============================
    def render_editor(self, grid, cx, cy, name):
        frame = []
        frame.append(f"=== РЕДАКТОР: {name} ===")
        
        width = len(grid[0])
        render_grid = [row.copy() for row in grid]
        
        for y in range(len(grid)):
            for x in range(width):
                if render_grid[y][x] == '#': render_grid[y][x] = c.WALL
                elif render_grid[y][x] == 'R': render_grid[y][x] = f"{c.GREEN}R{c.RESET}"
                elif render_grid[y][x] == 'E': render_grid[y][x] = f"{c.RED}E{c.RESET}"

        if grid[cy][cx] != ' ':
            render_grid[cy][cx] = f"{c.BG_WHITE}{c.TEXT_BLACK}{grid[cy][cx]}{c.RESET}"
        else:
            render_grid[cy][cx] = f"{c.BG_WHITE} {c.RESET}"

        self._draw_box(render_grid, width, frame)
        
        frame.append("")
        frame.append("[Стрілочки] Рух | [W] Стіна | [E] Ворог | [R] Гравець | [Пробіл] Стерти")
        frame.append("[Enter] Зберегти | [Q] Вихід/Скасувати")
        
        self._render_frame(frame)

    # ===============================
    # ДОПОМІЖНІ МЕТОДИ
    # ===============================
    def _draw_box(self, grid, width, frame_list):
        frame_list.append(c.YELLOW + "+" + "-" * width + "+" + c.RESET)
        for row in grid:
            frame_list.append(c.YELLOW + "|" + c.RESET + "".join(row) + c.YELLOW + "|" + c.RESET)
        frame_list.append(c.YELLOW + "+" + "-" * width + "+" + c.RESET)