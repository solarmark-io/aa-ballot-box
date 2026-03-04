"""App Views"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from .models import Ballot, BallotOption, Vote

@login_required
@permission_required("ballotbox.basic_access")
@login_required
@permission_required("ballotbox.basic_access")
def index(request):
    now = timezone.now()
    
    # 1. Strictly split by time
    active_ballots = Ballot.objects.filter(closes_at__gt=now).order_by('-created_at')
    closed_ballots = Ballot.objects.filter(closes_at__lte=now).order_by('-closes_at')
    
    available_ballots = []
    for b in active_ballots:
        # Show it if they are eligible OR if they are an admin who needs to monitor it
        if b.is_eligible(request.user) or request.user.has_perm('ballotbox.manage_ballots'):
            b.user_can_vote = b.is_eligible(request.user) # Explicitly pass voting rights to the template
            b.user_vote = Vote.objects.filter(ballot=b, user=request.user).first()
            b.can_view_results = b.user_can_view_results(request.user)
            available_ballots.append(b)
            
    past_ballots = []
    for b in closed_ballots:
        if b.is_eligible(request.user) or request.user.has_perm('ballotbox.manage_ballots'):
            b.can_view_results = b.user_can_view_results(request.user)
            b.user_vote = Vote.objects.filter(ballot=b, user=request.user).first()
            past_ballots.append(b)
            
    return render(request, "ballotbox/index.html", {
        'available_ballots': available_ballots,
        'past_ballots': past_ballots
    })

@login_required
@permission_required("ballotbox.basic_access")
def vote_view(request, ballot_id):
    ballot = get_object_or_404(Ballot, id=ballot_id)

    if not ballot.is_active():
        messages.error(request, "Voting has closed for this measure.")
        return redirect('ballotbox:index')
    
    if not ballot.is_eligible(request.user):
        messages.error(request, "You are not eligible to vote on this measure.")
        return redirect('ballotbox:index')

    current_vote = Vote.objects.filter(ballot=ballot, user=request.user).first()

    if request.method == 'POST':
        option_id = request.POST.get('option')
        option = get_object_or_404(BallotOption, id=option_id, ballot=ballot)
        
        # This will update their existing vote, or create a new one if it's their first time
        Vote.objects.update_or_create(
            user=request.user, ballot=ballot, 
            defaults={'option': option}
        )
        messages.success(request, "Your vote has been recorded securely.")
        return redirect('ballotbox:index')

    return render(request, 'ballotbox/vote.html', {'ballot': ballot, 'current_vote': current_vote})

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
