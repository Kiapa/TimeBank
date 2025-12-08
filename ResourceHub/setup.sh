#!/bin/bash

# Community Resource Hub - Quick Setup Script

echo "🚀 Setting up Community Resource Hub..."

# Create media directories
echo "📁 Creating media directories..."
mkdir -p media/profiles media/tools

# Create migrations
echo "🔄 Creating migrations..."
python manage.py makemigrations

# Apply migrations
echo "✅ Applying migrations..."
python manage.py migrate

# Create some initial skills
echo "🎯 Creating initial skill tags..."
python manage.py shell << EOF
from myapp.models import Skill

skills = [
    'Tutoring', 'Cooking', 'Home Repair', 'Gardening', 
    'Tech Support', 'Language Teaching', 'Music Lessons',
    'Pet Care', 'Carpentry', 'Plumbing', 'Electrical Work',
    'Painting', 'Cleaning', 'Childcare', 'Elder Care',
    'Transportation', 'Moving Help', 'Administrative Help',
    'Photography', 'Web Design', 'Writing/Editing'
]

for skill_name in skills:
    Skill.objects.get_or_create(name=skill_name)

print(f"Created {Skill.objects.count()} skill tags")
EOF

echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Create a superuser: python manage.py createsuperuser"
echo "2. Run the server: python manage.py runserver"
echo "3. Visit: http://127.0.0.1:8000/"
echo "4. Admin panel: http://127.0.0.1:8000/admin/"
echo ""
echo "Happy building! 🏘️"
