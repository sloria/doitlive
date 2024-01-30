def start_ipython_player(commands, speed):
    try:
        from doitlive.ipython.app import PlayerTerminalIPythonApp
    except ImportError as error:
        raise RuntimeError("ipython blocks require IPython to be installed") from error

    PlayerTerminalIPythonApp.commands = commands
    PlayerTerminalIPythonApp.speed = speed
    PlayerTerminalIPythonApp.launch_instance()
