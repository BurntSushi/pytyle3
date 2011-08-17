import os
import os.path
import sys

from xpybutil import conn, root
import xpybutil.event as event
import xpybutil.keysym as keysym

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

_keybindmap = {}
kbmap = keysym.get_keyboard_mapping(conn).reply()

for key_string, fun in bindings.iteritems():
    mods, keycode = keysym.parse_keystring(conn, key_string, kbmap)
    _keybindmap[(mods, keycode)] = fun
    if not keysym.grab_key(conn, root, mods, keycode):
        print >> sys.stderr, 'Could not bind %s' % key_string

def cb_key_press(e):
    sys.stdout.flush()
    keycode, mods = e.detail, e.state
    for mod in keysym.TRIVIAL_MODS:
        mods &= ~mod

    key = (mods, keycode)
    if key in _keybindmap:
        _keybindmap[key]()

def cb_mapping_notify(e):
    global kbmap

    kbmap = keysym.get_keyboard_mapping(conn).reply()

event.connect('MappingNotify', root, cb_mapping_notify)
event.connect('KeyPress', root, cb_key_press)

