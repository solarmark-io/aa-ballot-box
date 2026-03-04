"""App Models"""
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from allianceauth.authentication.models import State

class Ballot(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Detailed explanation of the measure.")
    created_at = models.DateTimeField(auto_now_add=True)
    closes_at = models.DateTimeField()
    
    public_results = models.BooleanField(default=False, help_text="If checked, eligible voters can see the results.")
    hide_results_until_closed = models.BooleanField(default=False, help_text="If checked along with Public Results, voters cannot see the results until the poll closes.")

    allowed_groups = models.ManyToManyField(Group, blank=True, help_text="Limit voting to these AA groups. Leave empty for alliance-wide.")
    allowed_states = models.ManyToManyField(State, blank=True, help_text="Limit voting to these AA states. Leave empty for alliance-wide.")

    class Meta:
        permissions = (
            ("basic_access", "Can access the ballot box"),
            ("manage_ballots", "Can view all ballot results and manage measures"),
        )

    def is_active(self):
        return timezone.now() < self.closes_at

    def is_eligible(self, user):
        if not self.allowed_groups.exists() and not self.allowed_states.exists():
            return True
        if self.allowed_groups.filter(id__in=user.groups.all()).exists():
            return True
        if hasattr(user, 'profile') and self.allowed_states.filter(id=user.profile.state_id).exists():
            return True
        return False

    def user_can_vote(self, user):
        # We no longer block them if they already voted, so they can update it
        return self.is_eligible(user)

    def user_can_view_results(self, user):
        if user.has_perm('ballotbox.manage_ballots'):
            return True
        if self.public_results and self.is_eligible(user):
            # Block standard users from seeing active polls if the hide toggle is checked
            if self.hide_results_until_closed and self.is_active():
                return False
            return True
        return False

    def __str__(self):
        return self.title

class BallotOption(models.Model):
    ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.ballot.title} - {self.text}"

class Vote(models.Model):
    ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    option = models.ForeignKey(BallotOption, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('ballot', 'user') # Strictly 1 vote per user