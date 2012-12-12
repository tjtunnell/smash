""" smashlib.plugin_manager
"""
import os
import json
import demjson
from IPython import ipapi

from smashlib.util import report,ope
from smashlib.util import die
from smashlib.python import opj, ope
from smashlib.reflect import namedAny

ip = ipapi.get()

# plugins can define their own persistent settings, and they
# should be stored here. by default the schema only consists in
# answering whether a plugin is enabled.
DEFAULT_SCHEMA = dict(enabled=0,)

class PluginManager(object):
    """ smash plugins manager """
    report = staticmethod(report.plugins)

    @property
    def PLUGINS_DIR(self):
        return opj(self.SMASH_DIR, 'plugins')

    @property
    def SMASH_DIR(self):
        from smashlib import SMASH_DIR
        return SMASH_DIR

    @property
    def PLUGINS_CONF(self):
        return os.path.join(self.SMASH_DIR, 'etc', 'plugins.json')

    def __init__(self):
        self.plugins_json_file = self.PLUGINS_CONF
        self._plugins = []
        if self.stale_plugins:
            data = self.plugin_data
            [ data.pop(fname) for fname in self.stale_plugins ]
            self._update_file(data)

    def _update_file(self, data):
        """ json.dumps(, sort_keys=True, indent=4)
        """
        with open(self.plugins_json_file, 'w') as fhandle:
            fhandle.write(json.dumps(data, sort_keys=True, indent=2))

    def _set_enabled(self, name, val):
        """ helper """
        data = self.plugin_data
        if name not in data:
            print "Bad plugin? {0}".format(name)
            from IPython import Shell; Shell.IPShellEmbed(argv=['-noconfirm_exit'])()
        data[name].update(enabled=val)
        self._update_file(data)

    def disable(self, name):
        """ disable plugin by name """
        self.report('disabling {0}'.format(name))
        self._set_enabled(name, 0)

    def enable(self, name):
        """ enable plugin by name """
        self.report('enabling {0}'.format(name))
        self._set_enabled(name, 1)

    def install_plugin_from_fname(self, abs_path_to_plugin):
        G = globals().copy()
        L = dict(report=self.report)
        G.update(__name__='__smash__')
        execfile(abs_path_to_plugin, G, L)
        G.update(**L)
        if 'Plugin' not in G:
            err  = abs_path_to_plugin + ' is old style,'
            err += ' "Plugin" not found in namespace'
            raise Exception, err
        plugin = G['Plugin']()
        rel_fname = os.path.split(abs_path_to_plugin)[-1]
        if not getattr(plugin, 'name', None):
            plugin.name = rel_fname
        plugin.filename = rel_fname
        #plugin.pre_install()
        plugin.install()
        self._plugins.append(plugin)

    def _get_some_plugins(self, name, val):
        plugins     = self.plugin_data
        return [ fname for fname in plugins if plugins[fname][name] == val ]

    @property
    def plugin_data(self):
        """ updates based on files in dir and default schema """
        with open(self.plugins_json_file, 'r') as fhandle:
            try:
                from_file = demjson.decode(fhandle.read())
            except demjson.JSONDecodeError:
                err="error reading json file: "+self.plugins_json_file
                report.ERROR(err)
                import sys
                sys.exit(err)
        data = from_file.copy()
        for fname in self.possible_plugins:
            if fname not in data:
                data[fname] = DEFAULT_SCHEMA
        return data

    @property
    def possible_plugins(self):
        return [ fname for fname in os.listdir(self.PLUGINS_DIR) if fname.endswith('.py') ]
    all_plugins = possible_plugins

    @property
    def enabled_plugins(self):
        """ lists plugins mentioned as enabled in config """
        return self._get_some_plugins('enabled', 1)

    @property
    def disabled_plugins(self):
        """ lists plugins mentioned as disabled in config """
        return self._get_some_plugins('enabled', 0)

    @property
    def stale_plugins(self):
        """ lists plugins mentioned in config but not found on filesystem """
        return set(self.plugin_data.keys())-set(self.possible_plugins)
        stale = []
        for x in self.plugin_data.keys():
            x = opj(self.PLUGINS_DIR, x)
            if not ope(x):
                stale.append(x)
        return stale

    def list(self):
        """ lists available plugins (from {0}) """.format(self.SMASH_DIR)
        # reconstructed because `plugins_json_file` may not be up to date with system
        plugins     = self.plugin_data
        enabled     = self.enabled_plugins
        disabled    = self.disabled_plugins
        if enabled:
            self.report('enabled plugins')
            for p in enabled: print '  ',p
            print
        if disabled:
            self.report('disabled plugins:')
            for p in disabled: print '  ',p
        if not (enabled or disabled):
            self.report('no plugins at all in ' + self.SMASH_DIR)


    def install(self):
        """ install all plugins into the running environment """
        for plugin_file in self.enabled_plugins:
            abs_path_to_plugin = os.path.join(self.PLUGINS_DIR, plugin_file)
            if not ope(abs_path_to_plugin):
                msg = ('Your configuration file @ "{0}" contains an error.  '
                       '"{1}" does not exist')
                msg = msg.format(self.plugins_json_file,
                                 abs_path_to_plugin)
                self.report(msg)
                die()
            else:
               try:
                   self.install_plugin_from_fname(abs_path_to_plugin)
               except Exception, e:
                   self.report("ERROR loading plugin @ `" + \
                               plugin_file+'`. Exception follows:')
                   self.report('Exception: ')
                   print str([type(e), e])
                   raise

        #FIXME: cleaner way to do this back-ref
        import smashlib
        smashlib.PLUGINS = self._plugins


from .smash_plugin import SmashPlugin