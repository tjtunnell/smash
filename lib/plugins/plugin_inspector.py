""" plugin that provides a plugin inspector
"""
import asciitable

import smashlib
from smashlib.plugins import Plugins, SmashPlugin
from smashlib.util import list2table

class PluginInspector(Plugins):
    @property
    def __doc__(self):
        """ lists all plugins """
        dat = [ ]
        fnames = [x.filename for x in smashlib.PLUGINS]
        for p in self.all_plugins:
            dat.append([p,
                        p in self.enabled_plugins,
                        p in fnames])
        dat = sorted(dat,key=lambda x:x[0])
        return ("Smash-plugin information: \n\n"
                "  config-file: {0}\n\n").format(self.plugins_json_file) + \
                list2table(dat, header=['name', 'enabled', 'installed'])

class Plugin(SmashPlugin):
    """ """
    def install(self):
        self.contribute('plugins', PluginInspector())