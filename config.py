# A list of windows to ignore... they will search
# both the class and role of the WM_CLASS property
# (case-insensitive)
ignore = ['gmrun', 'krunner']

# How much to increment the master area proportion size
proportion_change = 0.02

# If you have panels that don't set struts (*ahem* JWM's panel), then
# setting a margin is the only way to force pytyle not to cover your panels.
# IMPORTANT NOTE: If you set *any* margin, pytyle3 will automatically skip
# all strut auto-detection. So your margins should account for all panels, even
# if the others set struts.
#
# The format here is to have one set of margins for each active physical
# head. They should be in the following order: Left to right, top to bottom.
# Make sure to set 'use_margins' to True!
use_margins = False
margins = [
    {'top': 50, 'bottom': 50, 'left': 50, 'right': 50},
    {'top': 50, 'bottom': 50, 'left': 50, 'right': 50},
    {'top': 50, 'bottom': 50, 'left': 50, 'right': 50},
]

# Whether to send any debug information to stdout
debug = False

