import xcb.xproto

import xpybutil.ewmh as ewmh
import xpybutil.window as window

import state

def rect_intersect_area(r1, r2):
    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2
    if x2 < x1 + w1 and x2 + w2 > x1 and y2 < y1 + h1 and y2 + h2 > y1:
        iw = min(x1 + w1 - 1, x2 + w2 - 1) - max(x1, x2) + 1
        ih = min(y1 + h1 - 1, y2 + h2 - 1) - max(y1, y2) + 1
        return iw * ih

    return 0

def get_monitor_area(search):
    marea = 0
    mon = None
    for mx, my, mw, mh in state.monitors:
        a = rect_intersect_area((mx, my, mw, mh), search)
        if a > marea:
            marea = a
            mon = (mx, my, mw, mh)

    return mon

def update_workarea():
    mons = state.monitors # alias
    wa = mons[:]

    clients = ewmh.get_client_list().reply()

    log = [] # Identical struts should be ignored

    for c in clients:
        try:
            cx, cy, cw, ch = window.get_geometry(c)
        except xcb.xproto.BadWindow:
            continue

        for i, (x, y, w, h) in enumerate(wa):
            if rect_intersect_area((x, y, w, h), (cx, cy, cw, ch)) > 0:
                struts = ewmh.get_wm_strut_partial(c).reply()
                if not struts:
                    struts = ewmh.get_wm_strut(c).reply()

                key = (cx, cy, cw, ch, struts)
                if key in log:
                    continue
                log.append(key)

                if struts and not all([v == 0 for v in struts.itervalues()]):
                    if struts['left'] or struts['right']:
                        if struts['left']:
                            x += cw
                        w -= cw
                    if struts['top'] or struts['bottom']:
                        if struts['top']:
                            y += ch
                        h -= ch
                elif struts:
                    # x/y shouldn't be zero
                    if cx > 0 and w == cx + cw:
                        w -= cw
                    elif cy > 0 and h == cy + ch:
                        h -= ch
                    elif cx > 0 and x == cx:
                        x += cw
                        w -= cw
                    elif cy > 0 and y == cy:
                        y += ch
                        h -= ch

                wa[i] = (x, y, w, h)

    state.workarea = wa

