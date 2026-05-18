import sys
import os

try:
    # ==========================================
    # РЕАЛІЗАЦІЯ ДЛЯ WINDOWS
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
        global _initialized
        buffer = b''
        
        while _initialized:
            try:
                ch = os.read(fd, 1)
                if not ch: continue
                if ch == b'\x03':
                    _input_queue.put('ctrl_c')
                    break
                buffer += ch
            except BlockingIOError:
                if buffer:
                    if buffer == b'\x1b[A': _input_queue.put('up')
                    elif buffer == b'\x1b[B': _input_queue.put('down')
                    elif buffer == b'\x1b[C': _input_queue.put('right')
                    elif buffer == b'\x1b[D': _input_queue.put('left')
                    elif buffer in (b'\n', b'\r'): _input_queue.put('enter')
                    elif len(buffer) == 1:
                        try: _input_queue.put(buffer.decode('utf-8').lower())
                        except: pass
                    buffer = b''
                time.sleep(0.01)

    def start_listening():
        global _initialized, _old_settings, _old_flags
        if _initialized: return
        
        fd = sys.stdin.fileno()
        _old_settings = termios.tcgetattr(fd)
        _old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        
        tty.setraw(fd)
        fcntl.fcntl(fd, fcntl.F_SETFL, _old_flags | os.O_NONBLOCK)
        _initialized = True
        
        t = threading.Thread(target=_background_listener, args=(fd,), daemon=True)
        t.start()

    def stop_listening():
        global _initialized, _old_settings, _old_flags
        if not _initialized: return
        _initialized = False
        
        fd = sys.stdin.fileno()
        if _old_settings:
            termios.tcsetattr(fd, termios.TCSADRAIN, _old_settings)
        if _old_flags:
            fcntl.fcntl(fd, fcntl.F_SETFL, _old_flags)

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