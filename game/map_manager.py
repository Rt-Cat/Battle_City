import json
import os

class MapManager:
    FILE_PATH = 'maps.json'

    @classmethod
    def get_all_levels(cls):
        if not os.path.exists(cls.FILE_PATH):
            with open(cls.FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump({"levels": []}, f, indent=2)
            return []
        with open(cls.FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f).get('levels', [])

    @classmethod
    def get_level(cls, index):
        levels = cls.get_all_levels()
        return levels[index] if 0 <= index < len(levels) else None

    @classmethod
    def save_level(cls, level_data, index=None):
        levels = cls.get_all_levels()
        if index is not None and 0 <= index < len(levels):
            levels[index] = level_data
        else:
            levels.append(level_data)
        
        with open(cls.FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump({"levels": levels}, f, indent=2)

    @classmethod
    def delete_level(cls, index):
        levels = cls.get_all_levels()
        if 0 <= index < len(levels):
            del levels[index]
            with open(cls.FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump({"levels": levels}, f, indent=2)