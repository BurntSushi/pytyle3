import pt3.config as config
import xpybutil.ewmh as ewmh
import xpybutil.util as util
import xpybutil.motif as motif

class Store(object):
    def __init__(self):
        self.masters, self.slaves, self.floats = [], [], []
        self.mcnt = 1 # Number of masters allowed

    def add(self, c, above=None):
        if c.floating:
            if getattr(config, 'remove_decorations', False):
                motif.set_hints_checked(c.wid,2,decoration=1).check() # add decorations
            if getattr(config, 'tiles_below', False):
                ewmh.request_wm_state_checked(c.wid,0,util.get_atom('_NET_WM_STATE_BELOW')).check()
            self.floats.append(c)
        else:
            #restore window if maximized
			#ewmh.request_wm_state_checked(c.wid,0,util.get_atom('_NET_WM_STATE_MAXIMIZED_VERT')).check()
			#ewmh.request_wm_state_checked(c.wid,0,util.get_atom('_NET_WM_STATE_MAXIMIZED_HORZ')).check()
            if getattr(config, 'remove_decorations', False):
                motif.set_hints_checked(c.wid,2,decoration=2).check() #remove decorations
            if getattr(config, 'tiles_below', False):
                ewmh.request_wm_state_checked(c.wid,1,util.get_atom('_NET_WM_STATE_BELOW')).check()
            if len(self.masters) < self.mcnt:
                if c in self.slaves:
                    self.slaves.remove(c)
                self.masters.append(c)
            elif c not in self.slaves:
                self.slaves.append(c)

    def remove(self, c):
        if c in self.floats:
            self.floats.remove(c)
        else:
            if c in self.masters:
                self.masters.remove(c)
                if len(self.masters) < self.mcnt and self.slaves:
                    self.masters.append(self.slaves.pop(0))
            elif c in self.slaves:
                self.slaves.remove(c)

    def reset(self):
        self.__init__()

    def inc_masters(self, current=None):
        self.mcnt = min(self.mcnt + 1, len(self))
        if len(self.masters) < self.mcnt and self.slaves:
            try:
                newmast = self.slaves.index(current)
            except ValueError:
                newmast = 0
            self.masters.append(self.slaves.pop(newmast))

    def dec_masters(self, current=None):
        self.mcnt = max(self.mcnt - 1, 0)
        if len(self.masters) > self.mcnt:
            try:
                newslav = self.masters.index(current)
            except ValueError:
                newslav = -1
            self.slaves.append(self.masters.pop(newslav))

    def switch(self, c1, c2):
        ms, ss = self.masters, self.slaves # alias
        if c1 in ms and c2 in ms:
            i1, i2 = ms.index(c1), ms.index(c2)
            ms[i1], ms[i2] = ms[i2], ms[i1]
        elif c1 in self.slaves and c2 in self.slaves:
            i1, i2 = ss.index(c1), ss.index(c2)
            ss[i1], ss[i2] = ss[i2], ss[i1]
        elif c1 in ms: # and c2 in self.slaves
            i1, i2 = ms.index(c1), ss.index(c2)
            ms[i1], ss[i2] = ss[i2], ms[i1]
        else: # c1 in ss and c2 in ms
            i1, i2 = ss.index(c1), ms.index(c2)
            ss[i1], ms[i2] = ms[i2], ss[i1]

    def toggle_float(self, c):
        self.remove(c)
        c.floating = not c.floating
        self.add(c)

    def __len__(self):
        return len(self.masters) + len(self.slaves)

    def __str__(self):
        s = ['Masters: %s' % [str(c) for c in self.masters],
             'Slaves: %s' % [str(c) for c in self.slaves]]
        return '\n'.join(s)

