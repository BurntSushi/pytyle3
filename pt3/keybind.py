import sys

from xpybutil import conn, root
import xpybutil.event as event
import xpybutil.keysym as keysym

bindings = None

execfile('pytylemh/userkeybind.py')

assert bindings is not None, \
       'No keybindings were found'

_keybindmap = {}
kbmap = keysym.get_keyboard_mapping(conn).reply()

for key_string, fun in bindings.iteritems():
    mods, keycode = keysym.parse_keystring(conn, key_string, kbmap)
    _keybindmap[(mods, keycode)] = fun
    keysym.grab_key(conn, root, mods, keycode)

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

