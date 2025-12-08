from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Transaction, ServiceListing, Tool, Event, Review, Profile, ToolBorrow, Skill

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'phone', 'profile_picture', 'is_available']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TransferForm(forms.ModelForm):
    # We override the receiver field to filter users properly if needed
    receiver = forms.ModelChoiceField(
        queryset=User.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    amount = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Hours (e.g., 1.5)'})
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What was this for?'})
    )

    class Meta:
        model = Transaction
        fields = ['receiver', 'amount', 'description']

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Time credits must be positive.")
        return amount

class ServiceListingForm(forms.ModelForm):
    PREDEFINED_SKILLS = [
        'Tutoring', 'Cooking', 'Gardening', 'Pet Care', 'Child Care',
        'Elder Care', 'Home Repair', 'Plumbing', 'Electrical Work', 'Carpentry',
        'Painting', 'Cleaning', 'Moving Help', 'Transportation', 'Computer Help',
        'Web Design', 'Graphic Design', 'Writing', 'Translation', 'Photography',
        'Music Lessons', 'Art Lessons', 'Fitness Training', 'Yoga', 'Massage',
        'Hair Styling', 'Sewing', 'Knitting', 'Baking', 'Event Planning',
        'Legal Advice', 'Tax Help', 'Career Counseling', 'Life Coaching', 'Mentoring'
    ]
    
    skills = forms.MultipleChoiceField(
        required=False,
        choices=[(skill, skill) for skill in PREDEFINED_SKILLS],
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': '8',
            'style': 'height: 200px;'
        }),
        help_text='Hold Ctrl (or Cmd on Mac) to select multiple skills'
    )
    
    other_skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Any other skills not listed above (comma-separated)'
        }),
        help_text='Add custom skills separated by commas'
    )
    
    class Meta:
        model = ServiceListing
        fields = ['title', 'description', 'listing_type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'listing_type': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing existing listing, populate with existing skills
        if self.instance and self.instance.pk:
            existing_skill_names = list(self.instance.skills.values_list('name', flat=True))
            
            # Separate predefined and custom skills
            predefined = [s for s in existing_skill_names if s in self.PREDEFINED_SKILLS]
            custom = [s for s in existing_skill_names if s not in self.PREDEFINED_SKILLS]
            
            self.fields['skills'].initial = predefined
            self.fields['other_skills'].initial = ', '.join(custom)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Must save the instance first before working with many-to-many relationships
        if commit:
            instance.save()
            
            # Clear existing skills
            instance.skills.clear()
            
            # Add selected predefined skills
            selected_skills = self.cleaned_data.get('skills', [])
            for skill_name in selected_skills:
                skill, created = Skill.objects.get_or_create(name=skill_name)
                instance.skills.add(skill)
            
            # Add custom skills from other_skills field
            other_skills_text = self.cleaned_data.get('other_skills', '')
            if other_skills_text:
                skill_names = [name.strip() for name in other_skills_text.split(',') if name.strip()]
                for skill_name in skill_names:
                    skill, created = Skill.objects.get_or_create(name=skill_name)
                    instance.skills.add(skill)
        
        return instance

class ToolForm(forms.ModelForm):
    class Meta:
        model = Tool
        fields = ['name', 'description', 'image', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ToolBorrowForm(forms.ModelForm):
    class Meta:
        model = ToolBorrow
        fields = ['start_date', 'end_date', 'notes']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'event_type', 'location', 'event_date', 'max_participants']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'event_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}, choices=[(i, '⭐' * i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
