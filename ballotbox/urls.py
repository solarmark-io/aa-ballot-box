"""App URLs"""
from django.urls import path
from ballotbox import views

app_name = "ballotbox"

urlpatterns = [
    path("", views.index, name="index"),
    path("vote/<int:ballot_id>/", views.vote_view, name="vote"),
    path("results/<int:ballot_id>/", views.admin_results, name="results"),
]