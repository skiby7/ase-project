DEBUG = 0
INFO = 1
WARN = 2
ERROR = 3
log_level = 0


def set_log_level(level: int):
    global log_level
    log_level = level


def log(level: int, message):
    global log_level
    if level == DEBUG and level >= log_level:
        print(f"\u001b[36mDEBUG\u001b[0m:    {message}", flush=True)
    elif level == INFO and level >= log_level:
        print(f"\u001b[32mINFO\u001b[0m:     {message}", flush=True)
    elif level == WARN and level >= log_level:
        print(f"\u001b[33mERROR\u001b[0m:    {message}", flush=True)
    elif level == ERROR and level >= log_level:
        print(f"\u001b[31mERROR\u001b[0m:    {message}", flush=True)
