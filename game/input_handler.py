import sys
import os

try:
    # Windows implementation
    import msvcrt
    def get_input():
        res = None
        while msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch in (b'\x00', b'\xe0'):
                ch = msvcrt.getch()
                if ch == b'H': res = 'up'
                elif ch == b'P': res = 'down'
                elif ch == b'K': res = 'left'
                elif ch == b'M': res = 'right'
            elif ch == b'\r':
                res = 'enter'
            else:
                try:
                    res = ch.decode('utf-8', 'ignore').lower()
                except: pass
        return res
        
except ImportError:
    # Unix/Linux/MacOS implementation
    import select
    import tty
    import termios
    
    def get_input():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        res = None
        try:
            # setcbreak краще підходить для macOS, ніж setraw (і не ламає Ctrl+C)
            tty.setcbreak(fd)
            while True:
                i, _, _ = select.select([fd], [], [], 0)
                if i:
                    # Читаємо сирі байти через os.read, щоб обійти блокування буфера sys.stdin
                    ch = os.read(fd, 1)
                    if ch == b'\x1b':
                        # Збільшений таймаут до 0.02 для обробки стрілочок на маках
                        i2, _, _ = select.select([fd], [], [], 0.02)
                        if i2 and os.read(fd, 1) == b'[':
                            i3, _, _ = select.select([fd], [], [], 0.02)
                            if i3:
                                seq = os.read(fd, 1)
                                if seq == b'A': res = 'up'
                                elif seq == b'B': res = 'down'
                                elif seq == b'D': res = 'left'
                                elif seq == b'C': res = 'right'
                    elif ch in (b'\n', b'\r'):
                        res = 'enter'
                    else:
                        try:
                            res = ch.decode('utf-8').lower()
                        except UnicodeDecodeError:
                            pass
                else:
                    break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return res