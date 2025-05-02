import threading
from skyfield.api import load

# Singleton instance of the ephemeris
_ephemeris = None
_loading = False
_ready_event = threading.Event()

def _load_ephemeris():
    global _ephemeris, _loading
    try:
        _ephemeris = load('de440s.bsp')
    except Exception as e:
        print(f"Error loading ephemeris data: {e}")
    finally:
        _loading = False
        _ready_event.set()

def preload_ephemeris():
    global _loading
    if not _loading:
        _loading = True
        threading.Thread(target=_load_ephemeris, daemon=True).start()

def get_ephemeris():
    # Wait for loading to complete
    _ready_event.wait()
    return _ephemeris
