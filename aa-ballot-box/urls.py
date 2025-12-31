"""App URLs"""

# Django
from django.urls import path

# AA Ballot Box App
from ballotbox import views

app_name: str = "ballotbox"  # pylint: disable=invalid-name

urlpatterns = [
    path("", views.index, name="index"),
]
