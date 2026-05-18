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
            # Використовуємо setraw замість setcbreak.
            # Це гарантує, що macOS віддаватиме натискання миттєво без жодної буферизації.
            tty.setraw(fd)
            
            while True:
                # Слухаємо безпосередньо системний дескриптор, ігноруючи буфер Python
                r, w, x = select.select([fd], [], [], 0)
                if r:
                    ch = os.read(fd, 1)
                    
                    if ch == b'\x03': 
                        # В setraw режим Ctrl+C не генерує сигнал SIGINT, а просто шле байт \x03.
                        # Ми перехоплюємо його вручну, щоб гра могла коректно закритися.
                        raise KeyboardInterrupt
                        
                    elif ch == b'\x1b':
                        # Обробка Escape-послідовностей (стрілочки)
                        r2, _, _ = select.select([fd], [], [], 0.02)
                        if r2:
                            if os.read(fd, 1) == b'[':
                                r3, _, _ = select.select([fd], [], [], 0.02)
                                if r3:
                                    seq = os.read(fd, 1)
                                    if seq == b'A': res = 'up'
                                    elif seq == b'B': res = 'down'
                                    elif seq == b'C': res = 'right'
                                    elif seq == b'D': res = 'left'
                    elif ch in (b'\n', b'\r'):
                        res = 'enter'
                    else:
                        try:
                            res = ch.decode('utf-8').lower()
                        except UnicodeDecodeError:
                            pass
                else:
                    break # Буфер клавіатури порожній, виходимо з циклу
        finally:
            # ЗАВЖДИ повертаємо термінал у нормальний стан
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
        return res