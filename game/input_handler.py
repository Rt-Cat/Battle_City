import sys
import os

try:
    # Windows
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
    # macOS / Linux
    import tty
    import termios
    import fcntl
    import time
    
    def get_input():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        # Отримуємо поточні прапорці файлового дескриптора
        old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        
        res = None
        try:
            # Переводимо термінал у сирий режим
            tty.setraw(fd)
            # Встановлюємо неблокуючий режим читання (O_NONBLOCK)
            fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
            
            while True:
                try:
                    ch = os.read(fd, 1)
                    
                    if ch == b'\x03':  # Ctrl+C
                        raise KeyboardInterrupt
                    elif ch == b'\x1b':  # Стрілочки (Escape-послідовність)
                        time.sleep(0.01) # Мікропауза, щоб буфер встиг наповнитися
                        try:
                            if os.read(fd, 1) == b'[':
                                time.sleep(0.01)
                                seq = os.read(fd, 1)
                                if seq == b'A': res = 'up'
                                elif seq == b'B': res = 'down'
                                elif seq == b'C': res = 'right'
                                elif seq == b'D': res = 'left'
                        except BlockingIOError:
                            pass
                    elif ch in (b'\n', b'\r'):
                        res = 'enter'
                    else:
                        try:
                            res = ch.decode('utf-8').lower()
                        except UnicodeDecodeError:
                            pass
                except BlockingIOError:
                    # У неблокуючому режимі помилка BlockingIOError означає "немає нових натискань"
                    break
                    
        finally:
            # Повертаємо все як було
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)
            
        return res