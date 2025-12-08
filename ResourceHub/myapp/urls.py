from django.urls import path
from myapp import views

urlpatterns = [
    # Home & Dashboard
    path('', views.index, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Profile
    path('profile/<str:username>/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Transactions
    path('transfer/', views.transfer_credits, name='transfer_credits'),
    
    # Service Listings
    path('listings/', views.listing_browse, name='listing_browse'),
    path('listings/create/', views.listing_create, name='listing_create'),
    path('listings/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('listings/<int:pk>/edit/', views.listing_edit, name='listing_edit'),
    path('listings/<int:pk>/delete/', views.listing_delete, name='listing_delete'),
    
    # Tools
    path('tools/', views.tool_browse, name='tool_browse'),
    path('tools/create/', views.tool_create, name='tool_create'),
    path('tools/<int:pk>/', views.tool_detail, name='tool_detail'),
    path('tools/<int:pk>/borrow/', views.tool_request_borrow, name='tool_request_borrow'),
    path('tools/borrows/', views.tool_manage_borrows, name='tool_manage_borrows'),
    path('tools/borrows/<int:pk>/approve/', views.tool_approve_borrow, name='tool_approve_borrow'),
    
    # Events
    path('events/', views.event_browse, name='event_browse'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/<int:pk>/join/', views.event_join, name='event_join'),
    path('events/<int:pk>/leave/', views.event_leave, name='event_leave'),
    
    # Reviews
    path('reviews/create/<str:username>/', views.create_review, name='create_review'),
    
    # Matching
    path('matches/', views.find_matches, name='find_matches'),
]
