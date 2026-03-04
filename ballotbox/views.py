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
    
    # Only show active ballots they are eligible for and haven't voted on
    available_ballots = [b for b in active_ballots if b.user_can_vote(request.user)]
    
    # Fetch past/voted ballots
    all_past = Ballot.objects.filter(closes_at__lte=now).order_by('-closes_at') | \
               Ballot.objects.filter(vote__user=request.user)
               
    # Filter past ballots so you only see polls meant for your group/state
    past_ballots = []
    for b in set(all_past):
        if b.is_eligible(request.user) or request.user.has_perm('ballotbox.manage_ballots'):
            # We inject a temporary variable so the HTML template knows whether to render a "View Results" button
            b.can_view_results = b.user_can_view_results(request.user)
            past_ballots.append(b)
    
    context = {
        'available_ballots': available_ballots,
        'past_ballots': past_ballots
    }
    return render(request, "ballotbox/index.html", context)

@login_required
@permission_required("ballotbox.basic_access")
def vote_view(request, ballot_id):
    """View for casting a vote."""
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
        messages.success(request, "Your vote has been recorded securely.")
        return redirect('ballotbox:index')

    return render(request, 'ballotbox/vote.html', {'ballot': ballot})

@login_required
@permission_required('ballotbox.basic_access')
def admin_results(request, ballot_id):
    """View to see results (Public or Admin depending on ballot settings)."""
    ballot = get_object_or_404(Ballot, id=ballot_id)
    
    if not ballot.user_can_view_results(request.user):
        messages.error(request, "You do not have permission to view these results, or they are not public.")
        return redirect('ballotbox:index')
        
    results = BallotOption.objects.filter(ballot=ballot).annotate(vote_count=Count('vote'))
    total_votes = sum(r.vote_count for r in results)
    
    return render(request, 'ballotbox/results.html', {
        'ballot': ballot, 
        'results': results,
        'total_votes': total_votes
    })