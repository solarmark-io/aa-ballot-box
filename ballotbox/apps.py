"""App Configuration"""

# Django
from django.apps import AppConfig

# AA Ballot-Box App
from ballotbox import __version__


class ExampleConfig(AppConfig):
    """App Config"""

    name = "ballotbox"
    label = "ballotbox"
    verbose_name = f"Ballot Box v{__version__}"
