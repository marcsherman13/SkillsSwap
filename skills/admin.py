from django.contrib import admin
from .models import Skill, Review, Message


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """
    Customize how Skills appear in Django Admin.
    Allows administrators to manage skills from /admin/
    """
    
    # Columns shown in the list view
    list_display = (
        'title',
        'owner',
        'category',
        'price_type',
        'availability',
        'created_at'
    )
    
    # Add filters on the right side
    list_filter = ('category', 'price_type', 'availability', 'created_at')
    
    # Add search box at the top
    search_fields = ('title', 'description', 'owner__username')
    
    # Fields that are read-only (auto-set)
    readonly_fields = ('created_at', 'updated_at')
    
    # Organize form fields when editing
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'owner', 'category')
        }),
        ('Pricing', {
            'fields': ('price_type', 'price')
        }),
        ('Availability & Contact', {
            'fields': ('availability', 'contact_preference')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Hidden by default
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Called when a skill is saved.
        If creating new skill and no owner set, set it to current admin user.
        """
        if not change:  # If creating new object
            obj.owner = request.user
        super().save_model(request, obj, form, change)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Customize how Reviews appear in Django Admin.
    Allows administrators to manage and moderate reviews.
    """
    
    # Columns shown in the list view
    list_display = (
        'reviewer',
        'skill',
        'rating',
        'created_at'
    )
    
    # Add filters on the right side
    list_filter = ('rating', 'created_at', 'skill__category')
    
    # Add search box at the top
    search_fields = ('reviewer__username', 'skill__title', 'review_text')
    
    # Fields that are read-only (auto-set)
    readonly_fields = ('created_at', 'updated_at', 'reviewer')
    
    # Organize form fields when editing
    fieldsets = (
        ('Review Information', {
            'fields': ('skill', 'reviewer', 'rating', 'review_text')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Hidden by default
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Called when a review is saved.
        If creating new review and no reviewer set, set it to current admin user.
        """
        if not change:  # If creating new object
            obj.reviewer = request.user
        super().save_model(request, obj, form, change)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Customize how Messages appear in Django Admin.
    Allows administrators to view and manage user messages.
    """
    
    # Columns shown in the list view
    list_display = (
        'sender',
        'recipient',
        'subject',
        'is_read',
        'created_at'
    )
    
    # Add filters on the right side
    list_filter = ('is_read', 'created_at', 'skill')
    
    # Add search box at the top
    search_fields = ('sender__username', 'recipient__username', 'subject', 'body')
    
    # Fields that are read-only (auto-set)
    readonly_fields = ('created_at', 'updated_at', 'sender')
    
    # Organize form fields when editing
    fieldsets = (
        ('Message Information', {
            'fields': ('sender', 'recipient', 'subject', 'body', 'skill')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Called when a message is saved.
        If creating new message and no sender set, set it to current admin user.
        """
        if not change:  # If creating new object
            obj.sender = request.user
        super().save_model(request, obj, form, change)
