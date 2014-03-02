import sys
import time

import xpybutil
import xpybutil.event as event
import xpybutil.ewmh as ewmh
import xpybutil.rect as rect
import xpybutil.util as util
import xpybutil.window as window
import xpybutil.xinerama as xinerama

import config

PYTYLE_STATE = 'startup'
GRAB = None

_wmrunning = False

wm = 'N/A'
utilwm = window.WindowManagers.Unknown
while not _wmrunning:
    w = ewmh.get_supporting_wm_check(xpybutil.root).reply()
    if w:
        childw = ewmh.get_supporting_wm_check(w).reply()
        if childw == w:
            _wmrunning = True
            wm = ewmh.get_wm_name(childw).reply()
            if wm.lower() == 'openbox':
                utilwm = window.WindowManagers.Openbox
            elif wm.lower() == 'kwin':
                utilwm = window.WindowManagers.KWin

            print '%s window manager is running...' % wm
            sys.stdout.flush()

    if not _wmrunning:
        time.sleep(1)

root_geom = ewmh.get_desktop_geometry().reply()
monitors = xinerama.get_monitors()
phys_monitors = xinerama.get_physical_mapping(monitors)
desk_num = ewmh.get_number_of_desktops().reply()
activewin = ewmh.get_active_window().reply()
desktop = ewmh.get_current_desktop().reply()
visibles = ewmh.get_visible_desktops().reply() or [desktop]
stacking = ewmh.get_client_list_stacking().reply()
workarea = []

def quit():
    print 'Exiting...'
    import tile
    for tiler in tile.tilers:
        tile.get_active_tiler(tiler)[0].untile()
    sys.exit(0)

def update_workarea():
    '''
    We update the current workarea either by autodetecting struts, or by
    using margins specified in the config file. Never both, though.
    '''
    global workarea

    if hasattr(config, 'use_margins') and config.use_margins:
        workarea = monitors[:]
        for physm, margins in enumerate(config.margins):
            i = phys_monitors[physm]
            mx, my, mw, mh = workarea[i]
            workarea[i] = (mx + margins['left'], my + margins['top'],
                           mw - (margins['left'] + margins['right']),
                           mh - (margins['top'] + margins['bottom']))
    else:
        workarea = rect.monitor_rects(monitors)

def cb_property_notify(e):
    global activewin, desk_num, desktop, monitors, phys_monitors, root_geom, \
           stacking, visibles, workarea

    aname = util.get_atom_name(e.atom)
    if aname == '_NET_DESKTOP_GEOMETRY':
        root_geom = ewmh.get_desktop_geometry().reply()
        monitors = xinerama.get_monitors()
        phys_monitors = xinerama.get_physical_mapping(monitors)
    elif aname == '_NET_ACTIVE_WINDOW':
        activewin = ewmh.get_active_window().reply()
    elif aname == '_NET_CURRENT_DESKTOP':
        desktop = ewmh.get_current_desktop().reply()
        if visibles is None or len(visibles) == 1:
            visibles = [desktop]
    elif aname == '_NET_VISIBLE_DESKTOPS':
        visibles = ewmh.get_visible_desktops().reply()
    elif aname == '_NET_NUMBER_OF_DESKTOPS':
        desk_num = ewmh.get_number_of_desktops().reply()
    elif aname == '_NET_CLIENT_LIST_STACKING':
        stacking = ewmh.get_client_list_stacking().reply()
    elif aname == '_NET_WORKAREA':
        update_workarea()

window.listen(xpybutil.root, 'PropertyChange')
event.connect('PropertyNotify', xpybutil.root, cb_property_notify)

update_workarea()

