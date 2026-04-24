from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Skill, Review, Message
from .forms import SkillForm, CustomUserCreationForm, ReviewForm, MessageForm


# ==================== HOME & SKILL LIST VIEWS ====================

def home(request):
    """
    Home page - shows the 6 most recent skills.
    Anyone can view this page (no login required).
    """
    recent_skills = Skill.objects.all()[:6]
    context = {
        'skills': recent_skills,
        'title': 'Welcome to Campus SkillSwap'
    }
    return render(request, 'home.html', context)


def skill_list(request):
    """
    Display all available skills with search/filter options.
    Anyone can browse skills.
    
    GET parameters:
    - category: filter by skill category
    - search: search in title and description
    """
    skills = Skill.objects.all()
    
    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        skills = skills.filter(category=category)
    
    # Search in title and description
    search_query = request.GET.get('search')
    if search_query:
        skills = skills.filter(
            title__icontains=search_query
        ) | skills.filter(
            description__icontains=search_query
        )
    
    context = {
        'skills': skills,
        'search_query': search_query,
        'selected_category': category,
    }
    return render(request, 'skills/list.html', context)


def skill_detail(request, pk):
    """
    Display details of a single skill.
    Shows: title, description, price, availability, owner contact info,
    and all reviews with average rating.
    Anyone can view this page.
    
    pk = primary key (skill ID)
    """
    skill = get_object_or_404(Skill, pk=pk)
    
    # Get all reviews for this skill (ordered by newest first)
    reviews = skill.reviews.all()
    
    # Check if current user already has a review for this skill
    user_review = None
    review_form = None
    if request.user.is_authenticated:
        user_review = skill.reviews.filter(reviewer=request.user).first()
        # If they have a review, show the edit form, otherwise show create form
        if user_review:
            review_form = ReviewForm(instance=user_review)
        else:
            review_form = ReviewForm()
    else:
        # Not logged in users can only see reviews, not create them
        review_form = None
    
    context = {
        'skill': skill,
        'reviews': reviews,
        'user_review': user_review,
        'review_form': review_form,
        'average_rating': skill.get_average_rating(),
        'review_count': skill.get_review_count(),
    }
    return render(request, 'skills/detail.html', context)


# ==================== SKILL CREATION & EDITING ====================

@login_required(login_url='login')
def skill_create(request):
    """
    Create a new skill post.
    ONLY logged-in users can create skills.
    
    GET: Display empty form
    POST: Process form submission, save to database
    """
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            # Create skill but don't save yet
            skill = form.save(commit=False)
            # Set the owner to the current user
            skill.owner = request.user
            # Now save it
            skill.save()
            messages.success(request, 'Skill posted successfully!')
            return redirect('skill_detail', pk=skill.pk)
    else:
        form = SkillForm()
    
    context = {
        'form': form,
        'title': 'Post a New Skill'
    }
    return render(request, 'skills/form.html', context)


@login_required(login_url='login')
def skill_update(request, pk):
    """
    Edit an existing skill post.
    ONLY the skill's owner can edit it.
    
    pk = skill ID
    """
    skill = get_object_or_404(Skill, pk=pk)
    
    # Check: is the current user the owner?
    if skill.owner != request.user:
        messages.error(request, 'You can only edit your own skills.')
        return HttpResponseForbidden('You do not have permission to edit this skill.')
    
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill updated successfully!')
            return redirect('skill_detail', pk=skill.pk)
    else:
        form = SkillForm(instance=skill)
    
    context = {
        'form': form,
        'skill': skill,
        'title': f'Edit: {skill.title}'
    }
    return render(request, 'skills/form.html', context)


@login_required(login_url='login')
def skill_delete(request, pk):
    """
    Delete a skill post.
    ONLY the skill's owner can delete it.
    
    GET: Show confirmation page
    POST: Actually delete it
    """
    skill = get_object_or_404(Skill, pk=pk)
    
    # Check: is the current user the owner?
    if skill.owner != request.user:
        messages.error(request, 'You can only delete your own skills.')
        return HttpResponseForbidden('You do not have permission to delete this skill.')
    
    if request.method == 'POST':
        skill_title = skill.title
        skill.delete()
        messages.success(request, f'Skill "{skill_title}" deleted.')
        return redirect('dashboard')
    
    context = {
        'skill': skill,
    }
    return render(request, 'skills/delete.html', context)


# ==================== USER DASHBOARD ====================

@login_required(login_url='login')
def dashboard(request):
    """
    User dashboard - shows only THEIR own skills.
    This is where users manage their posted skills.
    """
    user_skills = request.user.skills.all()
    context = {
        'skills': user_skills,
        'skill_count': user_skills.count(),
    }
    return render(request, 'skills/dashboard.html', context)


# ==================== AUTHENTICATION VIEWS ====================

def register(request):
    """
    User registration page.
    Allows new users to create an account.
    After registration, automatically logs them in.
    
    GET: Show registration form
    POST: Process form, create user account
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Create the user account
            user = form.save()
            # Automatically log them in
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Account created successfully.')
            return redirect('home')
        else:
            # Show form errors (password mismatch, email exists, etc.)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'title': 'Create an Account'
    }
    return render(request, 'auth/register.html', context)


def login_view(request):
    """
    User login page.
    Users enter username and password.
    
    GET: Show login form
    POST: Authenticate and log in
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try to authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login successful
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Redirect to dashboard or home
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
        else:
            # Login failed
            messages.error(request, 'Invalid username or password.')
    
    context = {
        'title': 'Log In'
    }
    return render(request, 'auth/login.html', context)


def logout_view(request):
    """
    Log out the current user.
    Clears their session.
    """
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


# ==================== REVIEW VIEWS ====================

@login_required(login_url='login')
def create_review(request, pk):
    """
    Create a new review for a skill.
    Users can only create ONE review per skill.
    If they already have a review, they're redirected to the edit view.
    
    ONLY authenticated users can review skills.
    pk = skill ID
    """
    skill = get_object_or_404(Skill, pk=pk)
    
    # Check: does this user already have a review for this skill?
    existing_review = skill.reviews.filter(reviewer=request.user).first()
    if existing_review:
        messages.info(request, 'You already reviewed this skill. Edit your review instead.')
        return redirect('edit_review', skill_id=skill.pk, review_id=existing_review.pk)
    
    # Check: is user trying to review their own skill?
    if skill.owner == request.user:
        messages.error(request, 'You cannot review your own skill.')
        return HttpResponseForbidden('You cannot review your own skill.')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.skill = skill
            review.reviewer = request.user
            review.save()
            messages.success(request, f'Thank you! Your review of "{skill.title}" has been posted.')
            return redirect('skill_detail', pk=skill.pk)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'skill': skill,
    }
    return render(request, 'reviews/create.html', context)


@login_required(login_url='login')
def edit_review(request, skill_id, review_id):
    """
    Edit an existing review.
    Users can only edit their OWN reviews.
    
    skill_id = skill ID
    review_id = review ID
    """
    skill = get_object_or_404(Skill, pk=skill_id)
    review = get_object_or_404(Review, pk=review_id, skill=skill)
    
    # Check: is current user the one who left this review?
    if review.reviewer != request.user:
        messages.error(request, 'You can only edit your own reviews.')
        return HttpResponseForbidden('You do not have permission to edit this review.')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your review has been updated.')
            return redirect('skill_detail', pk=skill.pk)
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'form': form,
        'skill': skill,
        'review': review,
        'is_edit': True,
    }
    return render(request, 'reviews/create.html', context)


@login_required(login_url='login')
def delete_review(request, skill_id, review_id):
    """
    Delete a review.
    Users can only delete their OWN reviews.
    
    GET: Show confirmation page
    POST: Actually delete it
    
    skill_id = skill ID
    review_id = review ID
    """
    skill = get_object_or_404(Skill, pk=skill_id)
    review = get_object_or_404(Review, pk=review_id, skill=skill)
    
    # Check: is current user the one who left this review?
    if review.reviewer != request.user:
        messages.error(request, 'You can only delete your own reviews.')
        return HttpResponseForbidden('You do not have permission to delete this review.')
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Your review has been deleted.')
        return redirect('skill_detail', pk=skill.pk)
    
    context = {
        'skill': skill,
        'review': review,
    }
    return render(request, 'reviews/delete.html', context)


# ==================== MESSAGING VIEWS ====================

@login_required(login_url='login')
def send_message(request, recipient_id, skill_id=None):
    """
    Send a message to another user (usually the skill owner).
    ONLY authenticated users can send messages.
    
    recipient_id = user ID of the message recipient
    skill_id = skill ID (optional context for the message)
    """
    recipient = get_object_or_404(User, pk=recipient_id)
    skill = None
    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    
    # Check: user cannot message themselves
    if request.user == recipient:
        messages.error(request, 'You cannot message yourself.')
        return HttpResponseForbidden('You cannot message yourself.')
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            if skill_id:
                message.skill_id = skill_id
            message.save()
            messages.success(request, f'Message sent to {recipient.username}!')
            return redirect('inbox')
    else:
        form = MessageForm()
    
    context = {
        'form': form,
        'recipient': recipient,
        'skill': skill,
    }
    return render(request, 'messages/send.html', context)


@login_required(login_url='login')
def inbox(request):
    """
    Display user's message inbox.
    Shows all conversations with unread message count.
    """
    # Get all messages where current user is the recipient
    received_messages = request.user.received_messages.all()
    
    # Get all messages where current user is the sender
    sent_messages = request.user.sent_messages.all()
    
    # Combine and get unique conversation partners
    # This gets unique users that have messaged this user
    conversations = []
    conversation_dict = {}
    
    # Add received messages (messages FROM other users)
    for msg in received_messages:
        if msg.sender.id not in conversation_dict:
            conversation_dict[msg.sender.id] = {
                'user': msg.sender,
                'last_message': msg,
                'unread_count': received_messages.filter(sender=msg.sender, is_read=False).count(),
                'with_skill': msg.skill
            }
    
    # Add sent messages (messages TO other users)
    for msg in sent_messages:
        if msg.recipient.id not in conversation_dict:
            conversation_dict[msg.recipient.id] = {
                'user': msg.recipient,
                'last_message': msg,
                'unread_count': 0,
                'with_skill': msg.skill
            }
    
    # Sort by most recent message
    conversations = sorted(conversation_dict.values(), key=lambda x: x['last_message'].created_at, reverse=True)
    
    # Count total unread messages
    total_unread = received_messages.filter(is_read=False).count()
    
    context = {
        'conversations': conversations,
        'total_unread': total_unread,
    }
    return render(request, 'messages/inbox.html', context)


@login_required(login_url='login')
def view_conversation(request, other_user_id):
    """
    Display entire conversation thread with another user.
    Marks all received messages as read.
    
    other_user_id = ID of the other user in the conversation
    """
    other_user = get_object_or_404(User, pk=other_user_id)
    
    # Get all messages in this conversation (both directions)
    messages_in_conversation = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).order_by('created_at')
    
    # Mark all received messages from this user as read
    received_unread = Message.objects.filter(
        sender=other_user,
        recipient=request.user,
        is_read=False
    )
    for msg in received_unread:
        msg.mark_as_read()
    
    context = {
        'other_user': other_user,
        'messages': messages_in_conversation,
    }
    return render(request, 'messages/conversation.html', context)


@login_required(login_url='login')
def reply_message(request, other_user_id):
    """
    Send a reply message in an existing conversation.
    
    other_user_id = ID of the user to reply to
    """
    other_user = get_object_or_404(User, pk=other_user_id)
    
    # Check: user cannot message themselves
    if request.user == other_user:
        messages.error(request, 'You cannot message yourself.')
        return HttpResponseForbidden('You cannot message yourself.')
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = other_user
            message.save()
            messages.success(request, 'Reply sent!')
            return redirect('view_conversation', other_user_id=other_user.pk)
    else:
        form = MessageForm()
    
    context = {
        'form': form,
        'other_user': other_user,
        'is_reply': True,
    }
    return render(request, 'messages/send.html', context)


@login_required(login_url='login')
def delete_message(request, message_id):
    """
    Delete a message.
    Users can only delete their OWN messages (sender only).
    
    message_id = ID of the message to delete
    """
    message = get_object_or_404(Message, pk=message_id)
    other_user_id = message.recipient.id if message.sender == request.user else message.sender.id
    
    # Check: only message sender can delete
    if message.sender != request.user:
        messages.error(request, 'You can only delete your own messages.')
        return HttpResponseForbidden('You do not have permission to delete this message.')
    
    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Message deleted.')
        return redirect('view_conversation', other_user_id=other_user_id)
    
    context = {
        'message': message,
    }
    return render(request, 'messages/delete.html', context)
