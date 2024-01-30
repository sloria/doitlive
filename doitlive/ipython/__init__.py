def start_ipython_player(commands, speed):
    try:
        from doitlive.ipython.app import PlayerTerminalIPythonApp
    except ImportError:
        raise RuntimeError("ipython blocks require IPython to be installed")

    PlayerTerminalIPythonApp.commands = commands
    PlayerTerminalIPythonApp.speed = speed
    PlayerTerminalIPythonApp.launch_instance()
