# Quick Start Guide - Community Resource Hub

## 🚀 Get Started in 5 Minutes

### Step 1: Run Setup Script
```bash
cd /home/kiapa/Desktop/ResourceHub/ResourceHub
chmod +x setup.sh
./setup.sh
```

This will:
- Create media directories
- Run migrations
- Create initial skill tags

### Step 2: Create Admin User
```bash
python manage.py createsuperuser
```

Enter your desired:
- Username
- Email
- Password

### Step 3: (Optional) Load Sample Data
```bash
python manage.py create_sample_data
```

This creates:
- 5 test users (alice, bob, carol, david, eve)
- Sample service listings (offers & requests)
- Sample tools
- Sample events
- Test password: `password123`

### Step 4: Start the Server
```bash
python manage.py runserver
```

### Step 5: Access the Site
- **Homepage**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 🎯 First Steps on the Site

### As a New User:
1. Click "Sign Up" in the navigation
2. Fill out registration form
3. Upload a profile picture (optional)
4. Complete your profile with location and bio

### Explore Features:
1. **Browse Services** - See what neighbors are offering
2. **Post a Listing** - Share what you can do or need
3. **Add Tools** - List equipment you can lend
4. **Create Events** - Organize community gatherings
5. **Find Matches** - Discover suggested connections

### Try the Matching System:
1. Post an OFFER (e.g., "Can tutor math")
2. Post a REQUEST (e.g., "Need help with algebra")
3. Click "Matches" in navigation
4. See algorithm suggestions!

## 🔑 Test Accounts (if you ran create_sample_data)

| Username | Location | Time Credits |
|----------|----------|--------------|
| alice | Downtown | 5-50 hrs |
| bob | Riverside | 5-50 hrs |
| carol | Hillside | 5-50 hrs |
| david | Oak Park | 5-50 hrs |
| eve | Maple Grove | 5-50 hrs |

**Password for all**: `password123`

## 📋 Things to Try

### Exchange Time Credits:
1. Login as `alice`
2. Go to "Transfer Credits"
3. Send 5 hours to `bob`
4. Check balances update automatically!

### Borrow a Tool:
1. Browse Tools
2. Click "Request to Borrow"
3. Select dates and submit
4. Owner receives notification in dashboard

### Join an Event:
1. Browse Events
2. Click on an event
3. Click "Join Event"
4. See yourself in participants list

### Leave a Review:
1. Visit another user's profile
2. Click "Write Review"
3. Rate 1-5 stars and leave comment
4. See it appear on their profile

## 🛠️ Admin Panel Features

Login to `/admin/` with your superuser account:

### Manage Content:
- **Users** - View all registered users
- **Profiles** - Edit time credits, locations
- **Service Listings** - Moderate offers/requests
- **Tools** - Manage tool library
- **Events** - Oversee community events
- **Transactions** - View all credit transfers
- **Reviews** - Monitor user feedback

### Bulk Actions:
- Activate/deactivate multiple listings
- Approve/reject tool borrow requests
- Mark borrows as returned

### Add Skills:
1. Go to Skills section
2. Click "Add Skill"
3. Enter name (e.g., "Yoga", "Carpentry")
4. Save

## 🎨 Customization Tips

### Change Colors:
Edit `myapp/templates/base.html`:
```html
<!-- Find the navbar class -->
<nav class="navbar navbar-dark bg-primary">
<!-- Change bg-primary to: bg-success, bg-danger, bg-info, etc. -->
```

### Adjust Starting Credits:
Edit `myapp/models.py`:
```python
class Profile(models.Model):
    time_credits = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=10.00  # Change this number
    )
```

### Change Site Name:
Edit `myapp/templates/base.html`:
```html
<a class="navbar-brand" href="{% url 'home' %}">
    <i class="bi bi-clock-history"></i> Your Community Name
</a>
```

## ❓ Troubleshooting

### "Profile does not exist" error:
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from myapp.models import Profile
>>> for user in User.objects.all():
...     Profile.objects.get_or_create(user=user)
```

### Images not showing:
```bash
mkdir -p media/profiles media/tools
# Verify in settings.py:
# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'
```

### Migrations error:
```bash
python manage.py makemigrations myapp
python manage.py migrate
```

### Reset database (WARNING: deletes all data):
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python manage.py create_sample_data
```

## 📚 Next Steps

1. **Invite Community Members** - Share the signup link
2. **Add More Skills** - Via admin panel
3. **Moderate Content** - Review listings and events
4. **Promote Events** - Create gatherings to build community
5. **Monitor Transactions** - Ensure fair exchanges
6. **Gather Feedback** - Use reviews to build trust

## 🎉 Success Metrics

Your platform is working when:
- ✅ Users are posting listings
- ✅ Time credits are being exchanged
- ✅ Tools are being borrowed
- ✅ Events have participants
- ✅ Reviews are being left
- ✅ Matches are being made

## 🆘 Need Help?

1. Check the main README.md for detailed documentation
2. Review code comments in `models.py` and `views.py`
3. Use Django shell for debugging: `python manage.py shell`
4. Check Django docs: https://docs.djangoproject.com/

---

**Happy Community Building! 🏘️**
