#doitlive shell: /bin/bash
#doitlive prompt: default
#doitlive speed: 2
#doitlive commentecho: true

### This comment stays in the file and is not displayed
# There is a comment in the .sh file above this one, but as it starts with "###", it is not echoed

#T# This is a title
# This is a normal comment after the title. Any whitespace after the initial "#" is stripped out.
# simply because that makes the .sh file more readable overall.

#2:2# This comment is preceded by 2 blank lines, and followed by 2. It is marked up with #2:2#

## This comment is preceded by one blank line. It starts with "##". It's the short-hand equivalent of "#1#" or "#1:0#"

#W# This is a warning callout, it starts with "#W#"

#I1:1# This is an info callout. We can also add blank lines around callouts: #I1:1#.

doitlive -h

