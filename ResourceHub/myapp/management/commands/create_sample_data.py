from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from myapp.models import Skill, ServiceListing, Tool, Event, Profile
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Create sample data for testing the Community Resource Hub'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...\n')

        # Create skills
        skills_data = [
            'Tutoring', 'Cooking', 'Home Repair', 'Gardening', 
            'Tech Support', 'Language Teaching', 'Music Lessons',
            'Pet Care', 'Carpentry', 'Plumbing', 'Electrical Work',
            'Painting', 'Cleaning', 'Childcare', 'Elder Care',
            'Transportation', 'Moving Help', 'Administrative Help',
            'Photography', 'Web Design', 'Writing/Editing', 'Yoga',
            'Fitness Training', 'Sewing', 'Auto Repair'
        ]
        
        skills = []
        for skill_name in skills_data:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            skills.append(skill)
            if created:
                self.stdout.write(f'  Created skill: {skill_name}')
        
        # Create sample users
        users_data = [
            {'username': 'alice', 'first_name': 'Alice', 'last_name': 'Johnson', 'email': 'alice@example.com', 'location': 'Downtown'},
            {'username': 'bob', 'first_name': 'Bob', 'last_name': 'Smith', 'email': 'bob@example.com', 'location': 'Riverside'},
            {'username': 'carol', 'first_name': 'Carol', 'last_name': 'Williams', 'email': 'carol@example.com', 'location': 'Hillside'},
            {'username': 'david', 'first_name': 'David', 'last_name': 'Brown', 'email': 'david@example.com', 'location': 'Oak Park'},
            {'username': 'eve', 'first_name': 'Eve', 'last_name': 'Davis', 'email': 'eve@example.com', 'location': 'Maple Grove'},
        ]
        
        created_users = []
        for user_data in users_data:
            location = user_data.pop('location')
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={**user_data, 'email': user_data['email']}
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'  Created user: {user.username}')
                
                # Update profile
                profile = user.profile
                profile.location = location
                profile.time_credits = random.randint(5, 50)
                profile.bio = f"Hi! I'm {user.first_name}. Happy to help the community!"
                profile.is_available = True
                profile.save()
                
            created_users.append(user)
        
        # Create sample service listings
        offers_data = [
            {'title': 'Guitar Lessons for Beginners', 'description': 'I can teach basic guitar chords and songs. 10 years experience!', 'type': 'OFFER', 'skills': ['Music Lessons']},
            {'title': 'Help with Math Tutoring', 'description': 'Available to tutor high school math. Former teacher.', 'type': 'OFFER', 'skills': ['Tutoring']},
            {'title': 'Lawn Mowing Service', 'description': 'Can mow your lawn and trim edges. Have all equipment.', 'type': 'OFFER', 'skills': ['Gardening']},
            {'title': 'Computer Troubleshooting', 'description': 'Can help fix computer issues, install software, etc.', 'type': 'OFFER', 'skills': ['Tech Support']},
            {'title': 'Home Cooked Meals', 'description': 'Love cooking! Can prepare healthy meals for busy families.', 'type': 'OFFER', 'skills': ['Cooking']},
        ]
        
        requests_data = [
            {'title': 'Need Help Moving Furniture', 'description': 'Moving to new apartment next week. Need help with heavy items.', 'type': 'REQUEST', 'skills': ['Moving Help']},
            {'title': 'Looking for Dog Walker', 'description': 'Need someone to walk my dog twice a week while I'm at work.', 'type': 'REQUEST', 'skills': ['Pet Care']},
            {'title': 'Website Design Help', 'description': 'Starting a small business and need help creating a simple website.', 'type': 'REQUEST', 'skills': ['Web Design']},
            {'title': 'Spanish Language Practice', 'description': 'Want to practice conversational Spanish with a native speaker.', 'type': 'REQUEST', 'skills': ['Language Teaching']},
        ]
        
        all_listings = offers_data + requests_data
        random.shuffle(all_listings)
        
        for i, listing_data in enumerate(all_listings):
            user = created_users[i % len(created_users)]
            skill_names = listing_data.pop('skills')
            listing_type = listing_data.pop('type')
            
            listing, created = ServiceListing.objects.get_or_create(
                user=user,
                title=listing_data['title'],
                defaults={
                    'description': listing_data['description'],
                    'listing_type': listing_type
                }
            )
            
            if created:
                for skill_name in skill_names:
                    skill = Skill.objects.get(name=skill_name)
                    listing.skills.add(skill)
                self.stdout.write(f'  Created listing: {listing.title}')
        
        # Create sample tools
        tools_data = [
            {'name': 'Electric Drill', 'description': 'Cordless drill with various bits. Great for home projects.'},
            {'name': 'Lawn Mower', 'description': 'Gas-powered push mower. Well maintained.'},
            {'name': 'Ladder (10ft)', 'description': 'Aluminum extension ladder. Perfect for outdoor work.'},
            {'name': 'Camping Tent (4-person)', 'description': 'Spacious tent for family camping trips.'},
            {'name': 'Pressure Washer', 'description': 'Electric pressure washer for cleaning driveways, decks, etc.'},
        ]
        
        for i, tool_data in enumerate(tools_data):
            user = created_users[i % len(created_users)]
            tool, created = Tool.objects.get_or_create(
                owner=user,
                name=tool_data['name'],
                defaults={'description': tool_data['description']}
            )
            if created:
                self.stdout.write(f'  Created tool: {tool.name}')
        
        # Create sample events
        events_data = [
            {
                'title': 'Community Garden Workday',
                'description': 'Join us for a morning of planting and weeding at the community garden!',
                'event_type': 'MUTUAL_AID',
                'location': 'Community Garden, Main St',
                'days_ahead': 7,
            },
            {
                'title': 'Home Repair Skills Workshop',
                'description': 'Learn basic home repair skills from experienced neighbors.',
                'event_type': 'WORKSHOP',
                'location': 'Community Center',
                'days_ahead': 14,
            },
            {
                'title': 'Neighborhood Potluck',
                'description': 'Bring a dish to share and meet your neighbors!',
                'event_type': 'GATHERING',
                'location': 'Central Park Pavilion',
                'days_ahead': 5,
            },
        ]
        
        for event_data in events_data:
            days_ahead = event_data.pop('days_ahead')
            event_date = timezone.now() + timedelta(days=days_ahead)
            organizer = random.choice(created_users)
            
            event, created = Event.objects.get_or_create(
                organizer=organizer,
                title=event_data['title'],
                defaults={
                    **event_data,
                    'event_date': event_date,
                    'max_participants': random.choice([None, 10, 20, 30])
                }
            )
            
            if created:
                # Add some participants
                num_participants = random.randint(1, min(3, len(created_users)))
                participants = random.sample(created_users, num_participants)
                for participant in participants:
                    if participant != organizer:
                        event.participants.add(participant)
                
                self.stdout.write(f'  Created event: {event.title}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sample data created successfully!'))
        self.stdout.write(f'   Users: {User.objects.count()}')
        self.stdout.write(f'   Skills: {Skill.objects.count()}')
        self.stdout.write(f'   Listings: {ServiceListing.objects.count()}')
        self.stdout.write(f'   Tools: {Tool.objects.count()}')
        self.stdout.write(f'   Events: {Event.objects.count()}')
        self.stdout.write('\n   Test user credentials:')
        self.stdout.write('   Username: alice, bob, carol, david, or eve')
        self.stdout.write('   Password: password123\n')
