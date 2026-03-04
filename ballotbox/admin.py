from django.contrib import admin
from django.forms import CheckboxInput
from django.utils.safestring import mark_safe
from .models import Ballot, BallotOption, Vote

# Custom widget that injects a real-time Javascript listener into the admin page
class PublicResultsWidget(CheckboxInput):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        script = """
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                const publicToggle = document.getElementById("id_public_results");
                const hideRow = document.querySelector(".field-hide_results_until_closed");
                const hideCheckbox = document.getElementById("id_hide_results_until_closed");
                
                function toggleVisibility() {
                    if (publicToggle && hideRow) {
                        if (publicToggle.checked) {
                            hideRow.style.display = ""; // Show the row
                        } else {
                            hideRow.style.display = "none"; // Hide the row
                            if (hideCheckbox) hideCheckbox.checked = false; // Auto-uncheck if hidden
                        }
                    }
                }
                
                if (publicToggle) {
                    publicToggle.addEventListener("change", toggleVisibility);
                    toggleVisibility(); // Run on initial page load
                }
            });
        </script>
        """
        return mark_safe(html + script)

class BallotOptionInline(admin.TabularInline):
    model = BallotOption
    extra = 2

@admin.register(Ballot)
class BallotAdmin(admin.ModelAdmin):
    list_display = ('title', 'closes_at', 'public_results', 'hide_results_until_closed')
    filter_horizontal = ('allowed_groups', 'allowed_states') 
    inlines = [BallotOptionInline]

    # Apply the custom Javascript widget strictly to the public_results checkbox
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'public_results':
            kwargs['widget'] = PublicResultsWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

admin.site.register(Vote)