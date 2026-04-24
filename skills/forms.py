from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Skill, Review, Message


class SkillForm(forms.ModelForm):
    """
    Form for creating and editing skill posts.
    Uses ModelForm to automatically generate fields from the Skill model.
    """
    class Meta:
        model = Skill
        fields = [
            'title', 'description', 'category', 
            'price_type', 'price', 'availability', 
            'contact_preference'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Spanish Tutoring'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your skill, experience, and what students can learn'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'price_type': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank if free',
                'step': '0.01'  # Allows decimal prices like $15.50
            }),
            'availability': forms.Select(attrs={
                'class': 'form-control'
            }),
            'contact_preference': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class CustomUserCreationForm(UserCreationForm):
    """
    Extended registration form with email field.
    Django's default UserCreationForm doesn't include email.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@university.edu'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_email(self):
        """Make sure email isn't already used"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered.')
        return email
    
    def save(self, commit=True):
        """Save the user with the email"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ReviewForm(forms.ModelForm):
    """
    Form for creating and editing reviews of skills.
    Uses ModelForm to automatically generate fields from the Review model.
    """
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
            'review_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your honest experience with this skill. What did you learn? Would you recommend it?',
                'maxlength': '1000'
            }),
        }
    
    def clean_rating(self):
        """Validate that rating is between 1 and 5"""
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise forms.ValidationError('Rating must be between 1 and 5 stars.')
        return rating
    
    def clean_review_text(self):
        """Validate that review text is not empty"""
        review_text = self.cleaned_data.get('review_text')
        if not review_text or not review_text.strip():
            raise forms.ValidationError('Please write a review.')
        if len(review_text) < 10:
            raise forms.ValidationError('Review must be at least 10 characters long.')
        return review_text


class MessageForm(forms.ModelForm):
    """
    Form for sending private messages between users.
    Uses ModelForm to automatically generate fields from the Message model.
    """
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'What is this message about?',
                'maxlength': '200'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Type your message here... Ask questions, discuss the skill, or arrange a meeting.',
                'maxlength': '5000'
            }),
        }
    
    def clean_subject(self):
        """Validate that subject is not empty"""
        subject = self.cleaned_data.get('subject')
        if not subject or not subject.strip():
            raise forms.ValidationError('Please enter a subject line.')
        if len(subject) < 3:
            raise forms.ValidationError('Subject must be at least 3 characters long.')
        return subject
    
    def clean_body(self):
        """Validate that message body is not empty"""
        body = self.cleaned_data.get('body')
        if not body or not body.strip():
            raise forms.ValidationError('Please write a message.')
        if len(body) < 5:
            raise forms.ValidationError('Message must be at least 5 characters long.')
        return body
