"""
"""
import os
opj=os.path.join
ope=os.path.exists

from smashlib.projects import Project, COMMAND_NAME
from smashlib.util import report, post_hook_for_magic
from smashlib.smash_plugin import SmashPlugin

class D(object):
    @property
    def apps(self):
        from django.db.models.loading import AppCache
        appcache = AppCache()
        return appcache.get_apps()
    @property
    def models(self):
        """ Helper to get all the models in a dictionary.
            NOTE: this triggers django autodiscovery, obv
        """
        from django.db.models.loading import AppCache
        appcache = AppCache()
        return dict( [ [ m.__name__, m] \
                       for m in appcache.get_models() ] )

def update_models():
    """ find all the models in INSTALLED_APPS,
        inject them and their lowercase equivalents
        into the IPython namespace
    """

def look_for_project(_dir=None):
    """ returns True if dir looks like a django project """
    _dir = _dir or os.getcwd()
    if all([ope(opj(_dir, 'settings.py')),]):
        return True
    return False

def look_for_app(_dir=None):
    """ returns True if dir looks like a django app"""
    _dir = _dir or os.getcwd()
    if all([ope(opj(_dir, 'urls.py')),
            ope(opj(_dir, 'models.py'))]):
        return True
    return False

class Plugin(SmashPlugin):
    requires = []
    report = report.bookmark_plugin

    def install(self):
        #self.contribute('update_models',update_models)
        post_hook_for_magic('cd', look_for_app)
