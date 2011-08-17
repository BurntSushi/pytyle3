import abc

import pt3.state as state

class Layout(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, desk):
        self.desk = desk # Should never change
        self.active = False
        self.tiling = False

    @abc.abstractmethod
    def add(self, c): pass

    @abc.abstractmethod
    def remove(self, c): pass

    @abc.abstractmethod
    def tile(self): pass

    @abc.abstractmethod
    def untile(self): pass

    @abc.abstractmethod
    def next_client(self): pass

    @abc.abstractmethod
    def switch_next_client(self): pass

    @abc.abstractmethod
    def prev_client(self): pass

    @abc.abstractmethod
    def switch_prev_client(self): pass

    def get_workarea(self):
        if self.desk not in state.visibles:
            return None

        mon = state.workarea[state.visibles.index(self.desk)]

        return mon

    def __str__(self):
        wa = self.get_workarea()
        if wa is None:
            wastr = 'which isn\'t visible'
        else:
            wx, wy, ww, wh = wa
            wastr = 'with workarea (%d, %d) %dx%d' % (wx, wy, ww, wh)

        return '%s on desktop %d %s' % (
                    self.__class__.__name__, self.desk, wastr)

from layout_vert_horz import VerticalLayout, HorizontalLayout

layouts = [VerticalLayout, HorizontalLayout]

