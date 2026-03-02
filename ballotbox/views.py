"""App Views"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from .models import Ballot, BallotOption, Vote

@login_required
@permission_required("ballotbox.basic_access")
def index(request):
    """List available ballots."""
    now = timezone.now()
    active_ballots = Ballot.objects.filter(closes_at__gt=now).order_by('-created_at')
    
    # Only show ballots this specific user has permission to see and hasn't voted on
    available_ballots = [b for b in active_ballots if b.user_can_vote(request.user)]
    
    # Show ballots they have already voted on or have closed
    past_ballots = Ballot.objects.filter(closes_at__lte=now).order_by('-closes_at') | \
                   Ballot.objects.filter(vote__user=request.user)
    
    context = {
        'available_ballots': set(available_ballots),
        'past_ballots': set(past_ballots)
    }
    return render(request, "ballotbox/index.html", context)

@login_required
@permission_required("ballotbox.basic_access")
def vote_view(request, ballot_id):
    ballot = get_object_or_404(Ballot, id=ballot_id)

    if not ballot.is_active():
        messages.error(request, "Voting has closed for this measure.")
        return redirect('ballotbox:index')
    
    if not ballot.user_can_vote(request.user):
        messages.error(request, "You are not eligible to vote or have already voted.")
        return redirect('ballotbox:index')

    if request.method == 'POST':
        option_id = request.POST.get('option')
        option = get_object_or_404(BallotOption, id=option_id, ballot=ballot)
        
        Vote.objects.create(user=request.user, ballot=ballot, option=option)
        messages.success(request, f"Your vote has been recorded securely.")
        return redirect('ballotbox:index')

    return render(request, 'ballotbox/vote.html', {'ballot': ballot})

@login_required
@permission_required('ballotbox.manage_ballots')
def admin_results(request, ballot_id):
    """Leadership view to see results."""
    ballot = get_object_or_404(Ballot, id=ballot_id)
    results = BallotOption.objects.filter(ballot=ballot).annotate(vote_count=Count('vote'))
    total_votes = sum(r.vote_count for r in results)
    
    return render(request, 'ballotbox/results.html', {
        'ballot': ballot, 
        'results': results,
        'total_votes': total_votes
    })