import state
import tile

bindings = {
    'Mod1-a':       tile.cmd('tile'),
    'Mod1-u':       tile.cmd('untile'),
    'Mod1-h':       tile.cmd('decrease_master'),
    'Mod1-l':       tile.cmd('increase_master'),
    'Mod1-j':       tile.cmd('prev_client'),
    'Mod1-k':       tile.cmd('next_client'),
    'Mod1-Shift-j': tile.cmd('switch_prev_client'),
    'Mod1-Shift-k': tile.cmd('switch_next_client'),
    'Mod1-comma':   tile.cmd('remove_master'),
    'Mod1-period':  tile.cmd('add_master'),
    'Mod1-Return':  tile.cmd('make_master'),
    'Mod1-m':       tile.cmd('focus_master'),
    'Mod1-z':       tile.cmd('cycle'),

    'Mod1-q':       tile.debug_state,
    'Mod1-Shift-q': state.quit,
}

