""" smashlib.embed
"""
import sys
import smashlib
from smashlib.util import report, report_if_verbose

from IPython import Shell
from IPython.ipmaker import make_IPython
from IPython.iplib import InteractiveShell
from IPython import ultraTB, ipapi
kill_embedded=Shell.kill_embedded
class SmashInteractiveShell(InteractiveShell):

    def runsource(self, source, filename="<input>", symbol="single"):
        self._smash_last_line = source
        return super(SmashInteractiveShell,self).runsource(
            source, filename=filename, symbol=symbol)

    def showsyntaxerror(self, filename=None):
        # WARNING:
        # this function encounters the error resulting from:
        #   shell.runsource('print 1; echo 1')
        # this function DOES NOT encounter the error resulting from:
        #   shell.runsource('asdasdasdasd')
        #
        # in the first case, it's called with "<ipython console>"
        report.SmaSh('caught error in {0}.  SyntaxError, CommandNotFound?'.format(
            filename))
        default_call = lambda: super(SmashInteractiveShell,self).showsyntaxerror(filename=filename)
        if filename=='<ipython console>':
            return self.smashlib_handle_syntaxerror()
        elif filename=='<smashlib_handle_syntax_error>':
            msg = 'nested error working on "{0}", this might be intended for the shell'
            msg = msg.format(self._smash_last_line)
            report_if_verbose(msg)
            return self.system(self._smash_last_line)
        else:
            return default_call()

    def showtraceback(self, exc_tuple = None,
                          filename=None,tb_offset=None,
                          exception_only=False):
        msg = 'intercepted showtraceback: '
        msg += str([filename, exc_tuple, tb_offset, exception_only])
        report_if_verbose(msg)
        default_call = lambda: super(SmashInteractiveShell, self).showtraceback(
            exc_tuple = exc_tuple, filename=filename, tb_offset=tb_offset,)
        return default_call()

    def smashlib_handle_syntaxerror(self):
        last_line = self._smash_last_line
        from smashlib.util import split_on_unquoted_semicolons
        tmp = split_on_unquoted_semicolons(last_line)
        if len(tmp) > 1:
            report('Treating input as mixed python/shell: {0}'.format(tmp))
            for cmd_component in tmp:
                report('running: {0}'.format(cmd_component))
                self.runsource(cmd_component, filename='<smashlib_handle_syntax_error>')

class SmashEmbed(Shell.IPShellEmbed): # __IPYTHON__?
    # Next function copied nearly verbatim from IPShellEmbed
    def __init__(self, argv=None, banner='',
                 exit_msg=None, rc_override=None,
                 user_ns=None):
        """Note that argv here is a string, NOT a list."""

        # XXX: NEXT BLOCK IS OVERRIDDEN FROM IPYTHON ORIGINAL CODE
        assert argv is None, 'argv is implied because rcfile=$smash_rc'
        argv = ['-rcfile={0}'.format(smashlib._meta['smash_rc'])]
        self.set_banner(banner)
        self.set_exit_msg(exit_msg)
        self.set_dummy_mode(0)

        # sys.displayhook is a global, we need to save the user's original
        # Don't rely on __displayhook__, as the user may have changed that.
        self.sys_displayhook_ori = sys.displayhook

        # save readline completer status
        try:
            #print 'Save completer',sys.ipcompleter  # dbg
            self.sys_ipcompleter_ori = sys.ipcompleter
        except:
            pass # not nested with IPython

        self.IP = make_IPython(argv,rc_override=rc_override,
                               embedded=True,
                               # XXX: NEXT LINE IS OVERRIDDEN FROM IPYTHON ORIGINAL CODE
                               shell_class=SmashInteractiveShell,
                               user_ns=user_ns)
        # XXX: NEXT LINES OVERRIDDEN FROM IPYTHON ORIGINAL CODE
        self.IP._smash_embed = self
        #self._smash_shell = IP

        ip = ipapi.IPApi(self.IP)
        ip.expose_magic("kill_embedded",kill_embedded)

        # copy our own displayhook also
        self.sys_displayhook_embed = sys.displayhook
        # and leave the system's display hook clean
        sys.displayhook = self.sys_displayhook_ori
        # don't use the ipython crash handler so that user exceptions aren't
        # trapped
        sys.excepthook = ultraTB.FormattedTB(color_scheme = self.IP.rc.colors,
                                             mode = self.IP.rc.xmode,
                                             call_pdb = self.IP.rc.pdb)
        self.restore_system_completer()

    # Now self.shell exists