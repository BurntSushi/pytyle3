import xpybutil

from pt3.debug import debug

import pt3.config as config
import pt3.client as client
import pt3.state as state
from pt3.layouts import Layout

import store

class OrientLayout(Layout):
    # Start implementing abstract methods
    def __init__(self, desk):
        super(OrientLayout, self).__init__(desk)
        self.store = store.Store()
        self.proportion = 0.5

    def add(self, c):
        debug('%s being added to %s' % (c, self))
        self.store.add(c)

        if self.tiling:
            self.tile()

    def remove(self, c):
        debug('%s being removed from %s' % (c, self))
        self.store.remove(c)

        if self.tiling:
            self.tile()

    def untile(self):
        for c in self.store.masters + self.store.slaves:
            c.restore()
        self.tiling = False
        xpybutil.conn.flush()

    def next_client(self):
        nxt = self._get_next()
        if nxt:
            nxt.activate()

    def switch_next_client(self):
        assert self.tiling

        awin = self._get_focused()
        nxt = self._get_next()
        if None not in (awin, nxt):
            self.store.switch(awin, nxt)
            self.tile()

    def prev_client(self):
        prv = self._get_prev()
        if prv:
            prv.activate()

    def switch_prev_client(self):
        assert self.tiling

        awin = self._get_focused()
        prv = self._get_prev()
        if None not in (awin, prv):
            self.store.switch(awin, prv)
            self.tile()

    def clients(self):
        return self.store.masters + self.store.slaves

    # End abstract methods; begin OrientLayout specific methods

    def decrease_master(self):
        self.proportion = max(0.0, self.proportion - config.proportion_change)
        self.tile()

    def increase_master(self):
        self.proportion = min(1.0, self.proportion + config.proportion_change)
        self.tile()

    def add_master(self):
        assert self.tiling

        self.store.inc_masters(self._get_focused())
        self.tile()

    def remove_master(self):
        assert self.tiling

        self.store.dec_masters(self._get_focused())
        self.tile()

    def make_master(self):
        assert self.tiling

        if not self.store.masters: # no masters right now, so don't add any!
            return

        awin = self._get_focused()
        if awin is None:
            return

        self.store.switch(self.store.masters[0], awin)
        self.tile()

    def focus_master(self):
        assert self.tiling

        if not self.store.masters:
            return

        self.store.masters[0].activate()

    # Begin private methods that should not be called by the user directly

    def _get_focused(self):
        if state.activewin not in client.clients:
            return None

        awin = client.clients[state.activewin]
        if awin not in self.store.masters + self.store.slaves:
            return None

        return awin

    def _get_next(self):
        ms, ss = self.store.masters, self.store.slaves
        awin = self._get_focused()
        if awin is None:
            return None

        nxt = None
        try:
            i = ms.index(awin)
            if i == 0:
                nxt = ss[0] if ss else ms[-1]
            else:
                nxt = ms[i - 1]
        except ValueError:
            i = ss.index(awin)
            if i == len(ss) - 1:
                nxt = ms[-1] if ms else ss[0]
            else:
                nxt = ss[i + 1]

        return nxt

    def _get_prev(self):
        ms, ss = self.store.masters, self.store.slaves
        awin = self._get_focused()
        if awin is None:
            return None

        prv = None
        try:
            i = ms.index(awin)
            if i == len(ms) - 1:
                prv = ss[-1] if ss else ms[0]
            else:
                prv = ms[i + 1]
        except ValueError:
            i = ss.index(awin)
            if i == 0:
                prv = ms[0] if ms else ss[-1]
            else:
                prv = ss[i - 1]

        return prv

class VerticalLayout(OrientLayout):
    def tile(self, save=True):
        if not super(VerticalLayout, self).tile(save):
            return

        wx, wy, ww, wh = self.get_workarea()
        msize = len(self.store.masters)
        ssize = len(self.store.slaves)

        if not msize and not ssize:
            return

        mx = wx
        mw = int(ww * self.proportion)
        sx = mx + mw
        sw = ww - mw

        if mw <= 0 or mw > ww or sw <= 0 or sw > ww:
            return

        if msize:
            mh = wh / msize
            mw = ww if not ssize else mw
            for i, c in enumerate(self.store.masters):
                c.moveresize(x=mx, y=wy + i * mh, w=mw, h=mh)

        if ssize:
            sh = wh / ssize
            if not msize:
                sx, sw = wx, ww
            for i, c in enumerate(self.store.slaves):
                c.moveresize(x=sx, y=wy + i * sh, w=sw, h=sh)

        xpybutil.conn.flush()

class HorizontalLayout(OrientLayout):
    def tile(self, save=True):
        if not super(HorizontalLayout, self).tile(save):
            return

        wx, wy, ww, wh = self.get_workarea()
        msize = len(self.store.masters)
        ssize = len(self.store.slaves)

        if not msize and not ssize:
            return

        my = wy
        mh = int(wh * self.proportion)
        sy = my + mh
        sh = wh - mh

        if mh <= 0 or mh > wh or sh <= 0 or sh > wh:
            return

        if msize:
            mw = ww / msize
            mh = wh if not ssize else mh
            for i, c in enumerate(self.store.masters):
                c.moveresize(x=wx + i * mw, y=my, w=mw, h=mh)

        if ssize:
            sw = ww / ssize
            if not msize:
                sy, sh = wy, wh
            for i, c in enumerate(self.store.slaves):
                c.moveresize(x=wx + i * sw, y=sy, w=sw, h=sh)

        xpybutil.conn.flush()

