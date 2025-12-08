from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from django.utils import timezone
from .form import (TransferForm, ServiceListingForm, ToolForm, EventForm, 
                   ReviewForm, UserRegistrationForm, ProfileForm, ToolBorrowForm)
from .models import (ServiceListing, Tool, Transaction, Event, Review, 
                     Profile, Skill, ToolBorrow)

# ============== HOME & DASHBOARD ==============
def index(request):
    """Homepage showing latest listings, tools, and events"""
    offers = ServiceListing.objects.filter(listing_type='OFFER', is_active=True)[:6]
    requests = ServiceListing.objects.filter(listing_type='REQUEST', is_active=True)[:6]
    tools = Tool.objects.filter(is_available=True)[:6]
    upcoming_events = Event.objects.filter(event_date__gte=timezone.now(), is_active=True)[:3]
    
    context = {
        'offers': offers,
        'requests': requests,
        'tools': tools,
        'upcoming_events': upcoming_events,
    }
    return render(request, 'index.html', context)

@login_required
def dashboard(request):
    """User dashboard with their stats and recent activity"""
    user = request.user
    
    # Ensure profile exists
    if not hasattr(user, 'profile'):
        Profile.objects.create(user=user)
    
    user_transactions = Transaction.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).order_by('-timestamp')[:10]
    
    my_listings = ServiceListing.objects.filter(user=user, is_active=True)
    my_tools = Tool.objects.filter(owner=user)
    my_events = Event.objects.filter(organizer=user)
    joined_events = user.joined_events.filter(event_date__gte=timezone.now())
    
    # Get user's rating
    avg_rating = Review.objects.filter(reviewed_user=user).aggregate(Avg('rating'))['rating__avg']
    
    context = {
        'balance': user.profile.time_credits,
        'transactions': user_transactions,
        'my_listings': my_listings,
        'my_tools': my_tools,
        'my_events': my_events,
        'joined_events': joined_events,
        'avg_rating': avg_rating or 0,
    }
    return render(request, 'dashboard.html', context)

# ============== AUTHENTICATION ==============
def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
        profile_form = ProfileForm()
    
    return render(request, 'registration/register.html', {
        'form': form,
        'profile_form': profile_form
    })

def user_login(request):
    """User login"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')

@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

# ============== PROFILE ==============
@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('view_profile', username=request.user.username)
    else:
        profile_form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'profile/edit_profile.html', {'profile_form': profile_form})

def view_profile(request, username):
    """View user profile"""
    user = get_object_or_404(User, username=username)
    reviews = Review.objects.filter(reviewed_user=user).order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    listings = ServiceListing.objects.filter(user=user, is_active=True)
    tools = Tool.objects.filter(owner=user, is_available=True)
    
    context = {
        'profile_user': user,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'listings': listings,
        'tools': tools,
    }
    return render(request, 'profile/view_profile.html', context)

# ============== TRANSACTIONS ==============
@login_required
def transfer_credits(request):
    """Transfer time credits to another user"""
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            transaction_obj = form.save(commit=False)
            transaction_obj.sender = request.user
            
            # Validation: Check if sender has enough credits
            if request.user.profile.time_credits < transaction_obj.amount:
                messages.error(request, "Insufficient time credits!")
                return redirect('transfer_credits')

            # Prevent sending to self
            if transaction_obj.receiver == request.user:
                messages.error(request, "You cannot send credits to yourself.")
                return redirect('transfer_credits')

            transaction_obj.save()
            messages.success(request, f"Sent {transaction_obj.amount} hrs to {transaction_obj.receiver.username}")
            return redirect('dashboard')
    else:
        form = TransferForm()

    return render(request, 'transfer.html', {'form': form})

# ============== SERVICE LISTINGS ==============
def listing_browse(request):
    """Browse all service listings with filtering"""
    listing_type = request.GET.get('type', 'all')
    search_query = request.GET.get('q', '')
    
    listings = ServiceListing.objects.filter(is_active=True)
    
    if listing_type == 'OFFER':
        listings = listings.filter(listing_type='OFFER')
    elif listing_type == 'REQUEST':
        listings = listings.filter(listing_type='REQUEST')
    
    if search_query:
        listings = listings.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(skills__name__icontains=search_query)
        ).distinct()
    
    context = {
        'listings': listings,
        'listing_type': listing_type,
        'search_query': search_query,
    }
    return render(request, 'listings/browse.html', context)

@login_required
def listing_create(request):
    """Create a new service listing"""
    if request.method == 'POST':
        form = ServiceListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            form.save_m2m()  # Save the many-to-many relationships
            messages.success(request, 'Listing created successfully!')
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = ServiceListingForm()
    
    return render(request, 'listings/create.html', {'form': form})

def listing_detail(request, pk):
    """View listing details"""
    listing = get_object_or_404(ServiceListing, pk=pk)
    context = {'listing': listing}
    return render(request, 'listings/detail.html', context)

@login_required
def listing_edit(request, pk):
    """Edit a service listing"""
    listing = get_object_or_404(ServiceListing, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ServiceListingForm(request.POST, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Listing updated successfully!')
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = ServiceListingForm(instance=listing)
    
    return render(request, 'listings/edit.html', {'form': form, 'listing': listing})

@login_required
def listing_delete(request, pk):
    """Delete a service listing"""
    listing = get_object_or_404(ServiceListing, pk=pk, user=request.user)
    
    if request.method == 'POST':
        listing.is_active = False
        listing.save()
        messages.success(request, 'Listing deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'listings/delete.html', {'listing': listing})

# ============== TOOLS ==============
def tool_browse(request):
    """Browse available tools"""
    search_query = request.GET.get('q', '')
    
    tools = Tool.objects.filter(is_available=True)
    
    if search_query:
        tools = tools.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    context = {
        'tools': tools,
        'search_query': search_query,
    }
    return render(request, 'tools/browse.html', context)

@login_required
def tool_create(request):
    """Add a new tool to the library"""
    if request.method == 'POST':
        form = ToolForm(request.POST, request.FILES)
        if form.is_valid():
            tool = form.save(commit=False)
            tool.owner = request.user
            tool.save()
            messages.success(request, 'Tool added successfully!')
            return redirect('tool_detail', pk=tool.pk)
    else:
        form = ToolForm()
    
    return render(request, 'tools/create.html', {'form': form})

def tool_detail(request, pk):
    """View tool details"""
    tool = get_object_or_404(Tool, pk=pk)
    borrows = ToolBorrow.objects.filter(tool=tool).order_by('-requested_at')[:5]
    
    context = {
        'tool': tool,
        'borrows': borrows,
    }
    return render(request, 'tools/detail.html', context)

@login_required
def tool_request_borrow(request, pk):
    """Request to borrow a tool"""
    tool = get_object_or_404(Tool, pk=pk)
    
    if request.method == 'POST':
        form = ToolBorrowForm(request.POST)
        if form.is_valid():
            borrow = form.save(commit=False)
            borrow.tool = tool
            borrow.borrower = request.user
            borrow.save()
            messages.success(request, f'Borrow request sent to {tool.owner.username}!')
            return redirect('tool_detail', pk=tool.pk)
    else:
        form = ToolBorrowForm()
    
    return render(request, 'tools/request_borrow.html', {'form': form, 'tool': tool})

@login_required
def tool_manage_borrows(request):
    """Manage tool borrow requests (for tool owners)"""
    pending_requests = ToolBorrow.objects.filter(
        tool__owner=request.user,
        status='PENDING'
    )
    
    active_borrows = ToolBorrow.objects.filter(
        tool__owner=request.user,
        status__in=['APPROVED', 'BORROWED']
    )
    
    context = {
        'pending_requests': pending_requests,
        'active_borrows': active_borrows,
    }
    return render(request, 'tools/manage_borrows.html', context)

@login_required
def tool_approve_borrow(request, pk):
    """Approve or reject a borrow request"""
    borrow = get_object_or_404(ToolBorrow, pk=pk, tool__owner=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            borrow.status = 'APPROVED'
            messages.success(request, 'Borrow request approved!')
        elif action == 'reject':
            borrow.status = 'CANCELLED'
            messages.success(request, 'Borrow request rejected.')
        borrow.save()
        return redirect('tool_manage_borrows')
    
    return render(request, 'tools/approve_borrow.html', {'borrow': borrow})

# ============== EVENTS ==============
def event_browse(request):
    """Browse community events"""
    events = Event.objects.filter(
        event_date__gte=timezone.now(),
        is_active=True
    ).order_by('event_date')
    
    context = {'events': events}
    return render(request, 'events/browse.html', context)

@login_required
def event_create(request):
    """Create a new event"""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm()
    
    return render(request, 'events/create.html', {'form': form})

def event_detail(request, pk):
    """View event details"""
    event = get_object_or_404(Event, pk=pk)
    is_participant = request.user.is_authenticated and request.user in event.participants.all()
    
    context = {
        'event': event,
        'is_participant': is_participant,
    }
    return render(request, 'events/detail.html', context)

@login_required
def event_join(request, pk):
    """Join an event"""
    event = get_object_or_404(Event, pk=pk)
    
    if event.max_participants and event.participants.count() >= event.max_participants:
        messages.error(request, 'Event is full!')
    elif request.user in event.participants.all():
        messages.info(request, 'You already joined this event.')
    else:
        event.participants.add(request.user)
        messages.success(request, f'You joined {event.title}!')
    
    return redirect('event_detail', pk=pk)

@login_required
def event_leave(request, pk):
    """Leave an event"""
    event = get_object_or_404(Event, pk=pk)
    
    if request.user in event.participants.all():
        event.participants.remove(request.user)
        messages.success(request, f'You left {event.title}.')
    
    return redirect('event_detail', pk=pk)

# ============== REVIEWS ==============
@login_required
def create_review(request, username):
    """Create a review for another user"""
    reviewed_user = get_object_or_404(User, username=username)
    
    if reviewed_user == request.user:
        messages.error(request, 'You cannot review yourself!')
        return redirect('view_profile', username=username)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.reviewed_user = reviewed_user
            review.save()
            messages.success(request, f'Review for {username} submitted!')
            return redirect('view_profile', username=username)
    else:
        form = ReviewForm()
    
    return render(request, 'reviews/create.html', {
        'form': form,
        'reviewed_user': reviewed_user
    })

# ============== MATCHING ALGORITHM ==============
@login_required
def find_matches(request):
    """Find matching offers/requests for the user"""
    user = request.user
    
    # Get user's requests
    user_requests = ServiceListing.objects.filter(
        user=user, 
        listing_type='REQUEST',
        is_active=True
    )
    
    # Get user's offers
    user_offers = ServiceListing.objects.filter(
        user=user,
        listing_type='OFFER',
        is_active=True
    )
    
    # Find matching offers for user's requests
    matching_offers = []
    for req in user_requests:
        skills = req.skills.all()
        matches = ServiceListing.objects.filter(
            listing_type='OFFER',
            is_active=True,
            skills__in=skills
        ).exclude(user=user).distinct()
        
        for match in matches:
            matching_offers.append({
                'request': req,
                'offer': match,
                'match_score': len(set(req.skills.all()) & set(match.skills.all()))
            })
    
    # Find matching requests for user's offers
    matching_requests = []
    for offer in user_offers:
        skills = offer.skills.all()
        matches = ServiceListing.objects.filter(
            listing_type='REQUEST',
            is_active=True,
            skills__in=skills
        ).exclude(user=user).distinct()
        
        for match in matches:
            matching_requests.append({
                'offer': offer,
                'request': match,
                'match_score': len(set(offer.skills.all()) & set(match.skills.all()))
            })
    
    # Sort by match score
    matching_offers.sort(key=lambda x: x['match_score'], reverse=True)
    matching_requests.sort(key=lambda x: x['match_score'], reverse=True)
    
    context = {
        'matching_offers': matching_offers[:10],
        'matching_requests': matching_requests[:10],
    }
    return render(request, 'matching/results.html', context)
