import time
import constants as c
from game.input_handler import get_input
from game.map_manager import MapManager
from game.map_editor import MapEditor
from game.game import Game
from utils.renderer import Renderer

class Menu:
    def __init__(self):
        self.renderer = Renderer()
        self.state = "MAIN" 
        self.main_options = ["Play", "Maps", "Quit"]
        self.main_idx = 0
        self.maps_opt_idx = 0 
        self.map_idx = 0      
        
        self.invalid_map_reason = ""
        self.previous_state = ""
        
        self.running = True

    def _validate_map(self, level_data):
        reasons = []
        if not level_data.get('player_start'):
            reasons.append("Не розміщено гравця (R)")
        if not level_data.get('enemy_spawns') or len(level_data.get('enemy_spawns')) == 0:
            reasons.append("Не розміщено жодного ворога (E)")
            
        return len(reasons) == 0, " та ".join(reasons)

    def run(self):
        while self.running:
            levels = MapManager.get_all_levels()
            current_main_opts = self.main_options.copy()
            if len(levels) == 0 and "Play" in current_main_opts:
                current_main_opts.remove("Play")
            
            self.main_idx = min(self.main_idx, len(current_main_opts) - 1)

            if self.state == "MAIN":
                self.renderer.render_main_menu(current_main_opts, self.main_idx)
                key = get_input()
                if key == 'up' and self.main_idx > 0: self.main_idx -= 1
                elif key == 'down' and self.main_idx < len(current_main_opts) - 1: self.main_idx += 1
                elif key == 'enter':
                    selection = current_main_opts[self.main_idx]
                    if selection == "Play":
                        self.state = "PLAY_SELECT"
                        self.map_idx = 0
                        self.renderer.clear()
                    elif selection == "Maps":
                        self.state = "MAPS_MENU"
                        self.maps_opt_idx = 0 
                        self.renderer.clear()
                    elif selection == "Quit":
                        self.running = False
                        self.renderer.clear()

            elif self.state == "MAPS_MENU":
                has_maps = len(levels) > 0
                if has_maps:
                    self.map_idx = max(0, min(self.map_idx, len(levels) - 1))
                    map_name = levels[self.map_idx]['name']
                    
                    is_valid, _ = self._validate_map(levels[self.map_idx])
                    color = c.CYAN if is_valid else c.YELLOW
                    
                    maps_options = [
                        "Create New Map",
                        f"Select Map: < {color}{map_name}{c.RESET} >",
                        "Edit Map",
                        "Delete Map",
                        "Play Map",
                        "Back"
                    ]
                else:
                    self.map_idx = 0
                    maps_options = ["Create New Map", "Back"]
                
                self.maps_opt_idx = max(0, min(self.maps_opt_idx, len(maps_options) - 1))
                self.renderer.render_maps_menu(maps_options, self.maps_opt_idx)
                
                key = get_input()
                if key == 'up' and self.maps_opt_idx > 0: self.maps_opt_idx -= 1
                elif key == 'down' and self.maps_opt_idx < len(maps_options) - 1: self.maps_opt_idx += 1
                elif key == 'left' and has_maps and self.maps_opt_idx == 1:
                    if self.map_idx > 0: self.map_idx -= 1
                elif key == 'right' and has_maps and self.maps_opt_idx == 1:
                    if self.map_idx < len(levels) - 1: self.map_idx += 1
                elif key == 'q': 
                    self.state = "MAIN"
                    self.maps_opt_idx = 0
                    self.renderer.clear()
                elif key == 'enter':
                    selection = maps_options[self.maps_opt_idx]
                    if selection == "Create New Map":
                        editor = MapEditor()
                        editor.run()
                        self.renderer.clear() # Очищаємо екран після виходу з редактора
                    elif selection.startswith("Select Map:"): pass
                    elif selection == "Edit Map":
                        editor = MapEditor(existing_level_idx=self.map_idx)
                        editor.run()
                        self.renderer.clear()
                    elif selection == "Delete Map":
                        MapManager.delete_level(self.map_idx)
                        self.maps_opt_idx = 0 
                        self.renderer.clear()
                    elif selection == "Play Map":
                        is_valid, reason = self._validate_map(levels[self.map_idx])
                        if is_valid:
                            game = Game(level_index=self.map_idx)
                            game.run()
                            self.renderer.clear()
                        else:
                            self.invalid_map_reason = reason
                            self.previous_state = self.state
                            self.state = "INVALID_MAP_PROMPT"
                            self.renderer.clear()
                    elif selection == "Back":
                        self.state = "MAIN"
                        self.maps_opt_idx = 0
                        self.renderer.clear()

            elif self.state == "PLAY_SELECT":
                self.renderer.render_play_select(levels, self.map_idx)
                key = get_input()
                if key == 'left' and self.map_idx > 0: self.map_idx -= 1
                elif key == 'right' and self.map_idx < len(levels) - 1: self.map_idx += 1
                elif key == 'q': 
                    self.state = "MAIN"
                    self.renderer.clear()
                elif key == 'enter':
                    is_valid, reason = self._validate_map(levels[self.map_idx])
                    if is_valid:
                        game = Game(level_index=self.map_idx)
                        game.run()
                        self.state = "MAIN" 
                        self.renderer.clear()
                    else:
                        self.invalid_map_reason = reason
                        self.previous_state = self.state
                        self.state = "INVALID_MAP_PROMPT"
                        self.renderer.clear()
                        
            elif self.state == "INVALID_MAP_PROMPT":
                self.renderer.render_invalid_map_prompt(levels[self.map_idx]['name'], self.invalid_map_reason)
                key = get_input()
                if key == 'e':
                    editor = MapEditor(existing_level_idx=self.map_idx)
                    editor.run()
                    self.state = self.previous_state
                    self.renderer.clear()
                elif key == 'q':
                    self.state = self.previous_state
                    self.renderer.clear()

            time.sleep(0.05)