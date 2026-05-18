import sys
import os
from game.menu import Menu

def restore_terminal():
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()
    os.system('cls' if os.name == 'nt' else 'clear')

def sanitize_terminal_flags():
    """Фікс BlockingIOError: скидаємо забаговані прапорці ОС для macOS терміналу."""
    if os.name != 'nt':
        try:
            import fcntl
            for stream in (sys.stdin, sys.stdout):
                fd = stream.fileno()
                flags = fcntl.fcntl(fd, fcntl.F_GETFL)
                # Примусово прибираємо O_NONBLOCK, якщо він залишився від минулих крашів
                fcntl.fcntl(fd, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)
        except Exception:
            pass

if __name__ == "__main__":
    # Лікуємо термінал перед стартом
    sanitize_terminal_flags()
    
    try:
        menu = Menu()
        menu.run()
    except KeyboardInterrupt:
        pass
    finally:
        restore_terminal()