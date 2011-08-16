import sys
import time

from xpybutil import conn, root
import xpybutil.event as event
import xpybutil.ewmh as ewmh
import xpybutil.keysym as keysym
import xpybutil.util as util
import xpybutil.window as window
import xpybutil.xinerama as xinerama

import rect

PYTYLE_STATE = 'startup'

util.build_atom_cache(conn, ewmh)

_wmrunning = False

wm = 'N/A'
utilwm = window.WindowManagers.Unknown
while not _wmrunning:
    w = ewmh.get_supporting_wm_check(conn, root).reply()
    if w:
        childw = ewmh.get_supporting_wm_check(conn, w).reply()
        if childw == w:
            _wmrunning = True
            wm = ewmh.get_wm_name(conn, childw).reply()
            if wm.lower() == 'openbox':
                utilwm = window.WindowManagers.Openbox
            elif wm.lower() == 'kwin':
                utilwm = window.WindowManagers.KWin

            print '%s window manager is running...' % wm
            sys.stdout.flush()

    if not _wmrunning:
        time.sleep(1)

xinerama.init(conn)

root_geom = ewmh.get_desktop_geometry(conn, root).reply()
monitors = xinerama.get_monitors()
desk_num = ewmh.get_number_of_desktops(conn, root).reply()
activewin = ewmh.get_active_window(conn, root).reply()
desktop = ewmh.get_current_desktop(conn, root).reply()
visibles = ewmh.get_visible_desktops(conn, root).reply()
stacking = ewmh.get_client_list_stacking(conn, root).reply()
workarea = []

def quit():
    print 'Exiting...'
    sys.exit(0)

def cb_property_notify(e):
    global activewin, desk_num, desktop, monitors, root_geom, stacking, visibles

    aname = util.get_atom_name(conn, e.atom)
    if aname == '_NET_DESKTOP_GEOMETRY':
        root_geom = ewmh.get_desktop_geometry(conn, root).reply()
        monitors = xinerama.get_monitors()
    elif aname == '_NET_ACTIVE_WINDOW':
        activewin = ewmh.get_active_window(conn, root).reply()
    elif aname == '_NET_CURRENT_DESKTOP':
        desktop = ewmh.get_current_desktop(conn, root).reply()
    elif aname == '_NET_VISIBLE_DESKTOPS':
        visibles = ewmh.get_visible_desktops(conn, root).reply()
    elif aname == '_NET_NUMBER_OF_DESKTOPS':
        desk_num = ewmh.get_number_of_desktops(conn, root).reply()
    elif aname == '_NET_CLIENT_LIST_STACKING':
        stacking = ewmh.get_client_list_stacking(conn, root).reply()
    elif aname == '_NET_WORKAREA':
        rect.update_workarea()

window.listen(conn, root, ['PropertyChange'])
event.connect('PropertyNotify', root, cb_property_notify)

rect.update_workarea()

