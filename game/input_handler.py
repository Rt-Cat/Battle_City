import sys
import os

try:
    # ==========================================
    # РЕАЛІЗАЦІЯ ДЛЯ WINDOWS (Без змін)
    # ==========================================
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

    def start_listening(): pass
    def stop_listening(): pass

except ImportError:
    # ==========================================
    # РЕАЛІЗАЦІЯ ДЛЯ MACOS / LINUX
    # ==========================================
    import select
    import tty
    import termios
    import atexit

    _old_settings = None
    _initialized = False

    def start_listening():
        global _initialized, _old_settings
        if _initialized: return
        fd = sys.stdin.fileno()
        _old_settings = termios.tcgetattr(fd)
        
        # tty.setcbreak ідеальний для macOS: він прибирає буферизацію рядків,
        # але залишає stdout повністю робочим і не блокує екран
        tty.setcbreak(fd)
        _initialized = True

    def stop_listening():
        global _initialized, _old_settings
        if not _initialized: return
        _initialized = False
        fd = sys.stdin.fileno()
        if _old_settings:
            termios.tcsetattr(fd, termios.TCSADRAIN, _old_settings)

    # Гарантоване відновлення терміналу при закритті програми
    atexit.register(stop_listening)

    def get_input():
        global _initialized
        if not _initialized:
            start_listening()

        fd = sys.stdin.fileno()
        res = None

        # Вичитуємо абсолютно всі натиснуті клавіші з буфера за цей тік (запобігає лагам)
        while True:
            # Перевіряємо наявність символу з таймаутом 0 (миттєвий неблокуючий запит)
            r, _, _ = select.select([fd], [], [], 0)
            if not r:
                break  # Клавіш у буфері більше немає
            
            ch = os.read(fd, 1)
            
            if ch == b'\x1b':  # Початок керуючої послідовності (Стрілочки)
                # Робимо мікроскопічну перевірку на наступні байти
                r2, _, _ = select.select([fd], [], [], 0.03)
                if r2 and os.read(fd, 1) == b'[':
                    r3, _, _ = select.select([fd], [], [], 0.03)
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
                    
        return res