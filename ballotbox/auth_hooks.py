"""Hook into Alliance Auth"""
from django.utils.translation import gettext_lazy as _
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook
from ballotbox import urls

class BallotBoxMenuItem(MenuItemHook):
    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _("Ballot Box"),
            "fas fa-vote-yea fa-fw",
            "ballotbox:index", # Fixed routing
            navactive=["ballotbox:"], # Fixed routing
        )

    def render(self, request):
        if request.user.has_perm("ballotbox.basic_access"): # Fixed permission
            return MenuItemHook.render(self, request)
        return ""

@hooks.register("menu_item_hook")
def register_menu():
    return BallotBoxMenuItem()

@hooks.register("url_hook")
def register_urls():
    # Fixed URL routing namespace
    return UrlHook(urls, "ballotbox", r"^ballotbox/")