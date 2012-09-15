""" ipy_smash_aliases

    general shell aliases.  this stuff is somewhat idiosyncratic
    to my own needs, but it's kind of just a place to throw your
    old bash aliases so transitioning to smash isn't too painful

    TODO: these aliases may not survive a "rehash" when proj is activated?
"""

def install_aliases():
    #from smash import aliases
    #for x in  [ 'dhclient sudo dhclient',
    #            'apt-get sudo apt-get',
    #            'dad django-admin.py',
    #            'ls ls --color=auto' ]:
    #    aliases.add(x)
    #aliases.install()

    # FIXME: can't move the import?  plus this is in the wrong file
    from IPython.Magic import Magic
    # avoid an unpleasant surprise:
    # patch reset to clean up the display like bash, not reset the namespace.
    def reset(himself, parameter_s=''):
        __IPYTHON__.system('reset')
        return 'overridden'
    Magic.magic_reset = reset

if __name__=='__smash__':
    install_aliases()
