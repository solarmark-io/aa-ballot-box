"""App Models"""
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone

class Ballot(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Detailed explanation of the measure. Supports Markdown/HTML if your templates allow it.")
    created_at = models.DateTimeField(auto_now_add=True)
    closes_at = models.DateTimeField()
    
    # AA Permissions: Limit who can vote. 
    allowed_groups = models.ManyToManyField(Group, blank=True, help_text="Limit voting to these AA groups. Leave empty for alliance-wide access.")

    class Meta:
        permissions = (("basic_access", "Can access the ballot box"),
                       ("manage_ballots", "Can view all ballot results and manage measures"),)

    def is_active(self):
        return timezone.now() < self.closes_at

    def user_can_vote(self, user):
        if Vote.objects.filter(ballot=self, user=user).exists():
            return False # Already voted
        
        if self.allowed_groups.exists():
            user_groups = user.groups.all()
            if not self.allowed_groups.filter(id__in=user_groups).exists():
                return False # Not in an allowed group
        return True

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