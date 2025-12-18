from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.http import JsonResponse
from decimal import Decimal
from math import radians, cos, sin, asin, sqrt
from .form import (TransferForm, ServiceListingForm, ToolForm, EventForm, 
                   ReviewForm, UserRegistrationForm, ProfileForm, ToolBorrowForm, MessageForm, CreditRequestForm)
from .models import (ServiceListing, Tool, Transaction, Event, Review, 
                     Profile, Skill, ToolBorrow, Conversation, Message, Notification)

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
            try:
                user = form.save()
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
                
                messages.success(request, f'Welcome {user.username}! Your account has been created.')
                login(request, user)
                return redirect('dashboard')
            except Exception as e:
                # If there's an error (like duplicate username), show it to the user
                messages.error(request, 'An error occurred during registration. Please try again.')
                if 'username' in str(e).lower():
                    form.add_error('username', 'This username is already taken.')
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
    # Ensure profile exists
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('view_profile', username=request.user.username)
    else:
        profile_form = ProfileForm(instance=profile)
    
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

@login_required
def tool_edit(request, pk):
    """Edit a tool listing"""
    tool = get_object_or_404(Tool, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = ToolForm(request.POST, request.FILES, instance=tool)
        if form.is_valid():
            form.save()
            messages.success(request, f'{tool.name} updated successfully!')
            return redirect('tool_detail', pk=tool.pk)
    else:
        form = ToolForm(instance=tool)
    
    context = {
        'form': form,
        'tool': tool,
        'is_edit': True,
    }
    return render(request, 'tools/create.html', context)

@login_required
def tool_delete(request, pk):
    """Delete a tool listing"""
    tool = get_object_or_404(Tool, pk=pk, owner=request.user)
    
    # Check if tool has active borrows
    active_borrows = ToolBorrow.objects.filter(tool=tool, status='APPROVED').exists()
    if active_borrows:
        messages.error(request, 'Cannot delete tool with active borrows. Please wait until all borrows are completed.')
        return redirect('tool_detail', pk=pk)
    
    if request.method == 'POST':
        tool_name = tool.name
        tool.delete()
        messages.success(request, f'{tool_name} has been deleted.')
        return redirect('tool_browse')
    
    return render(request, 'tools/delete.html', {'tool': tool})

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
def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    if not all([lat1, lon1, lat2, lon2]):
        return float('inf')  # Return infinity if coordinates are missing
    
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c  # Radius of earth in kilometers
    return km

def find_matches(request):
    """Find matching offers/requests for the user, prioritizing nearby matches"""
    user = request.user
    user_profile = user.profile
    
    # Get user's coordinates
    user_lat = user_profile.latitude
    user_lon = user_profile.longitude
    
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
        ).exclude(user=user).distinct().select_related('user__profile')
        
        for match in matches:
            distance = calculate_distance(
                user_lat, user_lon,
                match.user.profile.latitude, match.user.profile.longitude
            )
            matching_offers.append({
                'request': req,
                'offer': match,
                'match_score': len(set(req.skills.all()) & set(match.skills.all())),
                'distance': distance,
                'distance_display': f"{distance:.1f} km" if distance != float('inf') else "Location not set"
            })
    
    # Find matching requests for user's offers
    matching_requests = []
    for offer in user_offers:
        skills = offer.skills.all()
        matches = ServiceListing.objects.filter(
            listing_type='REQUEST',
            is_active=True,
            skills__in=skills
        ).exclude(user=user).distinct().select_related('user__profile')
        
        for match in matches:
            distance = calculate_distance(
                user_lat, user_lon,
                match.user.profile.latitude, match.user.profile.longitude
            )
            matching_requests.append({
                'offer': offer,
                'request': match,
                'match_score': len(set(offer.skills.all()) & set(match.skills.all())),
                'distance': distance,
                'distance_display': f"{distance:.1f} km" if distance != float('inf') else "Location not set"
            })
    
    # Sort by distance first, then by match score
    matching_offers.sort(key=lambda x: (x['distance'], -x['match_score']))
    matching_requests.sort(key=lambda x: (x['distance'], -x['match_score']))
    
    context = {
        'matching_offers': matching_offers[:10],
        'matching_requests': matching_requests[:10],
        'has_location': user_lat is not None and user_lon is not None,
    }
    return render(request, 'matching/results.html', context)

# ============== MESSAGING & NOTIFICATIONS ==============
@login_required
def inbox(request):
    """View all conversations"""
    # Get all conversations where user is a participant
    conversations = Conversation.objects.filter(
        Q(participant1=request.user) | Q(participant2=request.user)
    ).select_related('participant1', 'participant2', 'listing').prefetch_related('messages')
    
    conversation_list = []
    for conv in conversations:
        other_user = conv.get_other_user(request.user)
        last_message = conv.get_last_message()
        conversation_list.append({
            'conversation': conv,
            'other_user': other_user,
            'last_message': last_message,
            'has_unread': conv.has_unread_for(request.user),
        })
    
    context = {
        'conversations': conversation_list,
        'unread_count': sum(1 for c in conversation_list if c['has_unread']),
    }
    return render(request, 'messages/inbox.html', context)

@login_required
def conversation_detail(request, pk):
    """View a conversation thread and send messages"""
    conversation = get_object_or_404(Conversation, pk=pk)
    
    # Check permission
    if request.user not in [conversation.participant1, conversation.participant2]:
        messages.error(request, 'You do not have permission to view this conversation.')
        return redirect('inbox')
    
    other_user = conversation.get_other_user(request.user)
    
    # Mark all messages as read
    conversation.messages.filter(recipient=request.user, is_read=False).update(is_read=True)
    
    # Handle new message submission
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.recipient = other_user
            if message.requires_response:
                message.response_status = 'PENDING'
            message.save()
            
            # Update conversation timestamp
            conversation.save()  # This triggers auto_now update
            
            # Create notification for recipient
            Notification.objects.create(
                user=other_user,
                notification_type='MESSAGE',
                message=f"{request.user.username} sent you a message",
                link=f"/messages/conversation/{conversation.pk}/"
            )
            
            messages.success(request, 'Message sent!')
            return redirect('conversation_detail', pk=pk)
    else:
        form = MessageForm()
    
    # Get all messages in conversation
    conversation_messages = conversation.messages.all()
    
    context = {
        'conversation': conversation,
        'other_user': other_user,
        'messages': conversation_messages,
        'form': form,
    }
    return render(request, 'messages/conversation.html', context)

@login_required
def start_conversation(request, username=None, listing_id=None):
    """Start a new conversation or redirect to existing one"""
    recipient = None
    listing = None
    
    if username:
        recipient = get_object_or_404(User, username=username)
    if listing_id:
        listing = get_object_or_404(ServiceListing, pk=listing_id)
        recipient = listing.user
    
    if not recipient or recipient == request.user:
        messages.error(request, 'Invalid recipient.')
        return redirect('inbox')
    
    # Check if conversation already exists
    existing_conv = Conversation.objects.filter(
        Q(participant1=request.user, participant2=recipient) |
        Q(participant1=recipient, participant2=request.user),
        listing=listing
    ).first()
    
    if existing_conv:
        return redirect('conversation_detail', pk=existing_conv.pk)
    
    # Create new conversation
    conversation = Conversation.objects.create(
        participant1=request.user,
        participant2=recipient,
        listing=listing
    )
    
    # If there's a listing, send initial message
    if listing:
        initial_body = f"Hi! I'm interested in your listing: {listing.title}"
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            recipient=recipient,
            body=initial_body
        )
        
        # Create notification
        Notification.objects.create(
            user=recipient,
            notification_type='MESSAGE',
            message=f"{request.user.username} sent you a message about {listing.title}",
            link=f"/messages/conversation/{conversation.pk}/"
        )
    
    return redirect('conversation_detail', pk=conversation.pk)

@login_required
def respond_to_message(request, pk, action):
    """Accept or decline a message request"""
    message = get_object_or_404(Message, pk=pk, recipient=request.user)
    
    if not message.requires_response:
        messages.error(request, 'This message does not require a response.')
        return redirect('conversation_detail', pk=message.conversation.pk)
    
    if action == 'accept':
        message.response_status = 'ACCEPTED'
        message.save()
        
        # Create notification for sender
        Notification.objects.create(
            user=message.sender,
            notification_type='LISTING_RESPONSE',
            message=f"{request.user.username} accepted your request",
            link=f"/messages/conversation/{message.conversation.pk}/"
        )
        
        # Send confirmation message back
        Message.objects.create(
            conversation=message.conversation,
            sender=request.user,
            recipient=message.sender,
            body=f"✓ I have accepted your request!"
        )
        
        # Update conversation timestamp
        message.conversation.save()
        
        messages.success(request, 'Request accepted!')
        
    elif action == 'decline':
        message.response_status = 'DECLINED'
        message.save()
        
        # Create notification for sender
        Notification.objects.create(
            user=message.sender,
            notification_type='LISTING_RESPONSE',
            message=f"{request.user.username} declined your request",
            link=f"/messages/conversation/{message.conversation.pk}/"
        )
        
        messages.info(request, 'Request declined.')
    
    return redirect('conversation_detail', pk=message.conversation.pk)

@login_required
def request_credits(request, conversation_pk):
    """Request credits from someone in a conversation"""
    conversation = get_object_or_404(Conversation, pk=conversation_pk)
    
    # Check permission
    if request.user not in [conversation.participant1, conversation.participant2]:
        messages.error(request, 'You do not have permission to access this conversation.')
        return redirect('inbox')
    
    other_user = conversation.get_other_user(request.user)
    
    if request.method == 'POST':
        form = CreditRequestForm(request.POST)
        if form.is_valid():
            # Check if recipient has enough credits
            credit_amount = form.cleaned_data['credit_amount']
            if other_user.profile.time_credits < credit_amount:
                messages.error(request, f'{other_user.username} does not have enough credits ({other_user.profile.time_credits} available).')
                return redirect('conversation_detail', pk=conversation_pk)
            
            # Create credit request message
            credit_message = form.save(commit=False)
            credit_message.conversation = conversation
            credit_message.sender = request.user
            credit_message.recipient = other_user
            credit_message.is_credit_request = True
            credit_message.credit_status = 'PENDING'
            credit_message.save()
            
            # Update conversation timestamp
            conversation.save()
            
            # Create notification
            Notification.objects.create(
                user=other_user,
                notification_type='CREDIT_RECEIVED',
                message=f"{request.user.username} requested {credit_amount} credits from you",
                link=f"/messages/conversation/{conversation.pk}/"
            )
            
            messages.success(request, f'Credit request for {credit_amount} hours sent to {other_user.username}!')
            return redirect('conversation_detail', pk=conversation_pk)
    else:
        form = CreditRequestForm()
    
    context = {
        'form': form,
        'conversation': conversation,
        'other_user': other_user,
    }
    return render(request, 'messages/request_credits.html', context)

@login_required
def respond_to_credit_request(request, message_pk, action):
    """Accept or decline a credit request"""
    credit_message = get_object_or_404(Message, pk=message_pk, recipient=request.user, is_credit_request=True)
    
    if not credit_message.is_credit_request or credit_message.credit_status != 'PENDING':
        messages.error(request, 'Invalid credit request.')
        return redirect('conversation_detail', pk=credit_message.conversation.pk)
    
    if action == 'accept':
        # Check if user still has enough credits
        if request.user.profile.time_credits < credit_message.credit_amount:
            messages.error(request, f'You do not have enough credits. You have {request.user.profile.time_credits} but need {credit_message.credit_amount}.')
            return redirect('conversation_detail', pk=credit_message.conversation.pk)
        
        # Transfer credits
        sender_profile = credit_message.sender.profile
        recipient_profile = request.user.profile
        
        recipient_profile.time_credits -= credit_message.credit_amount
        sender_profile.time_credits += credit_message.credit_amount
        recipient_profile.save()
        sender_profile.save()
        
        # Create transaction record
        Transaction.objects.create(
            sender=request.user,
            recipient=credit_message.sender,
            amount=credit_message.credit_amount,
            description=credit_message.body
        )
        
        # Update message status
        credit_message.credit_status = 'ACCEPTED'
        credit_message.save()
        
        # Send confirmation message
        Message.objects.create(
            conversation=credit_message.conversation,
            sender=request.user,
            recipient=credit_message.sender,
            body=f"✓ I've sent you {credit_message.credit_amount} credits!"
        )
        
        # Update conversation
        credit_message.conversation.save()
        
        # Create notification
        Notification.objects.create(
            user=credit_message.sender,
            notification_type='CREDIT_RECEIVED',
            message=f"{request.user.username} sent you {credit_message.credit_amount} credits!",
            link=f"/messages/conversation/{credit_message.conversation.pk}/"
        )
        
        messages.success(request, f'Successfully sent {credit_message.credit_amount} credits to {credit_message.sender.username}!')
        
    elif action == 'decline':
        credit_message.credit_status = 'DECLINED'
        credit_message.save()
        
        # Create notification
        Notification.objects.create(
            user=credit_message.sender,
            notification_type='CREDIT_RECEIVED',
            message=f"{request.user.username} declined your credit request",
            link=f"/messages/conversation/{credit_message.conversation.pk}/"
        )
        
        messages.info(request, 'Credit request declined.')
    
    return redirect('conversation_detail', pk=credit_message.conversation.pk)

@login_required
def notifications(request):
    """View all notifications and pending tool borrow requests"""
    # Get notifications queryset (not sliced yet)
    user_notifications = Notification.objects.filter(user=request.user)
    
    # Mark all as read if requested
    if request.GET.get('mark_read'):
        user_notifications.update(is_read=True)
        return redirect('notifications')
    
    # Get pending tool borrow requests where user is the tool owner
    pending_borrow_requests = ToolBorrow.objects.filter(
        tool__owner=request.user,
        status='PENDING'
    ).select_related('borrower', 'tool')
    
    # Get unread count before slicing
    unread_count = user_notifications.filter(is_read=False).count()
    
    context = {
        'notifications': user_notifications[:50],  # Now slice after filtering
        'pending_borrow_requests': pending_borrow_requests,
        'unread_count': unread_count,
    }
    return render(request, 'messages/notifications.html', context)

@login_required
def respond_to_borrow_request(request, borrow_id, action):
    """Accept or decline a tool borrow request"""
    borrow_request = get_object_or_404(ToolBorrow, pk=borrow_id, tool__owner=request.user)
    
    if borrow_request.status != 'PENDING':
        messages.error(request, 'This request has already been processed.')
        return redirect('notifications')
    
    if action == 'accept':
        borrow_request.status = 'APPROVED'
        borrow_request.tool.is_available = False
        borrow_request.tool.save()
        borrow_request.save()
        
        # Create notification for borrower
        Notification.objects.create(
            user=borrow_request.borrower,
            notification_type='TOOL_APPROVED',
            message=f"{request.user.username} approved your request to borrow {borrow_request.tool.name}",
            link=f"/tools/{borrow_request.tool.pk}/"
        )
        
        messages.success(request, f'Approved! {borrow_request.tool.name} is now marked as unavailable.')
        
    elif action == 'decline':
        borrow_request.status = 'REJECTED'
        borrow_request.save()
        
        # Create notification for borrower
        Notification.objects.create(
            user=borrow_request.borrower,
            notification_type='TOOL_APPROVED',
            message=f"{request.user.username} declined your request to borrow {borrow_request.tool.name}",
            link=f"/tools/{borrow_request.tool.pk}/"
        )
        
        messages.info(request, 'Request declined.')
    
    return redirect('notifications')

# ============== MAP VIEW ==============
from django.http import JsonResponse

def map_view(request):
    """Display map with nearby users, services, tools, and events"""
    return render(request, 'map/view.html')

def map_data(request):
    """API endpoint to return map markers data"""
    # Get all profiles with coordinates
    profiles = Profile.objects.filter(
        latitude__isnull=False, 
        longitude__isnull=False,
        is_available=True
    ).select_related('user')
    
    # Get active service listings with user coordinates
    services = ServiceListing.objects.filter(
        is_active=True,
        user__profile__latitude__isnull=False,
        user__profile__longitude__isnull=False
    ).select_related('user__profile')
    
    # Get available tools with owner coordinates
    tools = Tool.objects.filter(
        is_available=True,
        owner__profile__latitude__isnull=False,
        owner__profile__longitude__isnull=False
    ).select_related('owner__profile')
    
    # Get upcoming events with coordinates (if event has location coords)
    events = Event.objects.filter(
        is_active=True,
        event_date__gte=timezone.now()
    )[:20]
    
    data = {
        'users': [
            {
                'id': p.user.id,
                'username': p.user.username,
                'lat': float(p.latitude),
                'lng': float(p.longitude),
                'location': p.location,
                'credits': float(p.time_credits),
                'url': f'/profile/{p.user.username}/'
            }
            for p in profiles
        ],
        'services': [
            {
                'id': s.id,
                'title': s.title,
                'type': s.listing_type,
                'lat': float(s.user.profile.latitude),
                'lng': float(s.user.profile.longitude),
                'owner': s.user.username,
                'url': f'/listings/{s.id}/'
            }
            for s in services
        ],
        'tools': [
            {
                'id': t.id,
                'name': t.name,
                'lat': float(t.owner.profile.latitude),
                'lng': float(t.owner.profile.longitude),
                'owner': t.owner.username,
                'url': f'/tools/{t.id}/'
            }
            for t in tools
        ],
    }
    
    return JsonResponse(data)

@login_required
def check_updates(request):
    """API endpoint to check for new messages and notifications"""
    # Get unread messages count
    unread_messages = Message.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    # Get the latest unread message
    latest_message = Message.objects.filter(
        recipient=request.user,
        is_read=False
    ).select_related('sender').order_by('-created_at').first()
    
    # Get unread notifications count
    unread_notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    # Get the latest unread notification
    latest_notification = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at').first()
    
    data = {
        'unread_messages': unread_messages,
        'unread_notifications': unread_notifications,
        'new_message': None,
        'new_notification': None,
    }
    
    # Check if there's a new message (created in last 30 seconds)
    if latest_message:
        time_diff = timezone.now() - latest_message.created_at
        if time_diff.total_seconds() < 30:
            data['new_message'] = {
                'sender': latest_message.sender.username,
                'body': latest_message.body[:50],
            }
    
    # Check if there's a new notification (created in last 30 seconds)
    if latest_notification:
        time_diff = timezone.now() - latest_notification.created_at
        if time_diff.total_seconds() < 30:
            data['new_notification'] = {
                'message': latest_notification.message[:50],
            }
    
    return JsonResponse(data)

