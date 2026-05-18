import sys
import os
from game.menu import Menu

def restore_terminal():
    # Примусово повертаємо видимість курсора
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()
    # Очищаємо екран, щоб не залишалося сміття після раптового виходу
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    try:
        menu = Menu()
        menu.run()
    except KeyboardInterrupt:
        # Безшумно перехоплюємо Ctrl+C, щоб не виводити купу червоного тексту (Traceback)
        pass
    finally:
        # Цей блок виконається ЗАВЖДИ, навіть при помилці чи Ctrl+C
        restore_terminal()