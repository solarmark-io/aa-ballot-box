"""Hook into Alliance Auth"""
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import urls
from .models import Ballot

class BallotBoxMenuItem(MenuItemHook):
    """ This class ensures only authorized users will see the menu entry """
    def __init__(self):
        # Setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _('Ballot Box'),
            'fas fa-check-to-slot fa-fw',  # Make sure this matches your preferred icon
            'ballotbox:index',
            navactive=['ballotbox:']
        )

    def render(self, request):
        if request.user.has_perm('ballotbox.basic_access'):
            now = timezone.now()
            # Fetch all currently active measures
            active_ballots = Ballot.objects.filter(closes_at__gt=now)
            
            pending_count = 0
            for b in active_ballots:
                # If they are eligible AND have not cast a vote yet
                if b.is_eligible(request.user) and not b.vote_set.filter(user=request.user).exists():
                    pending_count += 1
            
            # If they have pending votes, display the bubble. Otherwise, hide it.
            if pending_count > 0:
                self.count = pending_count
            else:
                self.count = None
                
            return MenuItemHook.render(self, request)
        return ''

@hooks.register('menu_item_hook')
def register_menu():
    return BallotBoxMenuItem()

@hooks.register('url_hook')
def register_urls():
    return UrlHook(urls, 'ballotbox', r'^ballotbox/')