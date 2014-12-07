""" smashlib.plugins.interface
"""

class myprop(property):
    pass

class PluginInterface(object):
    def __repr__(self):
        return "plugin interface"

    __str__ = __repr__

    def __init__(self, smash):
        self.smash = smash

    @property
    def edit(self):
        self.smash.shell.run_cell('ed_config')

    @property
    def __doc__(self):
        self.update()

    def __qmark__(self):
        """ user-friendly information when the input is "plugins?" """
        out = ['Smash Plugins: ({0} total)'.format(len(self._plugins))]
        for nick in self._plugins:
            out += ['   : {0}'.format(nick)]
        return '\n'.join(out)

    @property
    def _plugins(self):
        return self.smash._installed_plugins

    def update(self):
        tmp = self._plugins
        def fxn(name):
            return self.smash._installed_plugins[name]
        for name in tmp:
            tmp2 = lambda himself: fxn(name)
            #from smashlib.util.reflect import from_dotpath
            #tmp3=from_dotpath(self.smash._installed_plugins[name].__class__.__module__).__doc__
            tmp3 = self.smash._installed_plugins[name].__qmark__()
            tmp2.__doc__ = tmp3
            prop = myprop(tmp2)
            setattr(self.__class__, name, prop)
        whitelist = ['edit','smash', 'update']
        for x in dir(self):
            if not x.startswith('_') and \
                   x not in tmp and \
                   x not in whitelist:
                raise ValueError("interface is not clean")
