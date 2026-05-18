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
    import threading
    import queue
    import time
    import atexit

    _input_queue = queue.Queue()
    _initialized = False
    _old_settings = None
    _old_flags = None

    def _background_listener(fd):
        """Фоновий потік, який безперервно і без блокувань зчитує байти з терміналу."""
        global _initialized
        buffer = b''
        
        while _initialized:
            try:
                # Намагаємося зчитати 1 байт
                ch = os.read(fd, 1)
                if not ch:
                    continue
                
                # Перехоплюємо Ctrl+C у сирому режимі
                if ch == b'\x03':
                    _input_queue.put('ctrl_c')
                    break
                
                buffer += ch
            except BlockingIOError:
                # Якщо зараз байтів немає, обробляємо те, що вже встигли накопичити в буфері
                if buffer:
                    if buffer == b'\x1b[A': _input_queue.put('up')
                    elif buffer == b'\x1b[B': _input_queue.put('down')
                    elif buffer == b'\x1b[C': _input_queue.put('right')
                    elif buffer == b'\x1b[D': _input_queue.put('left')
                    elif buffer in (b'\n', b'\r'): _input_queue.put('enter')
                    elif len(buffer) == 1:
                        try:
                            _input_queue.put(buffer.decode('utf-8').lower())
                        except: pass
                    buffer = b''
                # Мікропауза 10мс, щоб потік не навантажував процесор на 100%
                time.sleep(0.01)

    def _start_listening():
        global _initialized, _old_settings, _old_flags
        if _initialized: return
        
        fd = sys.stdin.fileno()
        _old_settings = termios.tcgetattr(fd)
        _old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        
        # Переводимо термінал у постійний сирий режим
        tty.setraw(fd)
        # Робимо читання неблокуючим на рівні ОС
        fcntl.fcntl(fd, fcntl.F_SETFL, _old_flags | os.O_NONBLOCK)
        
        _initialized = True
        
        # Запускаємо демон-потік для збору кліків
        t = threading.Thread(target=_background_listener, args=(fd,), daemon=True)
        t.start()

    def _stop_listening():
        """Повертає термінал macOS до тями."""
        global _initialized, _old_settings, _old_flags
        if not _initialized: return
        _initialized = False
        
        fd = sys.stdin.fileno()
        if _old_settings:
            termios.tcsetattr(fd, termios.TCSADRAIN, _old_settings)
        if _old_flags:
            fcntl.fcntl(fd, fcntl.F_SETFL, _old_flags)

    # Автоматично викликати відновлення терміналу при будь-якому виході з Python
    atexit.register(_stop_listening)

    def get_input():
        global _initialized
        if not _initialized:
            _start_listening()
            
        res = None
        # Забираємо найсвіжішу клавішу з нашого фонового буфера
        while not _input_queue.empty():
            item = _input_queue.get_nowait()
            if item == 'ctrl_c':
                raise KeyboardInterrupt
            res = item
        return res