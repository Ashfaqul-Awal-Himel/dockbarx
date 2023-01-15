#!/usr/bin/python3

#   log.py
#
#	Copyright 2008, 2009, 2010 Aleksey Shaferov and Matias Sars
#
#	DockbarX is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	DockbarX is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with dockbar.  If not, see <http://www.gnu.org/licenses/>.

import logging
import logging.handlers
import os
import sys

# To avoid infinite recursion in some cases, e.g. out of disk space
logging.raiseExceptions = False

logging.basicConfig(format="%(message)s", level=logging.DEBUG)
logger = logging.getLogger("DockbarX")
file_handler = None

appdir = None
def get_app_homedir():
    global appdir
    if appdir is not None:
        return appdir
    homedir = os.environ['HOME']
    default = os.path.join(homedir, '.local', 'share')
    appdir = os.path.join(
    os.getenv('XDG_DATA_HOME', default),
    'dockbarx'
    )
    """
    Migration Path
    From "$HOME/.dockbarx" to "${XDG_DATA_HOME:-$HOME/.local/share}/dockbarx"
    """
    old_appdir = os.path.join(homedir, '.dockbarx')
    if os.path.exists(old_appdir) and os.path.isdir(old_appdir):
        try:
            os.rename(old_appdir, appdir)
        except OSError:
            sys.stderr.write(
            "Could not move dir '%s' to '%s'. Move the contents of '%s' to '%s' manually and then remove the first location.\n"
            % (old_appdir, appdir, old_appdir, appdir)
            )
    """
    End Migration Path
    """
    return appdir
    
    
def log_to_file():
    log_dir = os.path.join(get_app_homedir(), "log")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, "dockbarx.log")
    file_handler = logging.handlers.RotatingFileHandler(log_file, "a", 0, 5)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s\t| " + \
                                  "%(asctime)s\t| %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    file_handler.doRollover()


class StdOutWrapper():
    """
        Call wrapper for stdout
    """

    def __init__(self):
        self.message_text = ""
        self.log_this = logger.debug

    def write(self, s):
        if s.startswith("\n") or s.startswith("\r"):
            if self.message_text:
                self.log_this(self.message_text)
                self.message_text = ""
        s = s.lstrip("\r\n")
        if s.endswith("\n") or s.endswith("\r") :
            s = s.rstrip("\r\n")
            self.message_text += s
            if self.message_text:
                self.log_this(self.message_text)
            self.message_text = ""
        else:
            self.message_text +=  s

    def flush(self):
        if file_handler:
            file_handler.flush();
        return

class StdErrWrapper(StdOutWrapper):
    """
        Call wrapper for stderr
    """

    def __init__(self):
        StdOutWrapper.__init__(self)
        self.log_this = logger.error

