#
# SmaSh system configuration file
#
# Do not edit this file.
# The file in ~/.smash is reset from smashlib source on every run,
# and thus cannot be edited. To override these values, edit instead
# the user configuration file: ~/.smash/config.py (or inside smash
# type ed_ed).
#
from smashlib.editor import get_editor
print '..loading system config', __file__

get_config = eval('get_config') # shut up the linter

_ = get_config()

# set editor from $EDITOR if possible
_.TerminalInteractiveShell.editor = get_editor()

_.Smash.load_bash_aliases = True
_.Smash.load_bash_functions = True

# load toplevel extensions
################################################################################
_.InteractiveShellApp.extensions.append("smashlib.pysh")
#_.InteractiveShellApp.extensions.append("smashlib.dot_prefilter")
_.InteractiveShellApp.extensions.append("smashlib.ipy_smash")

# every smash component gets it's own verbosity setting.
# this mostly controls the printing of debugging info
################################################################################
_.Smash.verbose = False
_.DoWhatIMean.verbose = False
_.LiquidPrompt.verbose = False
_.ProjectManager.verbose = False
_.ChangeDirHooks.verbose = False
_.VirtualEnvSupport.verbose = False

# cross-cutting verbosity configs
################################################################################
_.Smash.ignore_warnings = True
_.Smash.verbose_events = False

# include various things that used to be
# done in profile_pysh/ipython_config.py
################################################################################
_.InteractiveShell.separate_in = ''
_.InteractiveShell.separate_out = ''
_.InteractiveShell.separate_out2 = ''
_.TerminalIPythonApp.display_banner = False
_.TerminalInteractiveShell.confirm_exit = False

# If False, only the completion results from
# the first non-empty completer will be returned.
################################################################################
_.IPCompleter.merge_completions = False


# load optional smash extensions
#_.InteractiveShellApp.extensions.append('powerline.bindings.ipython.post_0_11')
_.Smash.plugins.append('smashlib.plugins.cli_command_runner')
_.Smash.plugins.append('smashlib.plugins.post_input')
_.Smash.plugins.append('smashlib.plugins.handle_cmd_failure')
_.Smash.plugins.append('smashlib.plugins.liquidprompt')
_.Smash.plugins.append('smashlib.plugins.cd_hooks')
_.Smash.plugins.append('smashlib.plugins.venv')
_.Smash.plugins.append('smashlib.plugins.project_manager')
_.Smash.plugins.append("smashlib.plugins.dwim")
_.Smash.plugins.append("smashlib.plugins.fabric")
_.Smash.plugins.append("smashlib.plugins.python_comp_tools")
_.Smash.plugins.append("smashlib.plugins.autojump")

# setup default configuration for the linter (used by "project manager" plugin)
################################################################################


# setup default configuration for the linter (used by "project manager" plugin)
################################################################################
_.PyLinter.verbose = True
_.PyLinter.ignore_pep8 = True
_.PyLinter.ignore_undefined_names = [
    'get_ipython',
    ['get_config','.*_config.py'],
    ['load_subconfig','.*ipython_config.py'],
]

## configure the liquidprompt extension with some reasonable defaults.
################################################################################
_.LiquidPrompt.float           = True # insert more space around prompt
_.LiquidPrompt.prompt_append='\n> '
_.PromptManager.justify        = False

# configure the project manager extension
################################################################################
projects = _.ProjectManager

# this is safe even when the directories do not exist
projects.search_dirs.append('~/code')
projects.search_dirs.append('~/projects')

# load user's project manager configs from the ~/.smash/etc json
# see docs at: http://mattvonrocketstein.github.io/smash/project_manager.html
from smashlib.config import SmashConfig
config = SmashConfig(_)
config.append_from_etc(projects.search_dirs, 'search_dirs.json')
config.update_from_etc(projects.project_map, 'projects.json')
config.update_from_etc(projects.alias_map, 'aliases.json')
config.update_from_etc(projects.macro_map, 'macros.json')
config.update_from_etc(projects.venv_map, 'venvs.json')

# configure the ipython app
################################################################################
app = _.InteractiveShellApp
app.exec_lines.append("""%rehashx""")
app.exec_lines.append("""ip = get_ipython()""")
app.exec_lines.append("""cfg = ip.config""")
app.exec_lines.append("""_smash = ip._smash""")


# load smash user config.  NB: this must happen last!
################################################################################
from smashlib.config import SmashUserConfig
SmashUserConfig.load(globals())
