import os
import os.path
import sys

# from xpybutil import conn, root 
# import xpybutil.event as event 
import xpybutil.keybind as keybind

bindings = None

#####################
# Get key bindings
xdg = os.getenv('XDG_CONFIG_HOME') or os.path.join(os.getenv('HOME'), '.config')
conffile = os.path.join(xdg, 'pytyle3', 'keybind.py')

if not os.access(conffile, os.R_OK):
    conffile = os.path.join('/', 'etc', 'xdg', 'pytyle3', 'keybind.py')
    if not os.access(conffile, os.R_OK):
        print >> sys.stderr, 'UNRECOVERABLE ERROR: ' \
                             'No configuration file found at %s' % conffile
        sys.exit(1)

execfile(conffile)
#####################

assert bindings is not None

for key_string, fun in bindings.iteritems():
    if not keybind.bind_global_key('KeyPress', key_string, fun):
        print >> sys.stderr, 'Could not bind %s' % key_string

