import packaging.version


def is_modern_ipython():
    try:
        import IPython
    except ImportError:
        raise RuntimeError("ipython blocks require IPython to be installed")

    return packaging.version.parse(IPython.__version__) >= packaging.version.parse(
        "7.0.0"
    )


def start_ipython_player(commands, speed):
    if is_modern_ipython():
        from doitlive.ipython.app import PlayerTerminalIPythonApp
    else:
        from doitlive.ipython.legacy_app import PlayerTerminalIPythonApp

    PlayerTerminalIPythonApp.commands = commands
    PlayerTerminalIPythonApp.speed = speed
    PlayerTerminalIPythonApp.launch_instance()
