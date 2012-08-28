""" smash/ipy_profile_msh

    TODO: install aliases from a file
    TODO: move to hook-based prompt generation if 0.10 supports it
    TODO: replace unix 'which' with a macro that first tries unix-which,
          then, if it fails, tries py.which (from pycmd library)
"""
import os
import sys
import inspect
from optparse import OptionParser

import demjson
from IPython import ipapi

#from ipy_git_completers import install_git_aliases
from ipy_bonus_yeti import clean_namespace, report

VERBOSE      = False
SMASH_DIR    = os.path.dirname(__file__)

ip = ipapi.get()

if VERBOSE: report.smash('importing ipy_profile_msh')

## install various overrides into ip.options. doing it here puts as much code as
## possible actually in pure python instead of in ipython's weird rc format file
################################################################################
OVERRIDE_OPTIONS = dict(
    autoedit_syntax=1,
    confirm_exit = 0,
    prompt_in1= ' \C_Red${__IPYTHON__._cgb()} \C_LightBlue[\C_LightCyan\Y3\C_LightBlue]>',
    include = list(set(ip.options.include + ['ipythonrc-pysh',
                                             'ipythonrc-git-aliases',
                                             'ipythonrc-bash-aliases', ])),

    # 'complete' only completes as much as possible while
    # 'menu-complete'  cycles through all possible completions.
    # readline_parse_and_bind tab: menu-complete
    readline_parse_and_bind = list(set(ip.options.readline_parse_and_bind + \
                              ['tab: complete',
                               '"\C-l": clear-screen',      # control+L
                               '"\b": backward-kill-word',  # control+delete
                               ])),

    # readline_omit__names 1: omit showing any names starting with two __
    # readline_omit__names 2: completion will omit all names beginning with _
    # Regardless, typing a _ after the period and hitting <tab>: 'name._<tab>'
    # will always complete attribute names starting with '_'.
    readline_omit__names = 1,

    # uses emacs daemon to open files for objects. as if by magic
    # try it out.. "%edit SomeModelClass" opens the file!
    editor = 'emacsclient')

for option,val in OVERRIDE_OPTIONS.items():
    setattr(ip.options, option, val)

#from ipy_smash_aliases import install_aliases
#install_aliases()

## clean and begin main loop.  this first removes various common namespace
## collisions between py-modules and unix shell commands. then we clean up the
## strangeness of the command-line arguments (which are skewed due to the odd
## way this script is invoked).  after it's clean, we can do last-minute
## namespace manipulation and then start parsing on the
## command-line and we're finished bootstrapping.
################################################################################
clean_namespace()
sys.argv = sys.argv[1:]
__IPYTHON__.user_ns.update(getfile=inspect.getfile)

## setup project manager
################################################################################
from ipy_project_manager import Project
__manager__ = Project('__main__')
__manager__._ipy_install()

## idiosyncratic stuff.  TODO: this part should not be in this file!
################################################################################
# consider every directory in ~/code to be a "project"
# by default project.<dir-name> simply changes into that
# directory.  you can add activation hooks for things like
# "start venv if present" or "show fab commands if present"
from medley_ipy import load_medley_customizations
from medley_ipy import load_medley_customizations2

# for my personal projects and their customizations.
# ( robotninja requires hammock's activation first )
__manager__.bind_all('~/code')
#__manager__.pre_activate('robotninja',
#                         lambda: __manager__.activate(manager.hammock))

# Medley specific things
__manager__.bind('~/jellydoughnut')
__manager__.bind_all('~/devel',
                     post_activate=load_medley_customizations2,
                     post_invoke=load_medley_customizations,)

def get_parser():
    parser = OptionParser()
    parser.add_option("-v", dest="verbose", action="store_true",
                      default=False, help='more verbose bootstrapping info')
    parser.add_option("--panic", dest="panic",
                      default=False, action="store_true",
                      help="kill all running instances of 'smash'", )
    parser.add_option('-p', "--project",
                      dest="project", default='',
                      help="specify a project to initialize", )
    parser.add_option('-i', '--install',
                      dest='install', default='',
                      help='install new smash module')
    parser.add_option('-l', '--list',
                      action='store_true',dest='list', default=False,
                      help=Plugins.list.__doc__)
    parser.add_option('--enable',
                      dest='enable', default='',
                      help=Plugins.enable.__doc__)
    parser.add_option('--disable',
                      dest='disable', default='',
                      help=Plugins.disable.__doc__)
    return parser

def die():
    import threading
    threading.Thread(target=lambda: os.system('kill -KILL ' + str(os.getpid()))).start()


class Plugins(object):
    plugins_json_file = os.path.join(SMASH_DIR, 'plugins.json')
    report = staticmethod(report.plugins)

    def _set_enabled(self, name, val):
        data = self.plugin_data
        assert name in data,"Bad plugin?"
        data[name] = val
        with open(self.plugins_json_file,'w') as fhandle:
            fhandle.write(demjson.encode(data))

    def disable(self, name):
        """ disable plugin by name """
        self.report('disabling {0}'.format(name))
        self._set_enabled(name, 0)

    def enable(self, name):
        """ enable plugin by name """
        self.report('enabling {0}'.format(name))
        self._set_enabled(name, 1)


    @property
    def plugin_data(self):
        with open(self.plugins_json_file, 'r') as fhandle:
            from_file = demjson.decode(fhandle.read())
        data = from_file.copy()
        for fname in self.possible_plugins:
            if fname not in data:
                data[fname] = 0
        return data

    @property
    def possible_plugins(self):
        return [ fname for fname in os.listdir(SMASH_DIR) if fname.endswith('.py') ]

    def install(self):
        """ """
        # loop thru just enabled plugins
        for plugin_file in self._get_enabled_plugins():
            abs_path_to_plugin = os.path.join(SMASH_DIR, plugin_file)
            assert os.path.exists(abs_path_to_plugin)
            try:
                plugin_module = ''#__import__(os.path.splitext(plugin_file)[0])
                G = globals().copy()
                L = dict(report=self.report)
                G.update(__name__='__smash__')
                execfile(abs_path_to_plugin, G, L)
            except Exception,e:
                self.report("ERROR loading plugin @ `" + plugin_file+'`. Exception follows:')
                self.report('Exception: '+ str([type(e),e]))
            else:
                self.report('installed '+plugin_file+' ok')
                #\n{0}'.format(plugin_module.__doc__))

    def _get_enabled_plugins(self):
        plugins     = self.plugin_data
        enabled     = [ fname for fname in plugins if plugins[fname] == 1 ]
        return enabled

    def list(self, enabled=True, disabled=True):
        """ lists available plugins (from {0}) """.format(SMASH_DIR)
        # reconstructed because `plugins_json_file` may not be up to date with system
        plugins     = self.plugin_data
        enabled     = self._get_enabled_plugins()
        disabled    = disabled and [ fname for fname in plugins if plugins[fname] == 0 ]

        if enabled:
            self.report('enabled plugins')
            for p in enabled: print '  ',p
            print
        if disabled:
            self.report('disabled plugins:')
            for p in disabled: print '  ',p

        if not (enabled or disabled):
            self.report('no plugins at all in '+SMASH_DIR)

        if enabled and not disabled: return enabled
        if disabled and not enabled: return disabled

plugins = Plugins()

try: opts,args = get_parser().parse_args(sys.argv)
except SystemExit, e: die()
else:
    VERBOSE = VERBOSE or opts.verbose
    if VERBOSE:
        report.smash('parsed opts: '+str(eval(str(opts)).items()))
    if opts.project:
        report.cli('parsing project option')
        getattr(__manager__, opts.project).activate
    elif opts.enable:  plugins.enable(opts.enable);   die()
    elif opts.disable: plugins.disable(opts.disable); die()
    elif opts.list:    plugins.list();                 die()
    elif opts.panic:
        print "run this:\n\t","ps aux|grep smash|grep -v grep|awk '{print $2}'|xargs kill -KILL"
        die()

shh = __IPYTHON__.hooks['shutdown_hook']
gop = __IPYTHON__.hooks['pre_prompt_hook']
gop.add(__manager__.check)
shh.add(lambda: __manager__.shutdown())

# patch reset to clean up the display a la bash, not reset the namespace.
from IPython.Magic import Magic
def reset(himself,parameter_s=''):
    __IPYTHON__.system('reset')
    return 'overridden'
Magic.magic_reset = reset

plugins.install()
