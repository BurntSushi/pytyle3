import time

import xcb.xproto

import xpybutil
import xpybutil.event as event
import xpybutil.ewmh as ewmh
import xpybutil.motif as motif
import xpybutil.icccm as icccm
import xpybutil.rect as rect
import xpybutil.util as util
import xpybutil.window as window

from debug import debug

import config
import state
import tile

clients = {}
ignore = [] # Some clients are never gunna make it...

class Client(object):
    def __init__(self, wid):
        self.wid = wid

        self.name = ewmh.get_wm_name(self.wid).reply() or 'N/A'
        debug('Connecting to %s' % self)

        window.listen(self.wid, 'PropertyChange', 'FocusChange')
        event.connect('PropertyNotify', self.wid, self.cb_property_notify)
        event.connect('FocusIn', self.wid, self.cb_focus_in)
        event.connect('FocusOut', self.wid, self.cb_focus_out)

        # This connects to the parent window (decorations)
        # We get all resize AND move events... might be too much
        self.parentid = window.get_parent_window(self.wid)
        window.listen(self.parentid, 'StructureNotify')
        event.connect('ConfigureNotify', self.parentid, 
                      self.cb_configure_notify)

        # A window should only be floating if that is default
        self.floating = getattr(config, 'floats_default', False)

        # Not currently in a "moving" state
        self.moving = False

        # Load some data
        self.desk = ewmh.get_wm_desktop(self.wid).reply()

        # Add it to this desktop's tilers
        tile.update_client_add(self)

        # First cut at saving client geometry
        self.save()

    def remove(self):
        tile.update_client_removal(self)
        debug('Disconnecting from %s' % self)
        event.disconnect('ConfigureNotify', self.parentid)
        event.disconnect('PropertyNotify', self.wid)
        event.disconnect('FocusIn', self.wid)
        event.disconnect('FocusOut', self.wid)

    def activate(self):
        ewmh.request_active_window_checked(self.wid, source=1).check()

    def unmaximize(self):
        vatom = util.get_atom('_NET_WM_STATE_MAXIMIZED_VERT')
        hatom = util.get_atom('_NET_WM_STATE_MAXIMIZED_HORZ')
        ewmh.request_wm_state_checked(self.wid, 0, vatom, hatom).check()

    def save(self):
        self.saved_geom = window.get_geometry(self.wid)
        self.saved_state = ewmh.get_wm_state(self.wid).reply()

    def restore(self):
        debug('Restoring %s' % self)
        if getattr(config, 'remove_decorations', False):
            motif.set_hints_checked(self.wid,2,decoration=1).check()
        if getattr(config, 'tiles_below', False):
            ewmh.request_wm_state_checked(self.wid,0,util.get_atom('_NET_WM_STATE_BELOW')).check()
        if self.saved_state:
            fullymaxed = False
            vatom = util.get_atom('_NET_WM_STATE_MAXIMIZED_VERT')
            hatom = util.get_atom('_NET_WM_STATE_MAXIMIZED_HORZ')

            if vatom in self.saved_state and hatom in self.saved_state:
                fullymaxed = True
                ewmh.request_wm_state_checked(self.wid, 1, vatom, hatom).check()
            elif vatom in self.saved_state:
                ewmh.request_wm_state_checked(self.wid, 1, vatom).check()
            elif hatom in self.saved_state:
                ewmh.request_wm_state_checked(self.wid, 1, hatom).check()

            # No need to continue if we've fully maximized the window
            if fullymaxed:
                return
            
        mnow = rect.get_monitor_area(window.get_geometry(self.wid),
                                     state.monitors)
        mold = rect.get_monitor_area(self.saved_geom, state.monitors)

        x, y, w, h = self.saved_geom

        # What if the client is on a monitor different than what it was before?
        # Use the same algorithm in Openbox to convert one monitor's 
        # coordinates to another.
        if mnow != mold:
            nowx, nowy, noww, nowh = mnow
            oldx, oldy, oldw, oldh = mold

            xrat, yrat = float(noww) / float(oldw), float(nowh) / float(oldh)

            x = nowx + (x - oldx) * xrat
            y = nowy + (y - oldy) * yrat
            w *= xrat
            h *= yrat

        window.moveresize(self.wid, x, y, w, h)

    def moveresize(self, x=None, y=None, w=None, h=None):
        # Ignore this if the user is moving the window...
        if self.moving:
            print 'Sorry but %s is moving...' % self
            return

        try:
            window.moveresize(self.wid, x, y, w, h)
        except:
            pass

    def is_button_pressed(self):
        try:
            pointer = xpybutil.conn.core.QueryPointer(self.wid).reply()
            if pointer is None:
                return False

            if (xcb.xproto.KeyButMask.Button1 & pointer.mask or
                xcb.xproto.KeyButMask.Button3 & pointer.mask):
                return True
        except xcb.xproto.BadWindow:
            pass

        return False

    def cb_focus_in(self, e):
        if self.moving and e.mode == xcb.xproto.NotifyMode.Ungrab:
            state.GRAB = None
            self.moving = False
            tile.update_client_moved(self)

    def cb_focus_out(self, e):
        if e.mode == xcb.xproto.NotifyMode.Grab:
            state.GRAB = self

    def cb_configure_notify(self, e):
        if state.GRAB is self and self.is_button_pressed():
            self.moving = True

    def cb_property_notify(self, e):
        aname = util.get_atom_name(e.atom)

        try:
            if aname == '_NET_WM_DESKTOP':
                if should_ignore(self.wid):
                    untrack_client(self.wid)
                    return

                olddesk = self.desk
                self.desk = ewmh.get_wm_desktop(self.wid).reply()

                if self.desk is not None and self.desk != olddesk:
                    tile.update_client_desktop(self, olddesk)
                else:
                    self.desk = olddesk
            elif aname == '_NET_WM_STATE':
                if should_ignore(self.wid):
                    untrack_client(self.wid)
                    return
        except xcb.xproto.BadWindow:
            pass # S'ok...

    def __str__(self):
        return '{%s (%d)}' % (self.name[0:30], self.wid)

def update_clients():
    client_list = ewmh.get_client_list_stacking().reply()
    client_list = list(reversed(client_list))
    for c in client_list:
        if c not in clients:
            track_client(c)
    for c in clients.keys():
        if c not in client_list:
            untrack_client(c)

def track_client(client):
    assert client not in clients

    try:
        if not should_ignore(client):
            if state.PYTYLE_STATE == 'running':
                # This is truly unfortunate and only seems to be necessary when
                # a client comes back from an iconified state. This causes a 
                # slight lag when a new window is mapped, though.
                time.sleep(0.2)

            clients[client] = Client(client)
    except xcb.xproto.BadWindow:
        debug('Window %s was destroyed before we could finish inspecting it. '
              'Untracking it...' % client)
        untrack_client(client)

def untrack_client(client):
    if client not in clients:
        return

    c = clients[client]
    del clients[client]
    c.remove()

def should_ignore(client):
    # Don't waste time on clients we'll never possibly tile
    if client in ignore:
        return True

    nm = ewmh.get_wm_name(client).reply()

    wm_class = icccm.get_wm_class(client).reply()
    if wm_class is not None:
        try:
            inst, cls = wm_class
            matchNames = set([inst.lower(), cls.lower()])

            if matchNames.intersection(config.ignore):
                debug('Ignoring %s because it is in the ignore list' % nm)
                return True

            if hasattr(config, 'tile_only') and config.tile_only:
              if not matchNames.intersection(config.tile_only):
                debug('Ignoring %s because it is not in the tile_only '
                      'list' % nm)
                return True
        except ValueError:
            pass

    if icccm.get_wm_transient_for(client).reply() is not None:
        debug('Ignoring %s because it is transient' % nm)
        ignore.append(client)
        return True

    wtype = ewmh.get_wm_window_type(client).reply()
    if wtype:
        for atom in wtype:
            aname = util.get_atom_name(atom)

            if aname in ('_NET_WM_WINDOW_TYPE_DESKTOP',
                         '_NET_WM_WINDOW_TYPE_DOCK',
                         '_NET_WM_WINDOW_TYPE_TOOLBAR',
                         '_NET_WM_WINDOW_TYPE_MENU',
                         '_NET_WM_WINDOW_TYPE_UTILITY',
                         '_NET_WM_WINDOW_TYPE_SPLASH',
                         '_NET_WM_WINDOW_TYPE_DIALOG',
                         '_NET_WM_WINDOW_TYPE_DROPDOWN_MENU',
                         '_NET_WM_WINDOW_TYPE_POPUP_MENU',
                         '_NET_WM_WINDOW_TYPE_TOOLTIP',
                         '_NET_WM_WINDOW_TYPE_NOTIFICATION',
                         '_NET_WM_WINDOW_TYPE_COMBO', 
                         '_NET_WM_WINDOW_TYPE_DND'):
                debug('Ignoring %s because it has type %s' % (nm, aname))
                ignore.append(client)
                return True

    wstate = ewmh.get_wm_state(client).reply()
    if wstate is None:
        debug('Ignoring %s because it does not have a state' % nm)
        return True

    for atom in wstate:
        aname = util.get_atom_name(atom)

        # For now, while I decide how to handle these guys
        if aname == '_NET_WM_STATE_STICKY':
            debug('Ignoring %s because it is sticky and they are weird' % nm)
            return True
        if aname in ('_NET_WM_STATE_SHADED', '_NET_WM_STATE_HIDDEN',
                     '_NET_WM_STATE_FULLSCREEN', '_NET_WM_STATE_MODAL'):
            debug('Ignoring %s because it has state %s' % (nm, aname))
            return True

    d = ewmh.get_wm_desktop(client).reply()
    if d == 0xffffffff:
        debug('Ignoring %s because it\'s on all desktops' \
              '(not implemented)' % nm)
        return True

    return False

def cb_property_notify(e):
    aname = util.get_atom_name(e.atom)

    if aname == '_NET_CLIENT_LIST_STACKING':
        update_clients()

event.connect('PropertyNotify', xpybutil.root, cb_property_notify)

