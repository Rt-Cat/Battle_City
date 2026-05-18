import sys
import os

try:
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
    import select
    import tty
    import termios
    def get_input():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        res = None
        try:
            tty.setraw(fd)
            while True:
                i, _, _ = select.select([fd], [], [], 0)
                if i:
                    ch = sys.stdin.read(1)
                    if ch == '\x1b':
                        i2, _, _ = select.select([fd], [], [], 0.01)
                        if i2 and sys.stdin.read(1) == '[':
                            i3, _, _ = select.select([fd], [], [], 0.01)
                            if i3:
                                seq = sys.stdin.read(1)
                                if seq == 'A': res = 'up'
                                elif seq == 'B': res = 'down'
                                elif seq == 'D': res = 'left'
                                elif seq == 'C': res = 'right'
                    elif ch in ('\n', '\r'):
                        res = 'enter'
                    else:
                        res = ch.lower()
                else: break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return res