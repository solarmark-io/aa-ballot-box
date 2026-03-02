"""Admin models"""
from django.contrib import admin
from .models import Ballot, BallotOption, Vote

class OptionInline(admin.TabularInline):
    model = BallotOption
    extra = 2 # Shows 2 blank option fields by default

@admin.register(Ballot)
class BallotAdmin(admin.ModelAdmin):
    list_display = ('title', 'closes_at', 'is_active')
    inlines = [OptionInline]
    filter_horizontal = ('allowed_groups',) # Creates a drag-and-drop box for AA groups

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'ballot', 'option', 'timestamp')
    list_filter = ('ballot',)
    readonly_fields = ('user', 'ballot', 'option', 'timestamp') # Prevent tampering