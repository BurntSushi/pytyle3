#==============================================================================
# xpybutil - An incomplete xcb-util port plus some extras
# Copyright (C) 2009-2010  Andrew Gallant <andrew@pytyle.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#==============================================================================

import os
import os.path
import sys

from distutils import sysconfig
from distutils.core import setup

try:
    import xpybutil
except:
    print ''
    print 'pager-multihead requires xpybutil'
    print 'See: https://github.com/BurntSushi/xpybutil'
    sys.exit(1)

try:
    import pygtk
    pygtk.require('2.0')
    import gtk
except:
    print ''
    print 'pager-multihead requires pygtk'
    print 'See: http://www.pygtk.org/'
    sys.exit(1)

try:
    import keybinder
except:
    print ''
    print 'pager-multihead requiers python-keybinder'
    print 'See: http://kaizer.se/wiki/keybinder/'
    sys.exit(1)

setup(
    name = 'pager-multihead',
    author = 'Andrew Gallant',
    author_email = 'andrew@pytyle.com',
    version = '0.0.1',
    license = 'GPL',
    description = 'A pager that supports per-monitor desktops',
    long_description = 'See README',
    url = 'https://github.com/BurntSushi/pager-mutlihead',
    platforms = 'POSIX',
    packages = ['pagermh'],
    data_files = [('share/doc/pager-multihead', ['README', 'LICENSE']),
                  ('/etc/xdg/pager-multihead', 
                   ['config.py', 'keymousebind.py'])],
    scripts = ['pager-multihead']
)

