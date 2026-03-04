from django.contrib import admin
from .models import Ballot, BallotOption, Vote

# Define the inline class
class BallotOptionInline(admin.TabularInline):
    model = BallotOption
    extra = 2

# reference it in the main admin class
@admin.register(Ballot)
class BallotAdmin(admin.ModelAdmin):
    list_display = ('title', 'closes_at', 'public_results')
    filter_horizontal = ('allowed_groups', 'allowed_states') 
    inlines = [BallotOptionInline]

# Register the standalone vote model
admin.site.register(Vote)