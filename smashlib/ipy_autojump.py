""" smash_autojump

    Adds the magic 'j' or 'jump' command, which tracks and weights every time
    you change directory.

    Basically 'j some_specific_director<tab>' will be made to complete from a
    list or places that are already remembered from prior usage patterns (some
    of which might be really hard to type the absolute path for).
"""

import os
import smashlib
from smashlib.v2 import Reporter
from smashlib.util.events import receives_event
from smashlib.python import ope, opj
from smashlib.channels import C_CD_EVENT
from smashlib.data import SMASH_DIR
from smashlib.util import get_smash
DEFAULT_DATA_FILE = 'autojump.dat'

from smashlib.contrib.autojump import main as _main
from smashlib.contrib.autojump import parse_arguments
from IPython.core.magic import Magics, magics_class, line_magic

from smashlib.data import USER_CONFIG_PATH

mine = lambda x: _main(parse_arguments(args=x))

def j_completer(db, himself, event):
    """ TODO: longest-common-substring algorithm
              etc for even smarter completions """
    path_elements = [ ]
    for x in db.data.keys():
        path_elements += x.split(os.path.sep)
    path_elements = list(set(filter(None, path_elements)))
    return path_elements

def touch_file(_file):
    with open(_file, 'w') as handle:
        pass


@magics_class
class AutojumpMagics(Magics):
    """ main magics for smash """

    @line_magic
    def aj(self, parameter_s=''):
        tmp = parameter_s.split()
        if not tmp[0].startswith('-'):
            result = mine(tmp)
            get_ipython().magic('cd '+result)
        else:
            try:
                return mine(tmp)
            except SystemExit:
                pass


class AutojumpPlugin(Reporter):

    @property
    def datafile(self):
        return opj(SMASH_DIR, DEFAULT_DATA_FILE)

    def touch_datafile(self):
        touch_file(self.datafile)

    def init_magics(self):
        self.shell.register_magics(AutojumpMagics)

    @receives_event(C_CD_EVENT)
    def update_weights(self, new_dir, old_dir):
        """ useful as a post-hook for "cd" commands. it might be
            a good idea to call this after the "jump" command or
            after "pushd" as well, but that's not implemented.
        """
        if self.is_updating and new_dir is not None:
            mine(['-a', new_dir])
            #  increment the weight for that directory
            mine(['-i', ])
            self.report('autojump '+\
                        "incremented jump-weight for '{0}' to {1}".format(
                            new_dir,'?'))

    def install(self):
        #self.smash.set_env('AUTOJUMP_DATA_DIR', SMASH_DIR)
        #from smashlib.contrib.autojump import Database, find_matches
        self.is_updating = True
        return
        # do not move this import (it relies on the set_senv() call)
        #if not ope(self.datafile):
        #    self.touch_datafile()

        # define and bind the "j" command (short for jump)
        # TODO: refactor and use a partial here
        def j(_dir):
            if not _dir:
                print self.db.data
            else:
                matches = find_matches(self.db, [_dir])
                if matches:
                    chose = matches[0]
                    self.report('from {0} matches, chose "{1}"'.format(
                        len(matches),chose))
                    self.is_updating = False
                    get_ipython().ipmagic('pushd ' + chose)
                    self.is_updating = True
                else:
                    report.autojump("no matches found.")
        self.contribute_magic('j', j)
        self.contribute_magic('jump', j)
        self.contribute('db', self.db)

        # turns on the automatic weight-updating.
        self.is_updating = True
        #fxn = lambda himself, event: j_completer(self.db, himself, event)
        #set_complete(fxn, 'j')

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    tmp = AutojumpPlugin(ip)
    tmp.install()
    return tmp

def unload_ipython_extension(ip):
    smash = get_smash()
    # not implemented