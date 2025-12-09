from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.utils import timezone

# 1. Extended User Profile to track Time Credits
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    time_credits = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, help_text="Neighborhood or City")
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_available = models.BooleanField(default=True, help_text="Available to help others")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.time_credits} hrs)"
    
    def get_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.user.received_reviews.all()
        if reviews.exists():
            return sum(r.rating for r in reviews) / reviews.count()
        return 0

# 2. Skill Tags (for standardized searching)
class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

# 3. Service Listings (What people Offer/Need)
class ServiceListing(models.Model):
    TYPE_CHOICES = [
        ('OFFER', 'Offering Help'),
        ('REQUEST', 'Requesting Help'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    listing_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    skills = models.ManyToManyField(Skill, related_name='listings')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.get_listing_type_display()}] {self.title}"

# 4. Tool Library
class Tool(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tools')
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='tools/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

# 5. The Time Bank Ledger (Transaction History)
class Transaction(models.Model):
    sender = models.ForeignKey(User, related_name='sent_transactions', on_delete=models.PROTECT)
    receiver = models.ForeignKey(User, related_name='received_transactions', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=6, decimal_places=2, help_text="Hours exchanged")
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    related_listing = models.ForeignKey('ServiceListing', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.amount} hrs"

# 6. Tool Borrowing Tracking
class ToolBorrow(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('BORROWED', 'Currently Borrowed'),
        ('RETURNED', 'Returned'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='borrows')
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowed_tools')
    requested_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.borrower.username} borrowing {self.tool.name} ({self.status})"

# 7. Community Events
class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('WORKSHOP', 'Workshop'),
        ('GATHERING', 'Community Gathering'),
        ('MUTUAL_AID', 'Mutual Aid'),
        ('SKILL_SHARE', 'Skill Share'),
        ('OTHER', 'Other'),
    ]
    
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=15, choices=EVENT_TYPE_CHOICES)
    location = models.CharField(max_length=255)
    event_date = models.DateTimeField()
    max_participants = models.IntegerField(null=True, blank=True, help_text="Leave blank for unlimited")
    participants = models.ManyToManyField(User, related_name='joined_events', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} - {self.event_date.strftime('%Y-%m-%d')}"
    
    def spots_remaining(self):
        if self.max_participants:
            return self.max_participants - self.participants.count()
        return None

# 8. Reviews and Reputation System
class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text="1-5 stars")
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['reviewer', 'reviewed_user', 'transaction']
    
    def __str__(self):
        return f"{self.reviewer.username} rated {self.reviewed_user.username} - {self.rating}★"

# 9. Message System for Communication
class Conversation(models.Model):
    """Represents a conversation thread between two users"""
    participant1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_participant1')
    participant2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_participant2')
    listing = models.ForeignKey(ServiceListing, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ['participant1', 'participant2', 'listing']
    
    def __str__(self):
        return f"{self.participant1.username} ↔ {self.participant2.username}"
    
    def get_other_user(self, current_user):
        """Get the other participant in the conversation"""
        return self.participant2 if current_user == self.participant1 else self.participant1
    
    def get_last_message(self):
        """Get the most recent message in this conversation"""
        return self.messages.first()
    
    def has_unread_for(self, user):
        """Check if there are unread messages for a user"""
        return self.messages.filter(recipient=user, is_read=False).exists()

class Message(models.Model):
    """Individual message within a conversation"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending Response'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
        ('NONE', 'No Response Required'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    requires_response = models.BooleanField(default=False, help_text="Does this message require accept/decline?")
    response_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='NONE')
    
    # Credit request fields
    is_credit_request = models.BooleanField(default=False, help_text="Is this a credit transfer request?")
    credit_amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Amount of credits requested")
    credit_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='NONE', help_text="Status of credit request")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username} → {self.recipient.username}: {self.body[:50]}"

# 10. Notification System
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('MESSAGE', 'New Message'),
        ('LISTING_RESPONSE', 'Response to Listing'),
        ('TOOL_REQUEST', 'Tool Borrow Request'),
        ('TOOL_APPROVED', 'Tool Request Approved'),
        ('EVENT_JOINED', 'User Joined Event'),
        ('REVIEW_RECEIVED', 'New Review'),
        ('CREDIT_RECEIVED', 'Credits Received'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True, help_text="URL to related content")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.get_notification_type_display()}"
