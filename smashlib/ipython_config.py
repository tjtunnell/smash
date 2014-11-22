#
# SmaSh system configuration file
#
# Do not edit this file.
# This file is reset on every run, and cannot be edited.
# To override these values, edit ~/.smash/config.py instead.
#
print '..loading system config', __file__

get_config = eval('get_config') # shut up the linter

_ = get_config()

# load toplevel extensions
load_subconfig('ipython_config.py', profile='default')
_.InteractiveShellApp.extensions.append("smashlib.pysh")
_.InteractiveShellApp.extensions.append("smashlib.ipy_smash")

# every smash component gets it's own verbosity setting.
# this mostly controls the printing of debugging info
_.Smash.verbose = False
_.DoWhatIMean.verbose = False
_.LiquidPrompt.verbose = False
_.ProjectManager.verbose = False
_.ChangeDirHooks.verbose = False
_.VirtualEnvSupport.verbose = True

# cross-cutting verbosity configs
_.Smash.ignore_warnings = True
_.Smash.verbose_events = False

# configuration for the linter
# which is used by project_manager
_.PyLinter.verbose = True
_.PyLinter.ignore_pep8 = True
_.PyLinter.ignore_undefined_names = [
    'get_ipython',
    ['get_config','.*_config.py'],
    ['load_subconfig','.*ipython_config.py'],
]

# include various things that used to be
# done in profile_pysh/ipython_config.py
_.InteractiveShell.separate_in = ''
_.InteractiveShell.separate_out = ''
_.InteractiveShell.separate_out2 = ''
_.TerminalIPythonApp.display_banner = False
_.TerminalInteractiveShell.confirm_exit = False

# If False, only the completion results from
# the first non-empty completer will be returned.
_.IPCompleter.merge_completions = False


# load optional smash extensions
#_.InteractiveShellApp.extensions.append('powerline.bindings.ipython.post_0_11')
_.Smash.plugins.append('smashlib.plugins.liquidprompt')
_.Smash.plugins.append('smashlib.plugins.cd_hooks')
_.Smash.plugins.append('smashlib.plugins.venv')
_.Smash.plugins.append('smashlib.plugins.project_manager')
_.Smash.plugins.append("smashlib.plugins.dwim")
_.Smash.plugins.append("smashlib.plugins.fabric")
_.Smash.plugins.append("smashlib.plugins.python_comp_tools")
_.Smash.plugins.append("smashlib.plugins.autojump")
#_.Smash.plugins.append('smashlib.ipy_powerline')

## configure the liquidprompt extension with some reasonable defaults.
################################################################################
_.LiquidPrompt.float           = True # insert more space around prompt
_.LiquidPrompt.prompt_append   = "> "
_.PromptManager.justify        = False

# configure the project manager extension
################################################################################
projects = _.ProjectManager
projects.search_dirs.append('~/code')

# configure the ipython app
################################################################################
app = _.InteractiveShellApp
app.exec_lines.append("""%rehashx""")
app.exec_lines.append("""ip = get_ipython()""")
app.exec_lines.append("""cfg = ip.config""")
app.exec_lines.append("""_smash = ip._smash""")


# load smash user config.  this must happen last
################################################################################

from smashlib.config import SmashUserConfig
SmashUserConfig.load(globals())
