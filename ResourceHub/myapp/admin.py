from django.contrib import admin
from .models import (Profile, Skill, ServiceListing, Tool, Transaction, Event, 
                     Review, ToolBorrow, Conversation, Message, Notification)

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'time_credits', 'location', 'is_available', 'created_at']
    list_filter = ['is_available', 'created_at']
    search_fields = ['user__username', 'location']
    readonly_fields = ['created_at']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(ServiceListing)
class ServiceListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'listing_type', 'is_active', 'created_at']
    list_filter = ['listing_type', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    filter_horizontal = ['skills']
    readonly_fields = ['created_at']
    
    actions = ['activate_listings', 'deactivate_listings']
    
    def activate_listings(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} listings activated.")
    activate_listings.short_description = "Activate selected listings"
    
    def deactivate_listings(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} listings deactivated.")
    deactivate_listings.short_description = "Deactivate selected listings"

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'is_available']
    list_filter = ['is_available']
    search_fields = ['name', 'description', 'owner__username']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'amount', 'timestamp', 'description']
    list_filter = ['timestamp']
    search_fields = ['sender__username', 'receiver__username', 'description']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

@admin.register(ToolBorrow)
class ToolBorrowAdmin(admin.ModelAdmin):
    list_display = ['tool', 'borrower', 'status', 'start_date', 'end_date']
    list_filter = ['status', 'start_date']
    search_fields = ['tool__name', 'borrower__username']
    readonly_fields = ['requested_at']
    
    actions = ['approve_requests', 'mark_returned']
    
    def approve_requests(self, request, queryset):
        queryset.update(status='APPROVED')
        self.message_user(request, f"{queryset.count()} borrow requests approved.")
    approve_requests.short_description = "Approve selected requests"
    
    def mark_returned(self, request, queryset):
        queryset.update(status='RETURNED')
        self.message_user(request, f"{queryset.count()} borrows marked as returned.")
    mark_returned.short_description = "Mark as returned"

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'event_type', 'event_date', 'is_active']
    list_filter = ['event_type', 'is_active', 'event_date']
    search_fields = ['title', 'description', 'organizer__username']
    filter_horizontal = ['participants']
    readonly_fields = ['created_at']
    date_hierarchy = 'event_date'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'reviewed_user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['reviewer__username', 'reviewed_user__username', 'comment']
    readonly_fields = ['created_at']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['participant1', 'participant2', 'listing', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['participant1__username', 'participant2__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'conversation', 'is_read', 'is_credit_request', 'credit_amount', 'credit_status', 'created_at']
    list_filter = ['is_read', 'requires_response', 'response_status', 'is_credit_request', 'credit_status', 'created_at']
    search_fields = ['sender__username', 'recipient__username', 'body']
    readonly_fields = ['created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'message', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'message']
    readonly_fields = ['created_at']
