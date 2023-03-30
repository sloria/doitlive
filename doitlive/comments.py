import re

from click import echo, secho


def display_comment(command):
    # Triple ### = comment not to be output
    if command.startswith("###"):
        return
    
    # Double ## optionally containing instructions 
    # = special treatment
    applied = special_comment(command)
    if applied:
        return
    
    else:
        comment = re.sub(r"^#+\d*\s*", '', command)
        simple_comment(comment)
            
            
def special_comment(comment):
    pattern = r'^#([WIT])?(?:(\d+)?(?::?(\d+)?)?)#'
    match = re.search(pattern, comment)
    
    if match:
        callout = match.group(1)
        a = match.group(2)
        b = match.group(3)
        
        a = int(a) if a is not None else 0
        b = int(b) if b is not None else 0
        
        stripped_s = re.sub(pattern, '', comment).lstrip()
        
        for i in range(a):
            echo()
        comment_callout(stripped_s, callout)
        for i in range(b):
            echo()
        return stripped_s


def comment_callout(comment, callout):
    color_mapping = dict(
        W=("red", True, "❗️"),
        I=("cyan", False, "💡"),
        T=("blue", True, None)
    )    
    color = color_mapping.get(callout)

    if callout == "T":
        # title
        echo()
        echo("=" * len(comment))

    if color:
        # prefix with optional icon
        if color[2]:
            comment = color[2] + "  " + comment

        secho(comment, fg=color[0], bold=color[1])
    else:
        simple_comment(comment)
    
    if callout == "T":
        echo()
        
    return comment


def simple_comment(comment):
    secho(comment, fg="yellow", bold=True)