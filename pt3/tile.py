import sys
import traceback

from xpybutil import conn, root
import xpybutil.event as event
import xpybutil.util as util

from debug import debug

import state
import client
from layouts import layouts

tilers = {}

def debug_state():
    debug('-' * 45)
    for d in tilers:
        if d not in state.visibles:
            continue
        tiler, _ = get_active_tiler(d)
        debug(tiler)
        debug(tiler.store)
        debug('-' * 45)

def cmd(action):
    def _cmd():
        assert state.desktop in tilers

        tiler, _ = get_active_tiler(state.desktop)

        if action == 'tile':
            if not tiler.tiling:
                for c in tiler.store.masters + tiler.store.slaves:
                    c.save()
                    c.unmaximize()
            tiler.tile()
        elif tiler.tiling:
            getattr(tiler, action)()

    return _cmd

def get_active_tiler(desk):
    assert desk in tilers

    for i, tiler in enumerate(tilers[desk]):
        if tiler.active:
            return tiler, i

def update_client_desktop(c, olddesk):
    assert c.desk in tilers

    if olddesk in tilers:
        for tiler in tilers[olddesk]:
            tiler.remove(c)

    for tiler in tilers[c.desk]:
        tiler.add(c)

def update_client_add(c):
    assert c.desk in tilers
    
    for tiler in tilers[c.desk]:
        tiler.add(c)

def update_client_removal(c):
    assert c.desk in tilers

    for tiler in tilers[c.desk]:
        tiler.remove(c)

def update_tilers():
    for d in xrange(state.desk_num):
        if d not in tilers:
            tilers[d] = []
            for lay in layouts:
                t = lay(d)
                tilers[d].append(t)
            tilers[d][0].active = True
    for d in tilers.keys():
        if d >= state.desk_num:
            del tilers[d]

def cb_property_notify(e):
    aname = util.get_atom_name(conn, e.atom)

    if aname == '_NET_NUMBER_OF_DESKTOPS':
        update_tilers()
    elif aname == '_NET_VISIBLE_DESKTOPS':
        for d in state.visibles:
            tiler, _ = get_active_tiler(d)
            if tiler.tiling:
                tiler.tile()

event.connect('PropertyNotify', root, cb_property_notify)

