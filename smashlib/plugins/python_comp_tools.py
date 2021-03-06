""" smashlib.plugins.python_comp_tools

    This code adds tab completion over tox CLI options,
    and dynamic determination of environments for "tox -e"
"""
import os
from smashlib import get_smash
from smashlib.plugins import Plugin
from smashlib.util._tox import get_tox_envs

from smashlib.completion import opt_completer


def setup_completer(self, event):
    return 'install develop build'.split()


tox_completer = opt_completer('tox')


def tox_env_completer(self, event):
    line = event.line
    if line and line.split()[-1].strip().endswith('-e'):
        return get_tox_envs()


class ToxPlugin(Plugin):

    def install(self):
        self.smash.add_completer(tox_env_completer, re_key='tox .*-e')
        self.smash.add_completer(tox_completer, re_key='tox .*')
        return self


def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    return ToxPlugin(get_ipython()).install()


def unload_ipython_extension(ip):
    plugin_name = os.path.splitext(os.path.split(__file__)[-1])[0]
    raise Exception(plugin_name)
    get_smash().plugins[plugin_name].uninstall()
