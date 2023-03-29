import re

from click import secho


def display_comment(command):
    # Triple ### = comment not to be output
    if command.startswith("###"):
        return
    
    # Double ## followed by an int = comment is preceded by X blank lines
    if command.startswith('##'):
        has_digit = re.search(r'##(\d+)', command)
        blanks = int(has_digit.group(1)) if has_digit else 1
        for i in range(blanks):
            secho()
    
    comment = re.sub(r"^#+\d*\s*", '', command)
    secho(comment, fg="yellow", bold=True)