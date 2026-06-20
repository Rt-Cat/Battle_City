import sys
import os
from game.menu import Menu

def restore_terminal():
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()
    os.system('cls' if os.name == 'nt' else 'clear')

def sanitize_terminal_flags():
    if os.name != 'nt':
        try:
            import fcntl
            for stream in (sys.stdin, sys.stdout):
                fd = stream.fileno()
                flags = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)
        except Exception:
            pass

if __name__ == "__main__":
    sanitize_terminal_flags()
    
    try:
        menu = Menu()
        menu.run()
    except KeyboardInterrupt:
        pass
    finally:
        restore_terminal()