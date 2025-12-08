# Community Resource Hub & Time Banking Platform

A Django-based web platform where community members can share skills, tools, and resources using a time-based currency system. Instead of money, people earn "time credits" by helping others, which they can use to receive help themselves.

## 🌟 Features

### Core Functionality
- **Time Credit System**: Track hours given and received to encourage reciprocity
- **User Profiles**: Extended profiles with bio, location, phone, profile pictures, and ratings
- **Skill Exchange**: Users post offers and requests for services (tutoring, repairs, cooking, tech help, etc.)
- **Tool Library**: Share equipment like lawn mowers, power tools, camping gear
- **Community Events**: Announce gatherings, workshops, and mutual aid efforts
- **Smart Matching**: Algorithm suggests matches between service offers and requests
- **Reputation System**: Reviews and ratings (1-5 stars) build trust within the community
- **Tool Borrowing**: Request to borrow items with approval workflow
- **Mobile-Responsive Design**: Bootstrap 5 for accessibility on all devices

### Key Models
1. **Profile** - Extended user info with time credits, location, availability
2. **Skill** - Standardized skill tags for searching
3. **ServiceListing** - Offers or requests for help
4. **Tool** - Shared equipment with availability tracking
5. **ToolBorrow** - Borrowing requests and approval system
6. **Event** - Community gatherings and workshops
7. **Transaction** - Time credit transfers between users
8. **Review** - User ratings and feedback

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- Django 6.0
- Pillow (for image handling)

### Installation

1. **Navigate to project directory**:
```bash
cd /home/kiapa/Desktop/ResourceHub/ResourceHub
```

2. **Install dependencies** (if not already installed):
```bash
pip install django pillow
```

3. **Create migrations**:
```bash
python manage.py makemigrations
```

4. **Apply migrations**:
```bash
python manage.py migrate
```

5. **Create a superuser** (for admin access):
```bash
python manage.py createsuperuser
```

6. **Create media directory**:
```bash
mkdir -p media/profiles media/tools
```

7. **Run the development server**:
```bash
python manage.py runserver
```

8. **Access the site**:
- Website: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
ResourceHub/
├── myapp/
│   ├── models.py          # All database models
│   ├── views.py           # All view functions
│   ├── forms.py           # All forms
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin configurations
│   ├── signals.py         # Auto-create profiles & update credits
│   ├── templates/
│   │   ├── base.html      # Base template with navigation
│   │   ├── index.html     # Homepage
│   │   ├── dashboard.html # User dashboard
│   │   ├── transfer.html  # Credit transfer page
│   │   ├── registration/  # Login, register pages
│   │   ├── listings/      # Service listing templates
│   │   ├── tools/         # Tool library templates
│   │   ├── events/        # Event templates
│   │   ├── profile/       # User profile templates
│   │   ├── reviews/       # Review templates
│   │   └── matching/      # Match results templates
│   └── migrations/
├── ResourceHub/
│   ├── settings.py        # Django settings (media files configured)
│   ├── urls.py            # Main URL config
│   └── wsgi.py
├── media/                 # User-uploaded files (profiles, tools)
├── static/                # Static files (CSS, JS, images)
└── db.sqlite3             # SQLite database
```

## 🔑 Key URLs

### Public Pages
- `/` - Homepage
- `/register/` - User registration
- `/login/` - User login
- `/listings/` - Browse service listings
- `/tools/` - Browse tool library
- `/events/` - Browse community events

### Authenticated Pages
- `/dashboard/` - User dashboard
- `/profile/<username>/` - View user profile
- `/profile/edit/` - Edit your profile
- `/transfer/` - Transfer time credits
- `/matches/` - Find matching offers/requests
- `/listings/create/` - Post new service listing
- `/tools/create/` - Add tool to library
- `/events/create/` - Create community event
- `/tools/borrows/` - Manage tool borrow requests
- `/reviews/create/<username>/` - Write a review

## 👥 Getting Started as a User

1. **Register** - Create an account (you start with 0 time credits)
2. **Complete Profile** - Add bio, location, phone, profile picture
3. **Browse Services** - See what others are offering or requesting
4. **Post Listings** - Share what you can offer or what you need
5. **Share Tools** - List equipment you're willing to lend
6. **Find Matches** - Use the matching algorithm to find relevant connections
7. **Exchange Services** - Help someone and receive time credits
8. **Transfer Credits** - Send credits after receiving help
9. **Leave Reviews** - Build trust through ratings and feedback
10. **Join Events** - Participate in community gatherings

## 🛠️ Admin Panel Features

Access at `/admin/` with superuser credentials:

- **User Management** - View all users and their profiles
- **Moderation** - Activate/deactivate listings, approve/reject tool borrows
- **Transaction History** - Monitor all time credit transfers
- **Skill Management** - Add/edit skill tags
- **Event Management** - Oversee community events
- **Review Moderation** - Monitor user ratings and feedback

### Bulk Actions Available:
- Activate/deactivate service listings
- Approve/reject tool borrow requests
- Mark tools as returned

## 🎯 Usage Examples

### Example 1: Skill Exchange
1. Alice posts an OFFER: "Can teach guitar lessons"
2. Bob posts a REQUEST: "Need help learning guitar"
3. The matching algorithm suggests they connect
4. Alice helps Bob for 2 hours
5. Bob sends Alice 2 time credits
6. Both leave reviews for each other

### Example 2: Tool Borrowing
1. Carol lists her "Lawn Mower" as available
2. David requests to borrow it for Saturday
3. Carol approves the request
4. David borrows and returns the mower
5. Optional: David sends time credits as thanks

### Example 3: Community Event
1. Eve creates a "Community Garden Workshop"
2. Members join the event
3. Everyone participates and exchanges skills
4. Credits are exchanged based on contributions

## 🔒 Security Features

- Django's built-in authentication system
- CSRF protection on all forms
- Login required decorators on sensitive views
- User ownership validation before edits/deletes
- Password validation (minimum length, complexity)
- Profile privacy controls (availability status)

## 📱 Mobile Responsiveness

- Bootstrap 5 grid system
- Responsive navigation with hamburger menu
- Touch-friendly buttons and cards
- Optimized images for mobile
- DateTime pickers work on mobile browsers

## 🎨 Design Features

- Clean, modern interface with Bootstrap 5
- Bootstrap Icons for visual elements
- Card-based layouts for content
- Color-coded badges (offers=green, requests=warning)
- Hover effects on cards
- Hero section with gradient
- Responsive footer

## 🔄 Automatic Features

### Signals
- **Auto-create Profile**: When a user registers, a Profile is automatically created
- **Update Credits**: When a Transaction is saved, both users' credit balances update automatically

### Validation
- Prevent negative credit transfers
- Prevent sending credits to yourself
- Check available time credits before transfer
- Validate tool availability before borrowing
- Check event capacity before joining

## 📊 Database Relationships

```
User (Django Auth)
├── 1:1 → Profile (time credits, bio, location, rating)
├── 1:N → ServiceListings (offers/requests posted)
├── 1:N → Tools (equipment owned)
├── 1:N → Events (events organized)
├── M:N → Events (events joined as participant)
├── 1:N → Transactions (sent)
├── 1:N → Transactions (received)
├── 1:N → Reviews (given)
└── 1:N → Reviews (received)

ServiceListing
└── M:N → Skills

Tool
└── 1:N → ToolBorrow

Transaction
└── 1:1 → Review (optional)
```

## 🚀 Future Enhancements

- Email notifications for matches and events
- SMS reminders for upcoming events
- GeoDjango integration for location-based matching
- Calendar integration for tool borrowing
- Mobile app using Django REST Framework
- Real-time chat between users
- Dispute resolution system
- Community moderator roles
- Multi-language support
- Analytics dashboard for community insights
- Skill endorsements
- Time banking reports (monthly/yearly)

## 🤝 Community Impact

This platform helps:
- **Reduce isolation** - Especially for elderly or disabled community members
- **Increase accessibility** - Services available to those with limited income
- **Reduce waste** - Through tool and equipment sharing
- **Build social capital** - Strengthen neighborhood connections
- **Promote reciprocity** - Fair exchange through time credits
- **Foster resilience** - Communities support each other

## 📝 Notes

- Default time zone: UTC (change in settings.py if needed)
- Media files stored in `/media/` directory
- Static files in `/static/` directory
- SQLite database for development (use PostgreSQL for production)
- Debug mode is ON (turn off for production)
- Secret key should be changed for production

## 🐛 Troubleshooting

### Profile doesn't exist error
- Make sure migrations are run: `python manage.py migrate`
- Signals should auto-create profiles for new users
- For existing users without profiles, create them in admin or shell

### Images not displaying
- Ensure media directories exist: `mkdir -p media/profiles media/tools`
- Check MEDIA_ROOT and MEDIA_URL in settings.py
- Verify DEBUG=True in development

### Time credits not updating
- Check signals.py is being loaded (apps.py ready() method)
- Verify transaction saved successfully
- Check for atomic transaction errors

## 📄 License

This is an open-source community project. Feel free to use and modify for your community's needs.

## 🙋 Support

For issues or questions:
1. Check the Django documentation
2. Review the code comments in models.py and views.py
3. Access admin panel for data management
4. Use Django shell for debugging: `python manage.py shell`

---

**Built with Django** for creating stronger, more resilient communities through sharing and mutual aid.
