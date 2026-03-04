"""App Models"""
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from allianceauth.authentication.models import State

class Ballot(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Detailed explanation of the measure. Supports Markdown.")
    created_at = models.DateTimeField(auto_now_add=True)
    closes_at = models.DateTimeField()
    
    # New Visibility Toggle
    public_results = models.BooleanField(default=False, help_text="If checked, eligible voters can see the results after the poll closes.")

    # AA Permissions: Limit who can vote and see this specific poll
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
        """Core check: Does the user meet the group/state requirements?"""
        # If no restrictions are set, anyone with basic_access can participate
        if not self.allowed_groups.exists() and not self.allowed_states.exists():
            return True
        
        # Check if they are in an allowed Group
        if self.allowed_groups.filter(id__in=user.groups.all()).exists():
            return True
            
        # Check if their primary State is allowed
        if hasattr(user, 'profile') and self.allowed_states.filter(id=user.profile.state_id).exists():
            return True
            
        return False

    def user_can_vote(self, user):
        """Check if they are eligible AND haven't voted yet."""
        if Vote.objects.filter(ballot=self, user=user).exists():
            return False 
        return self.is_eligible(user)

    def user_can_view_results(self, user):
        """Check if the user is allowed to see the final results."""
        # Leadership/Admins can ALWAYS see the results (Ignores the public toggle)
        if user.has_perm('ballotbox.manage_ballots'):
            return True
        # Standard users can see it ONLY if it's public AND they were eligible for this specific poll
        if self.public_results and self.is_eligible(user):
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