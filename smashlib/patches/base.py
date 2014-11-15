""" smashlib.patches.base
"""

class PatchMagic(object):
    """ helper for patching ipython builtin line magics.
        it has to be done this way because ipy.shell.magics_manager
        is no help: the register_function() call can only change
        magics_manager.user_magics
    """
    name = None

    def __init__(self, component):
        self.component = component
        shell = component.smash.shell
        self.smash = component.smash
        self.original = shell.magics_manager.magics['line'][self.name]

    def install(self):
        self.component.shell.magics_manager.magics['line'][self.name] = self