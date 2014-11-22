""" smashlib.ipy_smash

    Defines the main smash plugin, which itself loads and
    allows communications between the other smash plugins.

    TODO: dynamic loading of plugins (use EventfulList)
"""
import os
import cyrusbus
from collections import defaultdict

from IPython.utils.traitlets import List, Bool

from smashlib.v2 import Reporter
from smashlib.channels import C_POST_RUN_INPUT
from smashlib.util.reflect import from_dotpath
from smashlib.util.events import receives_event
from smashlib.util import bash
from smashlib.magics import SmashMagics
from smashlib.channels import C_SMASH_INIT_COMPLETE, C_FAIL, C_FILE_INPUT
from smashlib.plugins.interface import PluginInterface

class Smash(Reporter):
    plugins = List(default_value=[], config=True)
    verbose_events = Bool(False, config=True)
    ignore_warnings = Bool(False, config=True)
    load_bash_aliases = Bool(False, config=True)

    error_handlers = []
    _installed_plugins = {}

    completers = defaultdict(list)

    def system(self, cmd, quiet=False):
        from smashlib.util._fabric import qlocal
        #if not quiet:
        self.report("run: "+cmd)
        return qlocal(cmd, capture=True)
    #system_raw=system
    def init_magics(self):
        self.shell.register_magics(SmashMagics)

    def init_plugins(self):
        _installed_plugins = {}
        for dotpath in self.plugins:
            mod = from_dotpath(dotpath)
            ext_name = dotpath.split('.')[-1]
            ext_obj = mod.load_ipython_extension(self.shell)
            _installed_plugins[ext_name] = ext_obj
            if ext_obj is None:
                msg = '{0}.load_ipython_extension should return an object'
                msg = msg.format(dotpath)
                self.warning(msg)
        self._installed_plugins = _installed_plugins
        plugin_iface = PluginInterface(self)
        plugin_iface.update()
        get_ipython().user_ns.update(plugins=plugin_iface)
        self.report("loaded plugins:", _installed_plugins.keys())

    def build_argparser(self):
        parser = super(Smash, self).build_argparser()
        parser.add_argument('-c','--command', default='')
        return parser

    def parse_argv(self):
        """ parse arguments recognized by myself,
            then let all the plugins take a stab
            at it.
        """
        main_args, unknown = super(Smash,self).parse_argv()
        ext_objs = self._installed_plugins.values()
        for obj in ext_objs:
            if obj:
                args,unknown = obj.parse_argv()
        if main_args.command:
            def run_command(*args, **kargs):
                self.shell.run_cell(main_args.command)
                self.shell.run_cell('exit')
            self.bus.subscribe(C_SMASH_INIT_COMPLETE, run_command)

    @property
    def project_manager(self):
        return self._installed_plugins['ipy_project_manager']

    def init(self):
        self.shell._smash = self
        self.init_bus()
        self.init_plugins()
        self.parse_argv()

        # TODO: move this to configurable Bool()
        if self.load_bash_aliases:
            for alias, cmd in bash.get_aliases():
                if alias not in 'ed cd'.split(): #HACK
                    self.shell.magic("alias {0} {1}".format(alias,cmd))

        smash_bin = os.path.expanduser('~/.smash/bin')
        if smash_bin not in os.environ['PATH']:
            os.environ['PATH'] =smash_bin + ':' + os.environ['PATH']

        from smashlib.patches.edit import PatchEdit

        PatchEdit(self).install()
        #from smashlib.patches.rehashx import PatchRehashX; PatchRehashX(self).install()
        self.publish(C_SMASH_INIT_COMPLETE, None)

    bus = cyrusbus.Bus()
    def init_bus(self):
        """ note: it is a special case that due to bootstrap ordering,
            @receive_events is not possible for this class.  if you want
            to register event callbacks you'll have to register everything
            the simple way.
        """
        super(Smash, self).init_bus()
        bus = self.bus
        def warning_dep(*args, **kargs):
            raise Exception("dont send warning that way")
        bus.subscribe('warning', warning_dep)
        bus.subscribe(C_POST_RUN_INPUT, self.input_finished_hook)
        bus.subscribe(C_FAIL, self.on_system_fail)

    #@receives_event(C_FAIL)
    def on_system_fail(self, bus, cmd, error):
        def is_path(input):
            if len(input.split())==1 and \
               (input.startswith('./') or \
                input.startswith('~/') or \
                input.startswith('/')):
                return True
        if is_path(cmd):
            self.smash.publish(C_FILE_INPUT, cmd)

    def input_finished_hook(self, bus, raw_finished_input):
        if not raw_finished_input.strip():
            return
        rehash_if = [
            'setup.py develop',
            'pip install',
            'setup.py install',
            'apt-get install']
        for x in rehash_if:
            if x in raw_finished_input:
                self.report("detected possible $PATH changes (rehashing)")
                self.shell.magic('rehashx')

    def add_completer(self, fxn, **kargs):
        from goulash._inspect import get_caller
        self.completers[get_caller(2)['class']].append(fxn)
        get_ipython().set_hook('complete_command', fxn, **kargs)

def load_ipython_extension(ip):
    """ called by %load_ext magic """
    ip = get_ipython()
    ip._smash = Smash(ip)
    return ip._smash

def unload_ipython_extension(ip):
    del ip._smash
