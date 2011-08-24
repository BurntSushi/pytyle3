import sys

import config

def debug(s):
    if not config.debug:
        return
    print s
    sys.stdout.flush()

