from django.contrib import admin
from .models import Ballot, BallotOption, Vote

class BallotOptionInline(admin.TabularInline):
    model = BallotOption
    extra = 2

@admin.register(Ballot)
class BallotAdmin(admin.ModelAdmin):
    # Added the new toggle here
    list_display = ('title', 'closes_at', 'public_results', 'hide_results_until_closed')
    filter_horizontal = ('allowed_groups', 'allowed_states') 
    inlines = [BallotOptionInline]

admin.site.register(Vote)