from django.db import models
from django.contrib.auth.models import User

# Category choices for skills
CATEGORY_CHOICES = [
    ('tutoring', 'Tutoring'),
    ('music', 'Music Lessons'),
    ('sports', 'Sports'),
    ('tech', 'Tech Help'),
    ('art', 'Art & Design'),
    ('writing', 'Writing'),
    ('language', 'Language'),
    ('other', 'Other'),
]

# Price type choices
PRICE_CHOICES = [
    ('free', 'Free'),
    ('paid', 'Paid'),
]

# Availability choices
AVAILABILITY_CHOICES = [
    ('available', 'Available Now'),
    ('weekends', 'Weekends Only'),
    ('limited', 'Limited Availability'),
    ('unavailable', 'Currently Unavailable'),
]

# Contact preference choices
CONTACT_CHOICES = [
    ('email', 'Email'),
    ('phone', 'Phone'),
    ('inperson', 'In Person'),
    ('online', 'Online'),
]


class Skill(models.Model):
    """
    Represents a skill or service that a student offers.
    Connected to Django's User model so each skill has an owner.
    """
    # Basic information
    title = models.CharField(max_length=100, help_text="What skill are you offering?")
    description = models.TextField(help_text="Describe your skill in detail")
    
    # Categorization
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other'
    )
    
    # Pricing
    price_type = models.CharField(
        max_length=10,
        choices=PRICE_CHOICES,
        default='free'
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,  # Optional if offering for free
        help_text="Leave blank if offering for free"
    )
    
    # Availability
    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='available'
    )
    
    # How to contact
    contact_preference = models.CharField(
        max_length=20,
        choices=CONTACT_CHOICES,
        default='email'
    )
    
    # Connection to user
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='skills'  # Access skills via user.skills.all()
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']  # Newest skills first
        verbose_name_plural = "Skills"
    
    def __str__(self):
        """Show skill title when printed"""
        return self.title
    
    def get_average_rating(self):
        """
        Calculate and return the average rating for this skill.
        Returns 0 if no reviews exist.
        """
        from django.db.models import Avg
        average = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(average, 1) if average else 0
    
    def get_review_count(self):
        """Return the total number of reviews for this skill."""
        return self.reviews.count()


# Rating choices for reviews
RATING_CHOICES = [
    (1, '⭐ Poor'),
    (2, '⭐⭐ Fair'),
    (3, '⭐⭐⭐ Good'),
    (4, '⭐⭐⭐⭐ Very Good'),
    (5, '⭐⭐⭐⭐⭐ Excellent'),
]


class Review(models.Model):
    """
    Represents a review/rating left by a user for a skill.
    Each user can only leave one review per skill (enforced by unique_together).
    """
    # The skill being reviewed
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='reviews'  # Access reviews via skill.reviews.all()
    )
    
    # The user who left the review
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='skill_reviews'  # Access reviews via user.skill_reviews.all()
    )
    
    # Rating (1-5 stars)
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        default=5,
        help_text="Rate this skill from 1 to 5 stars"
    )
    
    # Review text
    review_text = models.TextField(
        max_length=1000,
        help_text="Share your experience with this skill"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']  # Newest reviews first
        unique_together = ['skill', 'reviewer']  # Only one review per user per skill
    
    def __str__(self):
        """Display review as: 'Reviewer - Skill Title (X stars)'"""
        return f"{self.reviewer.username} reviewed {self.skill.title} ({self.rating}★)"


class Message(models.Model):
    """
    Represents a private message between two users.
    Users can message each other to discuss skills.
    """
    # The message sender
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'  # Access sent messages via user.sent_messages.all()
    )
    
    # The message recipient
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'  # Access received messages via user.received_messages.all()
    )
    
    # The skill being discussed (optional - context for the message)
    skill = models.ForeignKey(
        Skill,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages',
        help_text="The skill this message is about (optional)"
    )
    
    # Message content
    subject = models.CharField(
        max_length=200,
        help_text="Subject line for this message"
    )
    
    body = models.TextField(
        help_text="Your message content"
    )
    
    # Track if recipient has read the message
    is_read = models.BooleanField(
        default=False,
        help_text="Has the recipient read this message?"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']  # Newest messages first
    
    def __str__(self):
        """Display message as: 'From: sender To: recipient - subject'"""
        return f"From {self.sender.username} to {self.recipient.username}: {self.subject}"
    
    def mark_as_read(self):
        """Mark this message as read by the recipient."""
        self.is_read = True
        self.save()
    
    def get_conversation_with(self, other_user):
        """
        Get all messages in conversation between this message's sender/recipient and another user.
        Used to display entire conversation thread.
        """
        return Message.objects.filter(
            (models.Q(sender=self.sender) & models.Q(recipient=other_user)) |
            (models.Q(sender=other_user) & models.Q(recipient=self.sender))
        ).order_by('created_at')
