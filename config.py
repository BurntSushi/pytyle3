# A list of windows to ignore... 
# will search both the class and role of the WM_CLASS property
# case-insensitive
ignore = ['gmrun', 'qjackctl', 'viewnior', 'gnome-screenshot', 'mplayer', 'file-roller']

# If this list is non-empty, only windows in the list will be tiled.
# The matching algorithm is precisely the same as for 'ignore'.
tile_only = []

# Whether to enable tiling on startup
tile_on_startup = False

# Whether tiled windows are below others
tiles_below = True

# Whether new windows should tile or float by default (default is False)
floats_default = True

# Whether tiled windows should have their decorations removed
remove_decorations = False

# How much to increment the master area proportion size
proportion_change = 0.05

# If you have panels that don't set struts (*ahem* JWM's panel), then
# setting a margin is the only way to force pytyle not to cover your panels.
# IMPORTANT NOTE: If you set *any* margin, pytyle3 will automatically skip
# all strut auto-detection. So your margins should account for all panels, even
# if the others set struts.
# The format here is to have one set of margins for each active physical
# head. They should be in the following order: Left to right, top to bottom.
# Make sure to set 'use_margins' to True!
use_margins = False
margins = [ {'top': 0, 'bottom': 1, 'left': 0, 'right': 0} ]

# Leave some empty space between windows
gap = 0

# Whether to send any debug information to stdout
debug = False

