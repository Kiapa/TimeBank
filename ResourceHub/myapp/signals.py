from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.contrib.auth.models import User
from .models import Transaction, Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile for every new User"""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Ensure profile is saved when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

@receiver(post_save, sender=Transaction)
def update_user_balances(sender, instance, created, **kwargs):
    """
    Updates the Profile balance when a new Transaction is recorded.
    Wrapped in atomic transaction to ensure data integrity.
    """
    if created:
        with transaction.atomic():
            # Deduct from Sender
            sender_profile = instance.sender.profile
            sender_profile.time_credits -= instance.amount
            sender_profile.save()

            # Add to Receiver
            receiver_profile = instance.receiver.profile
            receiver_profile.time_credits += instance.amount
            receiver_profile.save()