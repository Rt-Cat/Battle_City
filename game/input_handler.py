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
    # РЕАЛІЗАЦІЯ ДЛЯ MACOS / LINUX (ФІКС БЛОКУВАННЯ)
    # ==========================================
    import select
    import tty
    import termios
    import threading
    import queue
    import time
    import atexit

    _input_queue = queue.Queue()
    _initialized = False
    _old_settings = None

    def _background_listener(fd):
        """Фоновий потік безпечно опитує дескриптор через select, не ламаючи stdout."""
        global _initialized
        
        while _initialized:
            # Використовуємо select з таймаутом 0.05 сек.
            # Це дозволяє потоку не блокувати термінал намертво і реагувати на закриття програми
            r, _, _ = select.select([fd], [], [], 0.05)
            if r:
                try:
                    ch = os.read(fd, 1)
                    if not ch: continue
                    
                    if ch == b'\x03':  # Ctrl+C
                        _input_queue.put('ctrl_c')
                        break
                        
                    elif ch == b'\x1b':  # Escape-послідовність (Стрілочки)
                        # Перевіряємо, чи летять наступні байти структури
                        r2, _, _ = select.select([fd], [], [], 0.02)
                        if r2 and os.read(fd, 1) == b'[':
                            r3, _, _ = select.select([fd], [], [], 0.02)
                            if r3:
                                seq = os.read(fd, 1)
                                if seq == b'A': _input_queue.put('up')
                                elif seq == b'B': _input_queue.put('down')
                                elif seq == b'C': _input_queue.put('right')
                                elif seq == b'D': _input_queue.put('left')
                                
                    elif ch in (b'\n', b'\r'):
                        _input_queue.put('enter')
                    else:
                        try:
                            _input_queue.put(ch.decode('utf-8').lower())
                        except UnicodeDecodeError:
                            pass
                except Exception:
                    pass

    def start_listening():
        global _initialized, _old_settings
        if _initialized: return
        
        fd = sys.stdin.fileno()
        _old_settings = termios.tcgetattr(fd)
        
        # Переводимо в сирий режим, але НЕ чіпаємо fcntl O_NONBLOCK!
        tty.setraw(fd)
        _initialized = True
        
        t = threading.Thread(target=_background_listener, args=(fd,), daemon=True)
        t.start()

    def stop_listening():
        global _initialized, _old_settings
        if not _initialized: return
        _initialized = False
        
        fd = sys.stdin.fileno()
        if _old_settings:
            termios.tcsetattr(fd, termios.TCSADRAIN, _old_settings)

    atexit.register(stop_listening)

    def get_input():
        global _initialized
        if not _initialized:
            start_listening()
            
        res = None
        while not _input_queue.empty():
            item = _input_queue.get_nowait()
            if item == 'ctrl_c':
                raise KeyboardInterrupt
            res = item
        return res