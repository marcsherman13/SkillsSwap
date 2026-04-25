from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
import os


@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    """
    Create a superuser automatically after migrations run.
    Uses environment variables: ADMIN_USERNAME and ADMIN_PASSWORD
    """
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'batman1815')
    admin_email = 'admin@skillswap.local'
    
    # Check if superuser already exists
    if not User.objects.filter(username=admin_username, is_superuser=True).exists():
        User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password
        )
        print(f"✅ Superuser '{admin_username}' created successfully!")
    else:
        print(f"✅ Superuser '{admin_username}' already exists.")
